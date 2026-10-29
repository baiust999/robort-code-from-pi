import { useState, type FormEvent } from 'react';
import { postVictim } from '../lib/api';
import type { VictimMark } from '../lib/protocol';
import type { PersonBox } from '../hooks/usePersonDetection';
import { drawPersonBoxes } from '../lib/drawPersonBoxes';

const NOTE_MAX = 280;
const JPEG_QUALITY = 0.8;

/** The current video frame, with the AI boxes drawn on, as base64 JPEG (no data: prefix). */
async function captureSnapshot(video: HTMLVideoElement, boxes: PersonBox[]): Promise<string | null> {
  if (!video.videoWidth) return null;
  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext('2d');
  if (!ctx) return null;
  ctx.drawImage(video, 0, 0);
  drawPersonBoxes(ctx, boxes, 1, 0, 0);
  const blob = await new Promise<Blob | null>((resolve) => canvas.toBlob(resolve, 'image/jpeg', JPEG_QUALITY));
  if (!blob) return null;
  const bytes = new Uint8Array(await blob.arrayBuffer());
  let binary = '';
  for (let i = 0; i < bytes.length; i += 0x8000) {
    binary += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
  }
  return btoa(binary);
}

function savedMessage(mark: VictimMark): string {
  if (mark.gps_fix) return 'Saved ✓ (with GPS fix)';
  if (mark.last_fix) return 'Saved ✓, no GPS fix: map shows the last known position. Add a location note.';
  return 'Saved ✓, no GPS position at all. Describe the location in the note.';
}

/**
 * "Mark victim here": saves the moment on the robot with P1's own GPS and
 * servo angles, a note, and a snapshot of what the camera sees.
 */
export function MarkVictimButton(props: {
  videoRef: React.RefObject<HTMLVideoElement | null>;
  boxes: PersonBox[];
  bestScore: number | null;
  controllerKey: string | null;
  disabled: boolean;
  onSaved: (mark: VictimMark) => void;
}) {
  const { videoRef, boxes, bestScore, controllerKey, disabled, onSaved } = props;
  const [open, setOpen] = useState(false);
  const [note, setNote] = useState('');
  const [saving, setSaving] = useState(false);
  const [status, setStatus] = useState<{ ok: boolean; text: string } | null>(null);
  // Taken when the form opens, so the snapshot is what made the operator click.
  const [pending, setPending] = useState<{ snapshot: string | null; score: number | null } | null>(null);

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
        snapshot_b64: pending.snapshot,
      });
      onSaved(mark);
      setStatus({ ok: true, text: savedMessage(mark) });
      setOpen(false);
      setNote('');
      setPending(null);
    } catch (err) {
      setStatus({ ok: false, text: err instanceof Error ? err.message : 'could not save' });
    } finally {
      setSaving(false);
    }
  }

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
      {status && <span className={`text-xs ${status.ok ? 'text-green-400' : 'text-red-400'}`}>{status.text}</span>}
    </div>
  );
}
