import { victimSnapshotUrl } from '../lib/api';
import type { VictimMark } from '../lib/protocol';

/** Every victim marked this mission, newest first; stored on the robot. */
export function VictimList(props: { marks: VictimMark[] }) {
  const marks = [...props.marks].reverse();
  return (
    <div>
      <h3 className="mb-1 text-xs font-semibold uppercase tracking-wide text-white/50">
        Victims found ({marks.length})
      </h3>
      <div className="flex max-h-40 flex-col overflow-y-auto rounded-lg border border-white/10 bg-black/30 p-2 text-xs">
        {marks.map((m) => (
          <div key={m.id} className="flex flex-wrap items-baseline gap-x-2 border-b border-white/5 py-1">
            <span className="text-white/30">{new Date(m.ts).toLocaleTimeString()}</span>
            <span className="text-white/80">{m.note || '(no note)'}</span>
            <span className={m.gps_fix ? 'text-green-400' : 'text-amber-300'}>
              {m.gps_fix ? 'GPS' : m.last_fix ? 'no fix (last known)' : 'no position'}
            </span>
            {m.snapshot && (
              <a href={victimSnapshotUrl(m.id)} target="_blank" rel="noreferrer" className="text-sky-400 hover:underline">
                snapshot
              </a>
            )}
          </div>
        ))}
        {marks.length === 0 && <div className="text-white/30">none marked yet</div>}
      </div>
    </div>
  );
}
