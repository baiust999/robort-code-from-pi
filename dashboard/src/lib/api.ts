/** REST client for P1's control-server endpoints, Section 8.8.1.1. */

const ROBOT_HOST = import.meta.env.VITE_ROBOT_HOST ?? window.location.hostname ?? 'localhost';
const P1_PORT = import.meta.env.VITE_P1_PORT ?? '8080';
const P2_PORT = import.meta.env.VITE_P2_PORT ?? '8443';

export const P1_HTTP_BASE = `http://${ROBOT_HOST}:${P1_PORT}`;
export const P2_HTTP_BASE = `http://${ROBOT_HOST}:${P2_PORT}`;
export const P1_WS_URL = `ws://${ROBOT_HOST}:${P1_PORT}/control/ws`;

export interface HealthResponse {
  serial_connected: boolean;
  ws_clients: number;
  gps_fix: boolean;
  uptime_s: number;
}

export interface IceConfigResponse {
  stun: string;
  iceServers: { urls: string }[];
  policy: string;
  turn: unknown | null;
}

export interface SessionResponse {
  session_id: string;
  mock_hardware: boolean;
  thresholds: Record<string, { warn?: number; crit?: number; direction: 'above' | 'below' }>;
  telemetry_period_ms: number;
  heartbeat_period_ms: number;
}

export interface GpsTrackResponse {
  type: 'LineString';
  coordinates: [number, number][];
}

async function getJson<T>(url: string): Promise<T> {
  const resp = await fetch(url);
  if (!resp.ok) throw new Error(`${url} -> ${resp.status}`);
  return (await resp.json()) as T;
}

export const fetchHealth = () => getJson<HealthResponse>(`${P1_HTTP_BASE}/health`);
export const fetchIceConfig = () => getJson<IceConfigResponse>(`${P1_HTTP_BASE}/api/ice-config`);
export const fetchSession = () => getJson<SessionResponse>(`${P1_HTTP_BASE}/api/session`);
export const fetchGpsTrack = () => getJson<GpsTrackResponse>(`${P1_HTTP_BASE}/api/gps-track`);

export async function fetchMediaHealth(): Promise<{
  status: string;
  camera_open: boolean;
  active_streams: number;
  mock_hardware: boolean;
}> {
  return getJson(`${P2_HTTP_BASE}/health`);
}

export async function negotiateWebrtc(offer: RTCSessionDescriptionInit): Promise<RTCSessionDescriptionInit> {
  const resp = await fetch(`${P2_HTTP_BASE}/webrtc/offer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ sdp: offer.sdp, type: offer.type }),
  });
  if (!resp.ok) throw new Error(`webrtc offer failed: ${resp.status}`);
  return (await resp.json()) as RTCSessionDescriptionInit;
}
