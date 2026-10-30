import { useCallback, useEffect, useRef, useState } from 'react';
import { fetchVictims, P1_WS_URL } from '../lib/api';
import {
  MSG_HELLO,
  MSG_HEARTBEAT,
  MSG_RESUME_FROM,
  MSG_TELEMETRY,
  MSG_RECOVERY_BATCH,
  MSG_ACK,
  MSG_ERROR,
  MSG_ROLE,
  MSG_VICTIM_MARK,
  MSG_VICTIM_DELETE,
  ROLE_CONTROLLER,
  ROLE_OBSERVER,
  HEARTBEAT_PERIOD_MS,
  type Auth,
  type ClientMessage,
  type TelemetrySnapshot,
  type Role,
  type VictimMark,
} from '../lib/protocol';
import { nextSignalLevel, SIGNAL_STALE_MS, type SignalLevel } from '../lib/signal';

const RECONNECT_MIN_MS = 1000;
const RECONNECT_MAX_MS = 30000;
const SIGNAL_CHECK_MS = 250;

export interface AlertLogEntry {
  id: number;
  ts: number;
  message: string;
}

export interface ControlSocketState {
  connected: boolean;
  role: Role | null;
  /** Result of the last controller-key check. */
  auth: Auth | null;
  /** Seconds left on a lockout, when auth is 'locked'. */
  retryAfterS: number | null;
  telemetry: TelemetrySnapshot | null;
  /** No live telemetry: socket closed or no frame for SIGNAL_STALE_MS. */
  telemetryStale: boolean;
  /** Wi-Fi warning level; 'none' whenever telemetryStale or signal_dbm is null. */
  signalLevel: SignalLevel;
  lastAckMs: number;
  alerts: AlertLogEntry[];
  pushAlert: (message: string) => void;
  /** Every victim mark on the robot, oldest first. */
  victimMarks: VictimMark[];
  /** Adds a mark this dashboard just saved, ahead of P1's broadcast. */
  addVictimMark: (mark: VictimMark) => void;
  /** Removes a mark this dashboard just deleted, ahead of P1's broadcast. */
  removeVictimMark: (id: string) => void;
  sendMotor: (dir: 'F' | 'R' | 'L' | 'G', speed: number) => void;
  sendServo: (axis: 'pan' | 'tilt', angle: number) => void;
  sendStopAll: () => void;
}

/**
 * Owns the P1 control WebSocket: connect, heartbeat, exponential-backoff
 * reconnect, and resume_from replay on reconnect (Section 8.10.1, 8.15.4).
 *
 * The hello carries `controllerKey`; P1 makes this dashboard controller only
 * if it is right. A changed key is re-sent as a fresh hello on the open socket.
 */
