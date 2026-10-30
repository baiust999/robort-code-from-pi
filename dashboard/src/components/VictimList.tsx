import type { VictimMark } from '../lib/protocol';
import { downloadVictimPhoto, downloadVictimRecord, localSnapshotUrl, useLocalSnapshots } from '../lib/saveVictim';

/** Every victim marked this mission, newest first. The robot keeps the marks; snapshots live only on the device that took them. */
export function VictimList(props: { marks: VictimMark[] }) {
  const marks = [...props.marks].reverse();
  useLocalSnapshots();
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
            {localSnapshotUrl(m.id) && (
              <a href={localSnapshotUrl(m.id)!} target="_blank" rel="noreferrer" className="text-sky-400 hover:underline">
                snapshot
              </a>
            )}
            {localSnapshotUrl(m.id) && (
              <button
                type="button"
                onClick={() => downloadVictimPhoto(m)}
                title="Download the snapshot kept on this device"
                className="text-sky-400 hover:underline"
              >
                save photo
              </button>
            )}
            <button
              type="button"
              onClick={() => downloadVictimRecord(m)}
              title="Download the details as a text file"
              className="text-sky-400 hover:underline"
            >
              save details
            </button>
          </div>
        ))}
        {marks.length === 0 && <div className="text-white/30">none marked yet</div>}
      </div>
    </div>
  );
}
