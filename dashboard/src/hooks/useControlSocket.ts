import { useCallback, useEffect, useRef, useState } from 'react';
import { P1_WS_URL } from '../lib/api';
import {
  MSG_HELLO,
  MSG_HEARTBEAT,
  MSG_RESUME_FROM,
  MSG_TELEMETRY,
  MSG_RECOVERY_BATCH,
  MSG_ACK,
  MSG_ERROR,
  ROLE_CONTROLLER,
  HEARTBEAT_PERIOD_MS,
  type ClientMessage,
  type TelemetrySnapshot,
  type Role,
} from '../lib/protocol';

const RECONNECT_MIN_MS = 1000;
const RECONNECT_MAX_MS = 30000;

export interface AlertLogEntry {
  id: number;
  ts: number;
  message: string;
}

export interface ControlSocketState {
  connected: boolean;
  role: Role | null;
  telemetry: TelemetrySnapshot | null;
  lastAckMs: number;
  alerts: AlertLogEntry[];
  sendMotor: (dir: 'F' | 'R' | 'L' | 'G', speed: number) => void;
  sendServo: (axis: 'pan' | 'tilt', angle: number) => void;
  sendStopAll: () => void;
}

/**
 * Owns the P1 control WebSocket: connect, heartbeat, exponential-backoff
 * reconnect, and resume_from replay on reconnect (Section 8.10.1, 8.15.4).
 */
export function useControlSocket(): ControlSocketState {
  const [connected, setConnected] = useState(false);
  const [role, setRole] = useState<Role | null>(null);
  const [telemetry, setTelemetry] = useState<TelemetrySnapshot | null>(null);
  const [lastAckMs, setLastAckMs] = useState(0);
  const [alerts, setAlerts] = useState<AlertLogEntry[]>([]);

  const socketRef = useRef<WebSocket | null>(null);
  const seqRef = useRef(0);
  const lastServerTsRef = useRef(0);
  const backoffRef = useRef(RECONNECT_MIN_MS);
  const heartbeatTimerRef = useRef<number | null>(null);
  const reconnectTimerRef = useRef<number | null>(null);
  const alertIdRef = useRef(0);
  const mountedRef = useRef(true);

  const pushAlert = useCallback((message: string) => {
    alertIdRef.current += 1;
    setAlerts((prev) => [...prev.slice(-49), { id: alertIdRef.current, ts: Date.now(), message }]);
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
      socket.send(JSON.stringify({ type: MSG_HELLO, role: ROLE_CONTROLLER }));
      if (lastServerTsRef.current > 0) {
        socket.send(JSON.stringify({ type: MSG_RESUME_FROM, last_ts: lastServerTsRef.current }));
      }
      pushAlert('connected to control server');
    };

    socket.onclose = () => {
      if (!isCurrent() || !mountedRef.current) return;
      setConnected(false);
      setRole(null);
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
            setRole(msg.role as Role);
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
  }, [pushAlert]);

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

  // Idle heartbeat: keeps the dead-man armed when the operator isn't driving.
  useEffect(() => {
    heartbeatTimerRef.current = window.setInterval(() => {
      send({ type: MSG_HEARTBEAT });
      setLastAckMs((v) => v + HEARTBEAT_PERIOD_MS);
    }, HEARTBEAT_PERIOD_MS);
    return () => {
      if (heartbeatTimerRef.current !== null) window.clearInterval(heartbeatTimerRef.current);
    };
  }, [send]);

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

  return { connected, role, telemetry, lastAckMs, alerts, sendMotor, sendServo, sendStopAll };
}
