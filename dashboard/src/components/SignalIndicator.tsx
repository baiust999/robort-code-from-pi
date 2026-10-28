import { signalBars, signalPercent, type SignalLevel } from '../lib/signal';

const LEVEL_COLOR: Record<SignalLevel, string> = {
  ok: 'bg-emerald-400',
  low: 'bg-amber-400',
  critical: 'bg-red-400',
  none: 'bg-white/20',
};

const LEVEL_TEXT: Record<SignalLevel, string> = {
  ok: 'text-emerald-300',
  low: 'text-amber-300',
  critical: 'text-red-300',
  none: 'text-red-300',
};

const BAR_HEIGHTS = ['h-1', 'h-2', 'h-3', 'h-4'];

/** Phone-style Wi-Fi bars and percentage for the robot's link. */
export function SignalIndicator(props: { signalDbm: number | null; level: SignalLevel }) {
  const { level } = props;
  // Never draw a value the level says can't be trusted.
  const dbm = level === 'none' ? null : props.signalDbm;
  const bars = dbm === null ? 0 : signalBars(dbm);
  return (
    <span
      className={`flex items-center gap-1.5 font-medium ${LEVEL_TEXT[level]}`}
      title={dbm === null ? 'no live signal reading from the robot' : `Wi-Fi ${dbm} dBm`}
    >
      <span className="flex items-end gap-0.5" aria-hidden>
        {BAR_HEIGHTS.map((height, i) => (
          <span
            key={height}
            className={`w-1 rounded-sm ${height} ${i < bars ? LEVEL_COLOR[level] : 'bg-white/15'}`}
          />
        ))}
      </span>
      {dbm === null ? 'NO SIGNAL' : `${signalPercent(dbm)}%`}
    </span>
  );
}
