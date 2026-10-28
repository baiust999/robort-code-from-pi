import type { SignalLevel } from '../lib/signal';

/** Full-width warning under the status bar while the Wi-Fi link is weak or gone. */
export function SignalWarningBanner(props: { level: SignalLevel; signalDbm: number | null }) {
  const { level, signalDbm } = props;
  if (level === 'ok') return null;
  if (level === 'low') {
    return (
      <div className="border-b border-amber-500/40 bg-amber-500/20 px-4 py-1.5 text-sm font-semibold text-amber-200">
        Weak signal ({signalDbm} dBm) — turn back soon
      </div>
    );
  }
  return (
    <div className="animate-pulse border-b border-red-500/50 bg-red-500/25 px-4 py-1.5 text-sm font-semibold text-red-200">
      {level === 'none'
        ? 'NO SIGNAL — no live telemetry from the robot'
        : `Signal critical (${signalDbm} dBm) — bring the robot back`}
    </div>
  );
}
