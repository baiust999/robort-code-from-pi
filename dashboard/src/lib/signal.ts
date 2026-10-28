/**
 * Wi-Fi signal indicator: dBm -> phone-style bars and percentage, plus the
 * warning level with hysteresis. Pure functions; useControlSocket owns the
 * timing (staleness) and the alert log.
 */

import { DEFAULT_THRESHOLDS } from './protocol';

/** No telemetry for this long and the reading is treated as gone (5 frames). */
export const SIGNAL_STALE_MS = 1000;

/** Leaving a worse level needs this much margin, so the warning doesn't flicker at the edge. */
export const SIGNAL_HYSTERESIS_DB = 3;

// Linear 0-100% span. -30 dBm is about as strong as Wi-Fi gets; by -90 the
// link is effectively unusable.
const PERCENT_FLOOR_DBM = -90;
const PERCENT_CEIL_DBM = -30;

// Weakest reading that still earns 4, 3, 2 and 1 bars.
const BAR_EDGES_DBM = [-60, -67, -75, -82] as const;

/** 'none' means there is no reading to trust: link down or telemetry stale. */
export type SignalLevel = 'ok' | 'low' | 'critical' | 'none';

export function signalPercent(dbm: number): number {
  const span = PERCENT_CEIL_DBM - PERCENT_FLOOR_DBM;
  const pct = ((dbm - PERCENT_FLOOR_DBM) / span) * 100;
  return Math.round(Math.min(100, Math.max(0, pct)));
}

export function signalBars(dbm: number): number {
  const index = BAR_EDGES_DBM.findIndex((edge) => dbm >= edge);
  return index === -1 ? 0 : BAR_EDGES_DBM.length - index;
}

/** Level for `dbm`, given the level shown before it. */
export function nextSignalLevel(prev: SignalLevel | null, dbm: number | null): SignalLevel {
  if (dbm === null) return 'none';
  const limits = DEFAULT_THRESHOLDS.signal_dbm;
  const warn = limits.warn ?? -70;
  const crit = limits.crit ?? -80;
  const wasCritical = prev === 'critical' || prev === 'none';
  const critEdge = wasCritical ? crit + SIGNAL_HYSTERESIS_DB : crit;
  const warnEdge = prev !== null && prev !== 'ok' ? warn + SIGNAL_HYSTERESIS_DB : warn;
  if (dbm <= critEdge) return 'critical';
  if (dbm <= warnEdge) return 'low';
  return 'ok';
}
