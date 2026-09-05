import { useEffect, useRef, useState } from 'react';
import { negotiateWebrtc } from '../lib/api';

export interface WebrtcVideoState {
  videoRef: React.RefObject<HTMLVideoElement | null>;
  connected: boolean;
  error: string | null;
}

/** Negotiates one WebRTC connection to P2 and attaches inbound tracks to a <video>. */
export function useWebrtcVideo(): WebrtcVideoState {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    let pc: RTCPeerConnection | null = null;

    async function start() {
      try {
        pc = new RTCPeerConnection();
        pc.addTransceiver('video', { direction: 'recvonly' });
        pc.addTransceiver('audio', { direction: 'recvonly' });

        const stream = new MediaStream();
        pc.ontrack = (event) => {
          stream.addTrack(event.track);
          if (videoRef.current) {
            videoRef.current.srcObject = stream;
          }
        };
        pc.onconnectionstatechange = () => {
          if (!pc || cancelled) return;
          setConnected(pc.connectionState === 'connected');
          if (pc.connectionState === 'failed') {
            setError('WebRTC connection failed');
          }
        };

        const offer = await pc.createOffer();
        await pc.setLocalDescription(offer);
        const answer = await negotiateWebrtc(offer);
        if (cancelled) return;
        await pc.setRemoteDescription(answer);
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : 'webrtc setup failed');
      }
    }

    start();

    return () => {
      cancelled = true;
      pc?.close();
    };
  }, []);

  return { videoRef, connected, error };
}
