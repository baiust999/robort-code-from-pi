import { useCallback, useEffect, useRef, useState } from 'react';
import { negotiateWebrtc } from '../lib/api';
import type { Auth } from '../lib/protocol';

/** Delay between attempts while P2 is still starting (e.g. right after Pi boot). */
const STARTUP_RETRY_MS = 3000;

/**
 * The operator-to-robot half of the peer connection (Section 16): senders the
 * talk-back hook attaches the laptop mic / video source to, and the data
 * channel carrying messages for the Robot Screen.
 */
export interface TalkLink {
  audioSender: RTCRtpSender;
  videoSender: RTCRtpSender;
  channel: RTCDataChannel;
}

export interface WebrtcVideoState {
  videoRef: React.RefObject<HTMLVideoElement | null>;
  connected: boolean;
  error: string | null;
  /** True while waiting for P2 to come up before the first successful connection. */
  waiting: boolean;
  /** Operator-initiated reconnect after the stream has failed. */
  retry: () => void;
  /** Present while a peer connection exists; replaced on every reconnect. */
  talkLink: TalkLink | null;
  /** P2's controller-key check for this connection. */
  auth: Auth | null;
}

/**
 * Negotiates one WebRTC connection to P2 and attaches inbound tracks to a <video>.
 *
 * The transceivers are sendrecv so the same connection can carry the
 * operator's voice and video back to the robot; nothing is sent until the
 * talk-back hook attaches a track to a sender.
 *
 * Until the first connection succeeds, failures are retried automatically: P2
 * takes several seconds longer than P1 to start, so a dashboard opened during
 * boot would otherwise be stuck on an error. Once video has connected, a later
 * loss is surfaced as an error and only reconnected via retry(), so the
 * operator sees the drop rather than having it papered over.
 *
 * The offer carries `controllerKey`; without the right one P2 still sends
 * the robot's video and audio but ignores anything sent back. A changed key
 * renegotiates.
 */
export function useWebrtcVideo(controllerKey: string | null): WebrtcVideoState {
  const videoRef = useRef<HTMLVideoElement>(null);
  const everConnected = useRef(false);
  const [attempt, setAttempt] = useState(0);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [waiting, setWaiting] = useState(false);
  const [talkLink, setTalkLink] = useState<TalkLink | null>(null);
  const [auth, setAuth] = useState<Auth | null>(null);

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
        const videoTx = pc.addTransceiver('video', { direction: 'sendrecv' });
        const audioTx = pc.addTransceiver('audio', { direction: 'sendrecv' });
        const channel = pc.createDataChannel('screen');
        setTalkLink({ audioSender: audioTx.sender, videoSender: videoTx.sender, channel });

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
        const answer = await negotiateWebrtc(offer, controllerKey);
        if (cancelled) return;
        setAuth(answer.auth);
        await pc.setRemoteDescription({ type: answer.type, sdp: answer.sdp });
      } catch (err) {
        fail(err instanceof Error ? err.message : 'webrtc setup failed');
      }
    }

    start();

    return () => {
      cancelled = true;
      if (retryTimer !== null) clearTimeout(retryTimer);
      pc?.close();
      setTalkLink(null);
      setAuth(null);
    };
  }, [attempt, controllerKey]);

  return { videoRef, connected, error, waiting, retry, talkLink, auth };
}
