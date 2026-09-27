import { useEffect, useState } from 'react';
import type { WebrtcVideoState } from '../hooks/useWebrtcVideo';

export function VideoSurface(props: { video: WebrtcVideoState }) {
  const { videoRef, connected, error, waiting, retry } = props.video;
  // Browsers only autoplay muted media, so the robot's microphone starts
  // muted and the operator turns it on with a click.
  const [listening, setListening] = useState(false);

  useEffect(() => {
    const el = videoRef.current;
    if (!el) return;
    el.muted = !listening;
    if (listening) el.play().catch(() => setListening(false));
  }, [listening, videoRef]);

  return (
    <div className="relative aspect-video w-full overflow-hidden rounded-lg bg-black">
      <video ref={videoRef} autoPlay playsInline muted className="h-full w-full object-contain" />
      {connected && (
        <button
          type="button"
          onClick={() => setListening((on) => !on)}
          className="absolute right-2 bottom-2 rounded bg-black/60 px-2 py-1 text-xs text-white/90 hover:bg-black/80"
        >
          {listening ? '🔊 Robot mic on' : '🔇 Listen to robot mic'}
        </button>
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
  );
}
