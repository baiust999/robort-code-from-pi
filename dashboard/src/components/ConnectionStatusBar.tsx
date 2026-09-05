import type { MissionState } from '../lib/protocol';

const MISSION_STYLES: Record<MissionState, string> = {
  STOP: 'bg-red-500/20 text-red-300 border-red-500/40',
  DRIVING_LIMITED: 'bg-amber-500/20 text-amber-300 border-amber-500/40',
  READY: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40',
  DRIVING: 'bg-sky-500/20 text-sky-300 border-sky-500/40',
};

export function ConnectionStatusBar(props: {
  connected: boolean;
  role: string | null;
  missionState: MissionState;
  serialOk: boolean;
  gpsFix: boolean;
}) {
  const { connected, role, missionState, serialOk, gpsFix } = props;
  return (
    <div className="flex items-center gap-3 border-b border-white/10 bg-black/30 px-4 py-2 text-sm">
      <span
        className={`rounded-full px-2 py-0.5 ${connected ? 'bg-emerald-500/20 text-emerald-300' : 'bg-red-500/20 text-red-300'}`}
      >
        {connected ? 'WS connected' : 'WS offline'}
      </span>
      <span className="text-white/50">role: {role ?? '—'}</span>
      <span className={`rounded-full border px-2 py-0.5 font-medium ${MISSION_STYLES[missionState]}`}>
        {missionState}
      </span>
      <span className={serialOk ? 'text-emerald-300' : 'text-red-300'}>
        serial {serialOk ? 'ok' : 'down'}
      </span>
      <span className={gpsFix ? 'text-emerald-300' : 'text-white/40'}>
        GPS {gpsFix ? 'fix' : 'no fix'}
      </span>
    </div>
  );
}
