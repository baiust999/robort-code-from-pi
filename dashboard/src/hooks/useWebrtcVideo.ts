import { useCallback, useEffect, useRef, useState } from 'react';
import { negotiateWebrtc } from '../lib/api';

/** Delay between attempts while P2 is still starting (e.g. right after Pi boot). */
const STARTUP_RETRY_MS = 3000;

export interface WebrtcVideoState {
  videoRef: React.RefObject<HTMLVideoElement | null>;
  connected: boolean;
  error: string | null;
  /** True while waiting for P2 to come up before the first successful connection. */
  waiting: boolean;
  /** Operator-initiated reconnect after the stream has failed. */
  retry: () => void;
}

/**
 * Negotiates one WebRTC connection to P2 and attaches inbound tracks to a <video>.
 *
 * Until the first connection succeeds, failures are retried automatically: P2
 * takes several seconds longer than P1 to start, so a dashboard opened during
 * boot would otherwise be stuck on an error. Once video has connected, a later
 * loss is surfaced as an error and only reconnected via retry(), so the
 * operator sees the drop rather than having it papered over.
 */
export function useWebrtcVideo(): WebrtcVideoState {
  const videoRef = useRef<HTMLVideoElement>(null);
  const everConnected = useRef(false);
  const [attempt, setAttempt] = useState(0);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [waiting, setWaiting] = useState(false);

  const retry = useCallback(() => {
    everConnected.current = false;
    setError(null);
    setWaiting(false);
    setAttempt((n) => n + 1);
  }, []);

  useEffect(() => {
    let cancelled = false;
    let pc: RTCPeerConnection | null = null;
    let retryTimer: ReturnType<typeof setTimeout> | null = null;

    function fail(message: string) {
      if (cancelled) return;
      setConnected(false);
      if (everConnected.current) {
        setError(message);
        return;
      }
      // Never connected yet: P2 is most likely still starting, keep trying.
      setWaiting(true);
      if (retryTimer === null) {
        retryTimer = setTimeout(() => setAttempt((n) => n + 1), STARTUP_RETRY_MS);
      }
    }

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
          if (pc.connectionState === 'connected') {
            everConnected.current = true;
            setConnected(true);
            setWaiting(false);
            setError(null);
          } else if (pc.connectionState === 'failed') {
            fail('WebRTC connection failed');
          } else {
            setConnected(false);
          }
        };

        const offer = await pc.createOffer();
        await pc.setLocalDescription(offer);
        const answer = await negotiateWebrtc(offer);
        if (cancelled) return;
        await pc.setRemoteDescription(answer);
      } catch (err) {
        fail(err instanceof Error ? err.message : 'webrtc setup failed');
      }
    }

    start();

    return () => {
      cancelled = true;
      if (retryTimer !== null) clearTimeout(retryTimer);
      pc?.close();
    };
  }, [attempt]);

  return { videoRef, connected, error, waiting, retry };
}
