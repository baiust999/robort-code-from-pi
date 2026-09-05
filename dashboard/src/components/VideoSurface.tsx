import { useWebrtcVideo } from '../hooks/useWebrtcVideo';

export function VideoSurface() {
  const { videoRef, connected, error } = useWebrtcVideo();
  return (
    <div className="relative aspect-video w-full overflow-hidden rounded-lg bg-black">
      <video ref={videoRef} autoPlay playsInline muted className="h-full w-full object-contain" />
      {!connected && (
        <div className="absolute inset-0 flex items-center justify-center text-sm text-white/50">
          {error ? `video error: ${error}` : 'connecting to video…'}
        </div>
      )}
    </div>
  );
}
