import { useState } from 'react';
import { deleteVictim, startNewMission } from '../lib/api';
import type { VictimMark } from '../lib/protocol';
import { downloadVictimPhoto, downloadVictimRecord, localSnapshotUrl, useLocalSnapshots } from '../lib/saveVictim';

/** Every victim marked this mission, newest first. The robot keeps the marks; snapshots live only on the device that took them. */
export function VictimList(props: {
  marks: VictimMark[];
  controllerKey: string | null;
  onDeleted: (id: string) => void;
  onNewMission: () => void;
}) {
  const { controllerKey, onDeleted, onNewMission } = props;
  const marks = [...props.marks].reverse();
  const [deleting, setDeleting] = useState<string | null>(null);
  const [rotating, setRotating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  useLocalSnapshots();

  async function remove(mark: VictimMark) {
    if (!window.confirm(`Delete this mark${mark.note ? ` ("${mark.note}")` : ''}? This cannot be undone.`)) return;
    setError(null);
    setDeleting(mark.id);
    try {
      await deleteVictim(controllerKey, mark.id);
      onDeleted(mark.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'could not delete');
    } finally {
      setDeleting(null);
    }
  }

  async function newMission() {
    if (marks.length > 0) {
      const ok = window.confirm(
        `Start a new mission? These ${marks.length} mark(s) are archived under a dated filename on the robot (not deleted) and this list starts empty.`,
      );
      if (!ok) return;
    }
    setError(null);
    setRotating(true);
    try {
      await startNewMission(controllerKey);
      onNewMission();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'could not start new mission');
    } finally {
      setRotating(false);
    }
  }

  return (
    <div>
      <div className="mb-1 flex items-center justify-between gap-2">
        <h3 className="text-xs font-semibold uppercase tracking-wide text-white/50">
          Victims found ({marks.length})
        </h3>
        <button
          type="button"
          disabled={!controllerKey || rotating}
          onClick={() => void newMission()}
          title={controllerKey ? 'Archive these marks and start a fresh list for a new mission' : 'Controller key required'}
          className="text-[11px] text-white/50 hover:text-white/80 hover:underline disabled:opacity-40"
        >
          {rotating ? 'archiving…' : 'new mission'}
        </button>
      </div>
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
            <button
              type="button"
              disabled={!controllerKey || deleting === m.id}
              onClick={() => void remove(m)}
              title={controllerKey ? 'Remove this mark' : 'Controller key required to delete'}
              className="text-red-400 hover:underline disabled:opacity-40"
            >
              {deleting === m.id ? 'deleting…' : 'delete'}
            </button>
          </div>
        ))}
        {marks.length === 0 && <div className="text-white/30">none marked yet</div>}
      </div>
      {error && <div className="mt-1 text-xs text-red-400">{error}</div>}
    </div>
  );
}
