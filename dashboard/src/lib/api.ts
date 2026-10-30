/** REST client for P1's control-server endpoints, Section 8.8.1.1. */

import type { Auth, Role, VictimMark } from './protocol';

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

export const fetchVictims = () => getJson<{ marks: VictimMark[] }>(`${P1_HTTP_BASE}/api/victims`);

/** Only the controller key may mark; P1 stamps position and servo angles itself. The snapshot stays on this device. */
export async function postVictim(
  key: string | null,
  body: { note: string; ai_score: number | null },
): Promise<VictimMark> {
  const resp = await fetch(`${P1_HTTP_BASE}/api/victims`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-Controller-Key': key ?? '' },
    body: JSON.stringify(body),
  });
  if (!resp.ok) {
    const detail = await resp.json().then((j: { detail?: string }) => j.detail).catch(() => null);
    throw new Error(detail ?? `save failed: ${resp.status}`);
  }
  return (await resp.json()) as VictimMark;
}

/** Only the controller key may delete a mark, same as marking one. */
export async function deleteVictim(key: string | null, id: string): Promise<void> {
  const resp = await fetch(`${P1_HTTP_BASE}/api/victims/${encodeURIComponent(id)}`, {
    method: 'DELETE',
    headers: { 'X-Controller-Key': key ?? '' },
  });
  if (!resp.ok) {
    const detail = await resp.json().then((j: { detail?: string }) => j.detail).catch(() => null);
    throw new Error(detail ?? `delete failed: ${resp.status}`);
  }
}

/** Only the controller key may start a new mission. Archives every current mark under a dated filename on the robot (nothing is deleted) and clears the active list. */
export async function startNewMission(key: string | null): Promise<{ archive: string | null }> {
  const resp = await fetch(`${P1_HTTP_BASE}/api/victims/new-mission`, {
    method: 'POST',
    headers: { 'X-Controller-Key': key ?? '' },
  });
  if (!resp.ok) {
    const detail = await resp.json().then((j: { detail?: string }) => j.detail).catch(() => null);
    throw new Error(detail ?? `new mission failed: ${resp.status}`);
  }
  return (await resp.json()) as { archive: string | null };
}

export async function fetchMediaHealth(): Promise<{
  status: string;
  camera_open: boolean;
  active_streams: number;
  mock_hardware: boolean;
}> {
  return getJson(`${P2_HTTP_BASE}/health`);
}

export interface WebrtcAnswer extends RTCSessionDescriptionInit {
  role: Role;
  auth: Auth;
  retry_after_s: number | null;
}

/** Sends the controller key, if any; without the right one P2 makes the session view-only. */
export async function negotiateWebrtc(
  offer: RTCSessionDescriptionInit,
  key: string | null,
): Promise<WebrtcAnswer> {
  const resp = await fetch(`${P2_HTTP_BASE}/webrtc/offer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ sdp: offer.sdp, type: offer.type, key }),
  });
  if (!resp.ok) throw new Error(`webrtc offer failed: ${resp.status}`);
  return (await resp.json()) as WebrtcAnswer;
}
