import type { MissionState } from '../lib/protocol';

const DESCRIPTIONS: Record<MissionState, string> = {
  STOP: 'Link or hardware fault — motion disabled',
  DRIVING_LIMITED: 'Video or mesh degraded — drive with caution',
  READY: 'All systems nominal — awaiting command',
  DRIVING: 'Actively driving',
};

export function MissionStateIndicator(props: { state: MissionState }) {
  return (
    <div className="rounded-lg border border-white/10 p-3">
      <div className="text-xs uppercase tracking-wide text-white/40">Mission State</div>
      <div className="text-2xl font-bold">{props.state}</div>
      <div className="text-xs text-white/50">{DESCRIPTIONS[props.state]}</div>
    </div>
  );
}