export function useControlSocket(controllerKey: string | null): ControlSocketState {
  const [connected, setConnected] = useState(false);
  const [role, setRole] = useState<Role | null>(null);
  const [auth, setAuth] = useState<Auth | null>(null);
  const [retryAfterS, setRetryAfterS] = useState<number | null>(null);
  const [telemetry, setTelemetry] = useState<TelemetrySnapshot | null>(null);
  const [lastAckMs, setLastAckMs] = useState(0);
  const [alerts, setAlerts] = useState<AlertLogEntry[]>([]);
  const [telemetryStale, setTelemetryStale] = useState(true);
  const [signalLevel, setSignalLevel] = useState<SignalLevel>('none');
  const [victimMarks, setVictimMarks] = useState<VictimMark[]>([]);

  const socketRef = useRef<WebSocket | null>(null);
  const seqRef = useRef(0);
  const lastServerTsRef = useRef(0);
  const backoffRef = useRef(RECONNECT_MIN_MS);
  const heartbeatTimerRef = useRef<number | null>(null);
  const reconnectTimerRef = useRef<number | null>(null);
  const alertIdRef = useRef(0);
  const keyRef = useRef(controllerKey);
  const roleRef = useRef<Role | null>(null);
  const mountedRef = useRef(true);
  // Live frames only; 0 means none since the socket last opened.
  const lastTelemetryAtRef = useRef(0);
  const signalDbmRef = useRef<number | null>(null);
  const signalLevelRef = useRef<SignalLevel | null>(null);

  const pushAlert = useCallback((message: string) => {
    alertIdRef.current += 1;
    setAlerts((prev) => [...prev.slice(-49), { id: alertIdRef.current, ts: Date.now(), message }]);
  }, []);

  const addVictimMark = useCallback((mark: VictimMark) => {
    setVictimMarks((prev) => (prev.some((m) => m.id === mark.id) ? prev : [...prev, mark]));
  }, []);

  const removeVictimMark = useCallback((id: string) => {
    setVictimMarks((prev) => prev.filter((m) => m.id !== id));
  }, []);

  const send = useCallback((message: ClientMessage) => {
    const socket = socketRef.current;
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(message));
    }
  }, []);

  const connect = useCallback(() => {
    if (!mountedRef.current) return;
    // A prior socket (e.g. from a StrictMode double-invoke) may still be
    // connecting when this runs; abandoning it without closing would leave
    // it to open later, claim the controller slot, and strand this hook on
    // an observer-only connection.
    socketRef.current?.close();

    const socket = new WebSocket(P1_WS_URL);
    socketRef.current = socket;
    const isCurrent = () => socketRef.current === socket;

    socket.onopen = () => {
      if (!isCurrent() || !mountedRef.current) {
        socket.close();
        return;
      }
      backoffRef.current = RECONNECT_MIN_MS;
      setConnected(true);
      socket.send(JSON.stringify(helloMessage(keyRef.current)));
      if (lastServerTsRef.current > 0) {
        socket.send(JSON.stringify({ type: MSG_RESUME_FROM, last_ts: lastServerTsRef.current }));
      }
      pushAlert('connected to control server');
      // Marks saved while this dashboard was away arrive with the full list.
      fetchVictims()
        .then(({ marks }) => {
          if (isCurrent()) setVictimMarks(marks);
        })
        .catch(() => pushAlert('could not load victim marks'));
    };

    socket.onclose = () => {
      if (!isCurrent() || !mountedRef.current) return;
      setConnected(false);
      lastTelemetryAtRef.current = 0;
      setRole(null);
      roleRef.current = null;
      pushAlert('disconnected; reconnecting…');
      scheduleReconnect();
    };

    socket.onerror = () => {
      socket.close();
    };

    socket.onmessage = (event) => {
      if (!isCurrent()) return;
      let msg: Record<string, unknown>;
      try {
        msg = JSON.parse(event.data as string);
      } catch {
        return;
      }
      switch (msg.type) {
        case MSG_TELEMETRY: {
          const frame = msg as unknown as TelemetrySnapshot;
          lastServerTsRef.current = frame.server_ts;
          lastTelemetryAtRef.current = Date.now();
          signalDbmRef.current = frame.signal_dbm ?? null;
          setTelemetry(frame);
          setLastAckMs(0);
          break;
        }
        case MSG_RECOVERY_BATCH: {
          const entries = (msg.entries as TelemetrySnapshot[]) ?? [];
          if (entries.length > 0) {
            lastServerTsRef.current = entries[entries.length - 1].server_ts;
            setTelemetry(entries[entries.length - 1]);
            pushAlert(`recovered ${entries.length} buffered telemetry frames`);
          }
          break;
        }
        case MSG_ACK: {
          if (msg.of === 'hello' && typeof msg.role === 'string') {
            roleRef.current = msg.role as Role;
            setRole(msg.role as Role);
            setAuth((msg.auth as Auth) ?? null);
            setRetryAfterS(typeof msg.retry_after_s === 'number' ? msg.retry_after_s : null);
          }
          break;
        }
        case MSG_ROLE: {
          if (typeof msg.role === 'string') {
            roleRef.current = msg.role as Role;
            setRole(msg.role as Role);
            if (msg.role === ROLE_OBSERVER && msg.reason === 'taken_over') {
              pushAlert('another dashboard took control; you are now an observer');
            }
          }
          break;
        }
        case MSG_VICTIM_MARK: {
          const mark = msg.mark as VictimMark | undefined;
          if (mark?.id) {
            addVictimMark(mark);
            pushAlert(`victim marked${mark.note ? `: ${mark.note}` : ''}`);
          }
          break;
        }
        case MSG_VICTIM_DELETE: {
          const id = msg.id as string | undefined;
          if (id) {
            removeVictimMark(id);
            pushAlert('victim mark deleted');
          }
          break;
        }
        case MSG_ERROR: {
          pushAlert(`error: ${msg.message ?? msg.code ?? 'unknown'}`);
          break;
        }
        default:
          break;
      }
    };
  }, [pushAlert, addVictimMark, removeVictimMark]);

  const scheduleReconnect = useCallback(() => {
    if (reconnectTimerRef.current !== null) return;
    reconnectTimerRef.current = window.setTimeout(() => {
      reconnectTimerRef.current = null;
      backoffRef.current = Math.min(backoffRef.current * 2, RECONNECT_MAX_MS);
      connect();
    }, backoffRef.current);
  }, [connect]);

  useEffect(() => {
    mountedRef.current = true;
    connect();
    return () => {
      mountedRef.current = false;
      if (reconnectTimerRef.current !== null) window.clearTimeout(reconnectTimerRef.current);
      if (heartbeatTimerRef.current !== null) window.clearInterval(heartbeatTimerRef.current);
      socketRef.current?.close();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // A changed key takes effect on the open socket; on a closed one the next
  // connect sends it anyway.
  useEffect(() => {
    if (keyRef.current === controllerKey) return;
    keyRef.current = controllerKey;
    send(helloMessage(controllerKey));
  }, [controllerKey, send]);

  // Idle heartbeat: keeps the dead-man armed when the operator isn't driving.
  // Only the controller's count, so observers don't send them.
  useEffect(() => {
    heartbeatTimerRef.current = window.setInterval(() => {
      if (roleRef.current !== ROLE_CONTROLLER) return;
      send({ type: MSG_HEARTBEAT });
      setLastAckMs((v) => v + HEARTBEAT_PERIOD_MS);
    }, HEARTBEAT_PERIOD_MS);
    return () => {
      if (heartbeatTimerRef.current !== null) window.clearInterval(heartbeatTimerRef.current);
    };
  }, [send]);

  // The link is judged here, not by P1: when it drops, P1's last good
  // signal_dbm is exactly what must not stay on screen. Recovery batches are
  // old frames and don't count as live.
  useEffect(() => {
    const timer = window.setInterval(() => {
      const last = lastTelemetryAtRef.current;
      const stale = last === 0 || Date.now() - last > SIGNAL_STALE_MS;
      setTelemetryStale(stale);

      const dbm = stale ? null : signalDbmRef.current;
      const prev = signalLevelRef.current;
      const level = nextSignalLevel(prev, dbm);
      // Before the first reading arrives there is nothing to report yet; the
      // initial state already shows NO SIGNAL.
      if (level === prev || (prev === null && level === 'none')) return;
      signalLevelRef.current = level;
      setSignalLevel(level);
      // The first reading after load is not news unless it is already bad.
      if (prev === null && level === 'ok') return;
      pushAlert(signalAlert(level, dbm));
    }, SIGNAL_CHECK_MS);
    return () => window.clearInterval(timer);
  }, [pushAlert]);

  const sendMotor = useCallback(
    (dir: 'F' | 'R' | 'L' | 'G', speed: number) => {
      seqRef.current += 1;
      send({ type: 'motor', dir, speed, seq: seqRef.current });
    },
    [send],
  );

  const sendServo = useCallback(
    (axis: 'pan' | 'tilt', angle: number) => {
      seqRef.current += 1;
      send({ type: 'servo', axis, angle, seq: seqRef.current });
    },
    [send],
  );

  const sendStopAll = useCallback(() => {
    send({ type: 'stop_all' });
  }, [send]);

  return {
    connected,
    role,
    auth,
    retryAfterS,
    telemetry,
    telemetryStale,
    signalLevel,
    lastAckMs,
    alerts,
    pushAlert,
    victimMarks,
    addVictimMark,
    removeVictimMark,
    sendMotor,
    sendServo,
    sendStopAll,
  };
}

function signalAlert(level: SignalLevel, dbm: number | null): string {
  switch (level) {
    case 'low':
      return `weak Wi-Fi signal (${dbm} dBm); turn back soon`;
    case 'critical':
      return `Wi-Fi signal critical (${dbm} dBm); bring the robot back`;
    case 'none':
      return 'NO SIGNAL: no live telemetry from the robot';
    default:
      return `Wi-Fi signal recovered (${dbm} dBm)`;
  }
}

function helloMessage(key: string | null): ClientMessage {
  return key ? { type: MSG_HELLO, role: ROLE_CONTROLLER, key } : { type: MSG_HELLO, role: ROLE_CONTROLLER };
}
