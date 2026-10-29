import { useEffect, useRef, useState } from 'react';
import type { WebrtcVideoState } from '../hooks/useWebrtcVideo';
import type { PersonBox, PersonDetectionState } from '../hooks/usePersonDetection';
import { drawPersonBoxes } from '../lib/drawPersonBoxes';

/** Keeps the overlay canvas the size of the video box and draws the boxes where the picture is. */
function DetectionOverlay(props: { videoRef: WebrtcVideoState['videoRef']; boxes: PersonBox[] }) {
  const { videoRef, boxes } = props;
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [size, setSize] = useState({ w: 0, h: 0 });

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const observer = new ResizeObserver(([entry]) =>
      setSize({ w: entry.contentRect.width, h: entry.contentRect.height }),
    );
    observer.observe(canvas);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    const video = videoRef.current;
    const ctx = canvas?.getContext('2d');
    if (!canvas || !ctx || !video) return;
    const dpr = window.devicePixelRatio || 1;
    canvas.width = Math.round(size.w * dpr);
    canvas.height = Math.round(size.h * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, size.w, size.h);
    if (boxes.length === 0 || !video.videoWidth) return;
    // object-contain: the picture is scaled to fit and centred, with bars.
    const scale = Math.min(size.w / video.videoWidth, size.h / video.videoHeight);
    const dx = (size.w - video.videoWidth * scale) / 2;
    const dy = (size.h - video.videoHeight * scale) / 2;
    drawPersonBoxes(ctx, boxes, scale, dx, dy);
  }, [boxes, size, videoRef]);

  return <canvas ref={canvasRef} className="pointer-events-none absolute inset-0 h-full w-full" />;
}

export function VideoSurface(props: { video: WebrtcVideoState; detection: PersonDetectionState }) {
  const { videoRef, connected, error, waiting, retry } = props.video;
  const detection = props.detection;
  // Browsers only autoplay muted media, so the robot's microphone starts
  // muted and the operator turns it on with a click.
  const [listening, setListening] = useState(false);

  useEffect(() => {
    const el = videoRef.current;
    if (!el) return;
    el.muted = !listening;
    if (listening) el.play().catch(() => setListening(false));
  }, [listening, videoRef]);

  let aiLabel = '🤖 AI: off';
  if (detection.enabled) aiLabel = detection.error ? '🤖 AI: error' : detection.ready ? '🤖 AI: on' : '🤖 AI: loading…';

  return (
    <div className="flex flex-col gap-1">
      <div className="relative aspect-video w-full overflow-hidden rounded-lg bg-black">
        <video ref={videoRef} autoPlay playsInline muted className="h-full w-full object-contain" />
        {connected && <DetectionOverlay videoRef={videoRef} boxes={detection.boxes} />}
        {connected && detection.personPresent && (
          <div className="absolute top-2 left-2 animate-pulse rounded bg-red-600 px-2 py-1 text-sm font-bold text-white">
            POSSIBLE PERSON
          </div>
        )}
        {connected && (
          <div className="absolute right-2 bottom-2 flex gap-1">
            <button
              type="button"
              onClick={() => detection.setEnabled(!detection.enabled)}
              title={detection.error ?? 'Person detection on the video, run on this computer'}
              className="rounded bg-black/60 px-2 py-1 text-xs text-white/90 hover:bg-black/80"
            >
              {aiLabel}
            </button>
            <button
              type="button"
              onClick={() => setListening((on) => !on)}
              className="rounded bg-black/60 px-2 py-1 text-xs text-white/90 hover:bg-black/80"
            >
              {listening ? '🔊 Robot mic on' : '🔇 Listen to robot mic'}
            </button>
          </div>
        )}
        {!connected && (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-2 text-sm text-white/50">
            {error ? (
              <>
                <span>video error: {error}</span>
                <button
                  type="button"
                  onClick={retry}
                  className="rounded border border-white/30 px-3 py-1 text-white/80 hover:bg-white/10"
                >
                  Retry video
                </button>
              </>
            ) : waiting ? (
              'waiting for video server…'
            ) : (
              'connecting to video…'
            )}
          </div>
        )}
      </div>
      {detection.error && <p className="text-xs text-amber-300">{detection.error}</p>}
      {detection.enabled && (
        <p className="text-xs text-white/40">
          AI detects people only when visible and lit; it can miss victims. Always check the video yourself.
        </p>
      )}
    </div>
  );
}
