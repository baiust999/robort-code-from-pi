import { useWebrtcVideo } from '../hooks/useWebrtcVideo';

export function VideoSurface() {
  const { videoRef, connected, error, waiting, retry } = useWebrtcVideo();
  return (
    <div className="relative aspect-video w-full overflow-hidden rounded-lg bg-black">
      <video ref={videoRef} autoPlay playsInline muted className="h-full w-full object-contain" />
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
