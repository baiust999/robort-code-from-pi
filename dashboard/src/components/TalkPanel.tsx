import { useEffect, useRef, useState, type FormEvent } from 'react';
import {
  SCREEN_TEXT_MAX,
  type DisplayMode,
  type TalkbackState,
  type VideoSource,
} from '../hooks/useTalkback';

const DISPLAY_MODES: { id: DisplayMode; label: string }[] = [
  { id: 'robot', label: '🖥 Robot Display' },
  { id: 'vnc', label: '💻 VNC Mode' },
];

const SOURCES: { id: VideoSource; label: string }[] = [
  { id: 'none', label: 'Nothing' },
  { id: 'camera', label: 'My camera' },
  { id: 'image', label: 'Image' },
  { id: 'screen', label: 'My screen' },
];

/** Talk to the victim through the robot's speaker and display, Section 16. */
export function TalkPanel(props: { talk: TalkbackState; linkUp: boolean }) {
  const { talk, linkUp } = props;
  const [text, setText] = useState('');
  const [sentTs, setSentTs] = useState<number | null>(null);
  const fileInput = useRef<HTMLInputElement>(null);
  const preview = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    if (preview.current) preview.current.srcObject = talk.previewStream;
  }, [talk.previewStream]);

  const blocked = !linkUp || talk.floor === 'other';
  const shown = sentTs !== null && talk.lastAckTs === sentTs;

  function submit(e: FormEvent) {
    e.preventDefault();
    const ts = talk.sendText(text);
    if (ts !== null) {
      setSentTs(ts);
      setText('');
    }
  }

  function pick(source: VideoSource) {
    if (source === 'image') {
      fileInput.current?.click();
    } else {
      talk.showVideo(source);
    }
  }

  return (
    <section className="flex flex-col gap-2 rounded-lg border border-white/10 bg-white/5 p-3 text-sm">
      <div className="flex items-center gap-2">
        <h3 className="text-xs font-semibold uppercase tracking-wide text-white/50">Talk to victim</h3>
        <span
          className={`ml-auto flex items-center gap-1 text-xs ${talk.screenOnline ? 'text-green-400' : 'text-amber-400'}`}
        >
          <span className="inline-block h-2 w-2 rounded-full bg-current" />
          robot screen {talk.screenOnline ? 'online' : 'offline'}
        </span>
        {talk.floor === 'you' && (
          <button
            type="button"
            onClick={talk.release}
            className="rounded border border-white/20 px-2 py-0.5 text-xs text-white/70 hover:bg-white/10"
          >
            Release screen
          </button>
        )}
      </div>

      <fieldset disabled={!linkUp} className="flex items-center gap-3 text-xs disabled:opacity-40">
        <legend className="sr-only">Robot display</legend>
        <span className="text-white/50">Robot display:</span>
        {DISPLAY_MODES.map((m) => (
          <label key={m.id} className="flex cursor-pointer items-center gap-1">
            <input
              type="radio"
              name="display-mode"
              value={m.id}
              checked={talk.displayMode === m.id}
              onChange={() => talk.setDisplayMode(m.id)}
            />
            {m.label}
          </label>
        ))}
      </fieldset>

      {talk.displayMode === 'vnc' && (
        <p className="rounded bg-amber-500/20 px-2 py-1 text-xs text-amber-300">
          VNC mode: the robot screen is OFF. The victim can't see your video, images or messages
          until you switch back to Robot Display.
        </p>
      )}

      {talk.floor === 'other' && (
        <p className="text-xs text-amber-300">Another operator is talking to the victim.</p>
      )}

      <div className="flex items-stretch gap-2">
        <button
          type="button"
          disabled={blocked || !talk.mediaDevicesAvailable}
          onPointerDown={(e) => {
            e.currentTarget.setPointerCapture(e.pointerId);
            talk.startTalking();
          }}
          onPointerUp={talk.stopTalking}
          onPointerCancel={talk.stopTalking}
          onLostPointerCapture={talk.stopTalking}
          className={`w-32 shrink-0 select-none rounded-md px-3 py-2 font-semibold touch-none disabled:opacity-40 ${
            talk.talking ? 'bg-red-600 text-white' : 'bg-white/10 hover:bg-white/20'
          }`}
        >
          {talk.talking ? '🎤 Talking…' : talk.micReady ? '🎤 Hold to talk' : '🎤 Enable mic'}
        </button>

        <div className="flex flex-1 flex-col gap-1">
          <span className="text-xs text-white/50">Show on robot display</span>
          <div className="flex flex-wrap gap-1">
            {SOURCES.map((s) => {
              const needsDevices = s.id === 'camera' || s.id === 'screen';
              return (
                <button
                  key={s.id}
                  type="button"
                  disabled={blocked || (needsDevices && !talk.mediaDevicesAvailable)}
                  onClick={() => pick(s.id)}
                  className={`rounded px-2 py-1 text-xs disabled:opacity-40 ${
                    talk.videoSource === s.id ? 'bg-sky-600 text-white' : 'bg-white/10 hover:bg-white/20'
                  }`}
                >
                  {s.label}
                </button>
              );
            })}
          </div>
          <input
            ref={fileInput}
            type="file"
            accept="image/*"
            hidden
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) talk.showVideo('image', file);
              e.target.value = '';
            }}
          />
        </div>

        <video
          ref={preview}
          autoPlay
          playsInline
          muted
          hidden={!talk.previewStream}
          className="h-14 w-20 shrink-0 rounded bg-black object-contain"
        />
      </div>

      <form onSubmit={submit} className="flex gap-2">
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          maxLength={SCREEN_TEXT_MAX}
          disabled={blocked}
          placeholder="Message to show on robot screen…"
          className="min-w-0 flex-1 rounded border border-white/20 bg-black/40 px-2 py-1 disabled:opacity-40"
        />
        <button
          type="submit"
          disabled={blocked || !text.trim()}
          className="rounded bg-sky-600 px-3 py-1 font-semibold disabled:opacity-40"
        >
          Send
        </button>
        <button
          type="button"
          disabled={blocked}
          onClick={() => {
            talk.clearText();
            setSentTs(null);
          }}
          className="rounded bg-white/10 px-3 py-1 hover:bg-white/20 disabled:opacity-40"
        >
          Clear
        </button>
      </form>

      <div className="min-h-4 text-xs">
        {talk.error ? (
          <span className="text-red-400">{talk.error}</span>
        ) : !talk.mediaDevicesAvailable ? (
          <span className="text-white/40">
            Mic, camera and screen sharing need HTTPS; images and messages still work.
          </span>
        ) : shown ? (
          <span className="text-green-400">Message is on the robot screen ✓</span>
        ) : sentTs !== null ? (
          <span className="text-white/40">Sending message…</span>
        ) : null}
      </div>
    </section>
  );
}
