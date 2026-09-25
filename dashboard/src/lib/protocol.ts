/**
 * Wire protocol definitions shared by all Pi processes.
 *
 * Mirrors pi/common/protocol.py. Changing a constant there means changing it
 * here too — see that file's docstring for the section references.
 */

// --- Cadences ----------------------------------------------------------

export const TELEMETRY_PERIOD_MS = 200;
export const HEARTBEAT_PERIOD_MS = 500;
export const COMMAND_ACK_TIMEOUT_MS = 3000;

// --- Network -------------------------------------------------------------

export const P1_PORT = 8080;
export const P2_PORT = 8443;
export const WS_PATH = '/control/ws';
export const WEBRTC_OFFER_PATH = '/webrtc/offer';

// --- Motor / servo limits --------------------------------------------------

export const MIN_PWM = 0;
export const MAX_PWM = 180;
export const SERVO_MIN_ANGLE = 0;
export const SERVO_MAX_ANGLE = 180;

// Dashboard direction tokens, routed through DIRECTION_TO_OPCODE on the
// server; the dashboard already speaks the wire letters directly.
export type Direction = 'F' | 'R' | 'L' | 'G';
export type ServoAxis = 'pan' | 'tilt';

// --- WebSocket message types ------------------------------------------------

export const MSG_MOTOR = 'motor';
export const MSG_SERVO = 'servo';
export const MSG_HEARTBEAT = 'heartbeat';
export const MSG_STOP_ALL = 'stop_all';
export const MSG_HELLO = 'hello';
export const MSG_RESUME_FROM = 'resume_from';

export const MSG_TELEMETRY = 'telemetry';
export const MSG_RECOVERY_BATCH = 'recovery_batch';
export const MSG_ACK = 'ack';
export const MSG_ERROR = 'error';

export const ROLE_CONTROLLER = 'controller';
export const ROLE_OBSERVER = 'observer';
export type Role = typeof ROLE_CONTROLLER | typeof ROLE_OBSERVER;

// --- Firmware / mission state ------------------------------------------------

export const FW_STATE_ARMED = 1;
export const FW_STATE_DRIVING = 2;
export const FW_STATE_STOPPED = 3;

export const MISSION_STOP = 'STOP';
export const MISSION_DRIVING_LIMITED = 'DRIVING_LIMITED';
export const MISSION_READY = 'READY';
export const MISSION_DRIVING = 'DRIVING';
export type MissionState =
  | typeof MISSION_STOP
  | typeof MISSION_DRIVING_LIMITED
  | typeof MISSION_READY
  | typeof MISSION_DRIVING;

/** Mission state per Section 8.11.1.1. First matching rule wins. */
export function deriveMissionState(params: {
  wsConnected: boolean;
  serialOk: boolean;
  videoActive: boolean;
  meshOk: boolean;
  lastCmdAckMs: number;
  commandActive: boolean;
}): MissionState {
  const { wsConnected, serialOk, videoActive, meshOk, lastCmdAckMs, commandActive } = params;
  if (!wsConnected || !serialOk || lastCmdAckMs > COMMAND_ACK_TIMEOUT_MS) {
    return MISSION_STOP;
  }
  if (!videoActive || !meshOk) {
    return MISSION_DRIVING_LIMITED;
  }
  return commandActive ? MISSION_DRIVING : MISSION_READY;
}

// --- Telemetry snapshot, Section 8.10.1.2 -----------------------------------

export interface TelemetrySnapshot {
  type: typeof MSG_TELEMETRY;
  seq: number;
  server_ts: number;

  temperature_c: number;
  humidity_pct: number;
  gas_ppm: number;
  motion: number;
  range_cm: number;
  pan_angle: number;
  tilt_angle: number;
  fw_state: number;
  uptime_ms: number;

  lat: number | null;
  lon: number | null;
  gps_fix: boolean;
  gps_sats: number;
  turn_status: string;
  serial_ok: boolean;
  ws_clients: number;
}

export interface RecoveryBatchMessage {
  type: typeof MSG_RECOVERY_BATCH;
  entries: TelemetrySnapshot[];
  gap_ms: number;
}

export interface AckMessage {
  type: typeof MSG_ACK;
  of: string;
  role?: Role;
  session?: string;
}

export interface ErrorMessage {
  type: typeof MSG_ERROR;
  code: string;
  message: string;
}

export type ServerMessage = TelemetrySnapshot | RecoveryBatchMessage | AckMessage | ErrorMessage;

// --- Client -> server messages -----------------------------------------------

export interface HelloMessage {
  type: typeof MSG_HELLO;
  role: Role;
}

export interface MotorMessage {
  type: typeof MSG_MOTOR;
  dir: Direction;
  speed: number;
  seq: number;
}

export interface ServoMessage {
  type: typeof MSG_SERVO;
  axis: ServoAxis;
  angle: number;
  seq: number;
}

export interface HeartbeatMessage {
  type: typeof MSG_HEARTBEAT;
}

export interface StopAllMessage {
  type: typeof MSG_STOP_ALL;
}

export interface ResumeFromMessage {
  type: typeof MSG_RESUME_FROM;
  last_ts: number;
}

export type ClientMessage =
  | HelloMessage
  | MotorMessage
  | ServoMessage
  | HeartbeatMessage
  | StopAllMessage
  | ResumeFromMessage;

// --- Alert thresholds (defaults; overridden by /api/session) -----------------

export interface ThresholdLimits {
  warn?: number;
  crit?: number;
  direction: 'above' | 'below';
}

export const DEFAULT_THRESHOLDS: Record<string, ThresholdLimits> = {
  temperature_c: { warn: 50.0, crit: 70.0, direction: 'above' },
  // gas_ppm actually carries the MQ-136's raw ADC count (0-1023), not a
  // calibrated ppm value -- no calibration curve exists for this sensor yet.
  // Scaled to line up with the firmware's own alarm point, GAS_ALARM_THRESHOLD
  // in arduino/config.h.
  gas_ppm: { warn: 450.0, crit: 600.0, direction: 'above' },
  range_cm: { warn: 30.0, crit: 20.0, direction: 'below' },
};

export function isAlertActive(
  value: number,
  limits: ThresholdLimits | undefined,
  level: 'warn' | 'crit',
): boolean {
  if (!limits || limits[level] === undefined) return false;
  const threshold = limits[level] as number;
  return limits.direction === 'above' ? value >= threshold : value <= threshold;
}
