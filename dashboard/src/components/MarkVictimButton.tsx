import { useState, type FormEvent } from 'react';
import { deleteVictim, postVictim } from '../lib/api';
import type { VictimMark } from '../lib/protocol';
import type { PersonBox } from '../hooks/usePersonDetection';
import { drawPersonBoxes } from '../lib/drawPersonBoxes';
import { downloadVictimPhoto, downloadVictimRecord, forgetSnapshot, saveVictimToDevice } from '../lib/saveVictim';

const NOTE_MAX = 280;
const JPEG_QUALITY = 0.8;

/** The current video frame, with the AI boxes drawn on, as a JPEG. */
async function captureSnapshot(video: HTMLVideoElement, boxes: PersonBox[]): Promise<Blob | null> {
  if (!video.videoWidth) return null;
  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext('2d');
  if (!ctx) return null;
  ctx.drawImage(video, 0, 0);
  drawPersonBoxes(ctx, boxes, 1, 0, 0);
  return new Promise<Blob | null>((resolve) => canvas.toBlob(resolve, 'image/jpeg', JPEG_QUALITY));
}

function savedMessage(mark: VictimMark, photo: boolean, stored: boolean): string {
  let where = ' Details sent to Downloads.';
  if (photo) where = stored ? ' Photo kept on this device and sent to Downloads.' : ' Photo sent to Downloads (not kept after a reload).';
  if (mark.gps_fix) return `Saved ✓ (with GPS fix).${where}`;
  if (mark.last_fix) return `Saved ✓, no GPS fix: map shows the last known position. Add a location note.${where}`;
  return `Saved ✓, no GPS position at all. Describe the location in the note.${where}`;
}

/**
 * "Mark victim here": saves the moment on the robot with P1's own GPS and
 * servo angles and a note, then downloads the snapshot of what the camera
 * sees, with a text record, to this device. The robot never gets the image.
 */
export function MarkVictimButton(props: {
  videoRef: React.RefObject<HTMLVideoElement | null>;
  boxes: PersonBox[];
  bestScore: number | null;
  controllerKey: string | null;
  disabled: boolean;
  onSaved: (mark: VictimMark) => void;
  onDeleted: (id: string) => void;
  /** The marks the robot still has, so a mark deleted elsewhere loses its links here. */
  marks: VictimMark[];
}) {
  const { videoRef, boxes, bestScore, controllerKey, disabled, onSaved, onDeleted, marks } = props;
  const [open, setOpen] = useState(false);
  const [note, setNote] = useState('');
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [status, setStatus] = useState<{ ok: boolean; text: string; mark?: VictimMark; photo?: boolean } | null>(null);
  // Taken when the form opens, so the snapshot is what made the operator click.
  const [pending, setPending] = useState<{ snapshot: Blob | null; score: number | null } | null>(null);

  async function start() {
    setStatus(null);
    const video = videoRef.current;
    const snapshot = video ? await captureSnapshot(video, boxes) : null;
    setPending({ snapshot, score: bestScore });
    setOpen(true);
  }

  async function save(e: FormEvent) {
    e.preventDefault();
    if (!pending) return;
    setSaving(true);
    try {
      const mark = await postVictim(controllerKey, {
        note: note.trim(),
        ai_score: pending.score,
      });
      const stored = await saveVictimToDevice(mark, pending.snapshot);
      onSaved(mark);
      const photo = pending.snapshot !== null;
      setStatus({ ok: true, text: savedMessage(mark, photo, stored), mark, photo });
      setOpen(false);
      setNote('');
      setPending(null);
    } catch (err) {
      setStatus({ ok: false, text: err instanceof Error ? err.message : 'could not save' });
    } finally {
      setSaving(false);
    }
  }

  // Undo for a mark saved by mistake, right where the operator just saved it.
  async function remove(mark: VictimMark) {
    const ok = window.confirm(
      'Delete this mark? It is removed from the robot and this device. Files already in Downloads stay there.',
    );
    if (!ok) return;
    setDeleting(true);
    try {
      await deleteVictim(controllerKey, mark.id);
      onDeleted(mark.id);
      forgetSnapshot(mark.id).catch(() => {});
      setStatus({ ok: true, text: 'Mark deleted.' });
    } catch (err) {
      setStatus({ ...status!, ok: false, text: err instanceof Error ? err.message : 'could not delete' });
    } finally {
      setDeleting(false);
    }
  }

  // Deleted from the victim list (or another dashboard): its message and links no longer apply.
  const markGone = status?.mark !== undefined && !marks.some((m) => m.id === status.mark!.id);

  return (
    <div className="flex flex-col gap-1 text-sm">
      {!open ? (
        <button
          type="button"
          disabled={disabled}
          onClick={() => void start()}
          className="rounded-md bg-red-700 px-3 py-2 font-semibold text-white hover:bg-red-600 disabled:opacity-40"
        >
          📍 Mark victim here
        </button>
      ) : (
        <form onSubmit={save} className="flex flex-wrap gap-2 rounded-md border border-red-500/50 bg-red-950/40 p-2">
          <input
            autoFocus
            value={note}
            onChange={(e) => setNote(e.target.value)}
            maxLength={NOTE_MAX}
            placeholder="Note: where, condition (e.g. 2nd room, under table, responding)"
            className="min-w-0 flex-1 rounded border border-white/20 bg-black/40 px-2 py-1"
          />
          <button
            type="submit"
            disabled={saving}
            className="rounded bg-red-700 px-3 py-1 font-semibold text-white disabled:opacity-40"
          >
            {saving ? 'Saving…' : 'Save'}
          </button>
          <button
            type="button"
            onClick={() => {
              setOpen(false);
              setPending(null);
            }}
            className="rounded bg-white/10 px-3 py-1 hover:bg-white/20"
          >
            Cancel
          </button>
          {!pending?.snapshot && <span className="w-full text-xs text-amber-300">No video frame: saving without a snapshot.</span>}
        </form>
      )}
      {status && <span className={`text-xs ${status.ok ? 'text-green-400' : 'text-red-400'}`}>{markGone ? 'Mark deleted.' : status.text}</span>}
      {status?.mark && !markGone && (
        <span className="text-xs text-white/60">
          No files in Downloads? Click:{' '}
          {status.photo && (
            <button type="button" onClick={() => downloadVictimPhoto(status.mark!)} className="text-sky-400 hover:underline">
              download photo
            </button>
          )}{' '}
          <button type="button" onClick={() => downloadVictimRecord(status.mark!)} className="text-sky-400 hover:underline">
            download details
          </button>
          {' · '}
          <button
            type="button"
            disabled={!controllerKey || deleting}
            onClick={() => void remove(status.mark!)}
            title={controllerKey ? 'Saved by mistake? Remove this mark' : 'Controller key required to delete'}
            className="text-red-400 hover:underline disabled:opacity-40"
          >
            {deleting ? 'deleting…' : 'delete mark'}
          </button>
        </span>
      )}
    </div>
  );
}
