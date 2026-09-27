import { useCallback, useEffect, useRef, useState } from 'react';
import type { TalkLink } from './useWebrtcVideo';

/** What the operator is showing on the robot display. */
export type VideoSource = 'none' | 'camera' | 'image' | 'screen';

/** Who holds the robot screen: this dashboard, another operator, or nobody. */
export type Floor = 'free' | 'you' | 'other';

export const SCREEN_TEXT_MAX = 280;

/** Canvas size for still images, matched to the robot's 1024×600 display. */
const IMAGE_WIDTH = 1024;
const IMAGE_HEIGHT = 576;
/** Repaint interval for a still image; P2 repeats the last frame after 1 s. */
const IMAGE_REPAINT_MS = 500;

export interface TalkbackState {
  /** Mic and camera need a secure context; images and text work regardless. */
  mediaDevicesAvailable: boolean;
  screenOnline: boolean;
  floor: Floor;
  talking: boolean;
  videoSource: VideoSource;
  /** The outgoing video track, for a local preview. */
  previewStream: MediaStream | null;
  /** Timestamp of the last message the robot screen confirmed showing. */
  lastAckTs: number | null;
  error: string | null;
  startTalking: () => void;
  stopTalking: () => void;
  showVideo: (source: VideoSource, image?: File) => void;
  /** Returns the message timestamp (matched against lastAckTs), or null if not sent. */
  sendText: (text: string) => number | null;
  clearText: () => void;
  release: () => void;
}

function drawContained(ctx: CanvasRenderingContext2D, img: HTMLImageElement) {
  const scale = Math.min(IMAGE_WIDTH / img.width, IMAGE_HEIGHT / img.height);
  const w = img.width * scale;
  const h = img.height * scale;
  ctx.fillStyle = '#000';
  ctx.fillRect(0, 0, IMAGE_WIDTH, IMAGE_HEIGHT);
  ctx.drawImage(img, (IMAGE_WIDTH - w) / 2, (IMAGE_HEIGHT - h) / 2, w, h);
}

function loadImage(file: File): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(file);
    const img = new Image();
    img.onload = () => {
      URL.revokeObjectURL(url);
      resolve(img);
    };
    img.onerror = () => {
      URL.revokeObjectURL(url);
      reject(new Error('could not read that image'));
    };
    img.src = url;
  });
}

/**
 * Operator-to-victim talk-back over the P2 peer connection, Section 16.
 *
 * Push-to-talk toggles the laptop mic track's `enabled` flag rather than
 * swapping tracks, so talking starts without a renegotiation or a fresh
 * permission prompt. The first action (talk, show video, send text) claims
 * the robot screen; P2 refuses it while another operator holds it.
 */
export function useTalkback(link: TalkLink | null): TalkbackState {
  const mediaDevicesAvailable =
    typeof window !== 'undefined' && window.isSecureContext && !!navigator.mediaDevices;

  const [screenOnline, setScreenOnline] = useState(false);
  const [floor, setFloor] = useState<Floor>('free');
  const [talking, setTalking] = useState(false);
  const [videoSource, setVideoSource] = useState<VideoSource>('none');
  const [previewStream, setPreviewStream] = useState<MediaStream | null>(null);
  const [lastAckTs, setLastAckTs] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const micRef = useRef<MediaStreamTrack | null>(null);
  const videoTrackRef = useRef<MediaStreamTrack | null>(null);
  const repaintTimer = useRef<ReturnType<typeof setInterval> | null>(null);
  const talkingRef = useRef(false);
  const sourceRef = useRef<VideoSource>('none');
  // Bumped on every showVideo() so a slow getUserMedia can't win a race
  // against a newer choice.
  const videoRequest = useRef(0);

  const send = useCallback(
    (payload: object) => {
      if (link?.channel.readyState !== 'open') return false;
      link.channel.send(JSON.stringify(payload));
      return true;
    },
    [link],
  );

  const sendMediaState = useCallback(() => {
    send({ type: 'media_state', talking: talkingRef.current, video: sourceRef.current });
  }, [send]);

  const stopVideoTrack = useCallback(() => {
    if (repaintTimer.current !== null) {
      clearInterval(repaintTimer.current);
      repaintTimer.current = null;
    }
    videoTrackRef.current?.stop();
    videoTrackRef.current = null;
    setPreviewStream(null);
  }, []);

  // Data channel: status from P2 and acks from the robot screen.
  useEffect(() => {
    if (!link) return;
    const channel = link.channel;
    function onMessage(event: MessageEvent) {
      let msg: { type?: string; [k: string]: unknown };
      try {
        msg = JSON.parse(event.data as string);
      } catch {
        return;
      }
      if (msg.type === 'talk_status') {
        setScreenOnline(Boolean(msg.screen_online));
        setFloor((msg.floor as Floor) ?? 'free');
      } else if (msg.type === 'screen_ack') {
        setLastAckTs(typeof msg.ts === 'number' ? msg.ts : null);
      } else if (msg.type === 'floor_denied') {
        setError('Another operator is using the robot screen.');
      }
    }
    // The peer connection reports "connected" slightly before the data
    // channel opens; replay anything the operator started in that gap.
    function onOpen() {
      if (talkingRef.current || sourceRef.current !== 'none') sendMediaState();
    }
    channel.addEventListener('message', onMessage);
    channel.addEventListener('open', onOpen);
    return () => {
      channel.removeEventListener('message', onMessage);
      channel.removeEventListener('open', onOpen);
    };
  }, [link, sendMediaState]);

  // A new connection starts from nothing: drop local media and state.
  useEffect(() => {
    return () => {
      micRef.current?.stop();
      micRef.current = null;
      stopVideoTrack();
      talkingRef.current = false;
      sourceRef.current = 'none';
      setTalking(false);
      setVideoSource('none');
      setScreenOnline(false);
      setFloor('free');
      setLastAckTs(null);
    };
  }, [link, stopVideoTrack]);

  const startTalking = useCallback(async () => {
    if (!link) return;
    if (!mediaDevicesAvailable) {
      setError('Microphone needs HTTPS or the Chrome insecure-origin flag.');
      return;
    }
    setError(null);
    talkingRef.current = true;
    setTalking(true);
    try {
      if (!micRef.current) {
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true },
        });
        micRef.current = stream.getAudioTracks()[0];
        await link.audioSender.replaceTrack(micRef.current);
      }
      // Released before the permission prompt was answered.
      micRef.current.enabled = talkingRef.current;
      sendMediaState();
    } catch (err) {
      talkingRef.current = false;
      setTalking(false);
      setError(err instanceof Error ? `Microphone: ${err.message}` : 'Microphone unavailable');
    }
  }, [link, mediaDevicesAvailable, sendMediaState]);

  const stopTalking = useCallback(() => {
    if (!talkingRef.current) return;
    talkingRef.current = false;
    setTalking(false);
    if (micRef.current) micRef.current.enabled = false;
    sendMediaState();
  }, [sendMediaState]);

  const showVideo = useCallback(
    async (source: VideoSource, image?: File) => {
      if (!link) return;
      const request = ++videoRequest.current;
      setError(null);
      try {
        let track: MediaStreamTrack | null = null;
        let timer: ReturnType<typeof setInterval> | null = null;

        if (source === 'camera' || source === 'screen') {
          if (!mediaDevicesAvailable) {
            throw new Error('camera and screen sharing need HTTPS or the Chrome insecure-origin flag');
          }
          const stream =
            source === 'camera'
              ? await navigator.mediaDevices.getUserMedia({
                  video: { width: 640, height: 480, frameRate: 10 },
                })
              : await navigator.mediaDevices.getDisplayMedia({ video: { frameRate: 5 } });
          track = stream.getVideoTracks()[0];
        } else if (source === 'image') {
          if (!image) return;
          const img = await loadImage(image);
          const canvas = document.createElement('canvas');
          canvas.width = IMAGE_WIDTH;
          canvas.height = IMAGE_HEIGHT;
          const ctx = canvas.getContext('2d');
          if (!ctx) throw new Error('canvas unavailable');
          drawContained(ctx, img);
          track = canvas.captureStream(2).getVideoTracks()[0];
          // captureStream only emits frames when the canvas changes, so keep
          // repainting to keep the still image flowing to the robot.
          timer = setInterval(() => drawContained(ctx, img), IMAGE_REPAINT_MS);
        }

        if (request !== videoRequest.current) {
          track?.stop();
          if (timer !== null) clearInterval(timer);
          return;
        }

        stopVideoTrack();
        videoTrackRef.current = track;
        repaintTimer.current = timer;
        await link.videoSender.replaceTrack(track);
        setPreviewStream(track ? new MediaStream([track]) : null);
        sourceRef.current = track ? source : 'none';
        setVideoSource(sourceRef.current);
        sendMediaState();

        // The browser's own "Stop sharing" bar ends the track.
        track?.addEventListener('ended', () => {
          if (videoTrackRef.current !== track) return;
          stopVideoTrack();
          link.videoSender.replaceTrack(null);
          sourceRef.current = 'none';
          setVideoSource('none');
          sendMediaState();
        });
      } catch (err) {
        if (request !== videoRequest.current) return;
        setError(err instanceof Error ? err.message : 'could not start video');
      }
    },
    [link, mediaDevicesAvailable, sendMediaState, stopVideoTrack],
  );

  const sendText = useCallback(
    (text: string) => {
      const trimmed = text.trim().slice(0, SCREEN_TEXT_MAX);
      if (!trimmed) return null;
      setError(null);
      const ts = Date.now();
      return send({ type: 'screen_text', text: trimmed, ts }) ? ts : null;
    },
    [send],
  );

  const clearText = useCallback(() => {
    send({ type: 'screen_clear' });
  }, [send]);

  const release = useCallback(() => {
    stopTalking();
    videoRequest.current++;
    stopVideoTrack();
    link?.videoSender.replaceTrack(null);
    sourceRef.current = 'none';
    setVideoSource('none');
    send({ type: 'floor_release' });
  }, [link, send, stopTalking, stopVideoTrack]);

  return {
    mediaDevicesAvailable,
    screenOnline,
    floor,
    talking,
    videoSource,
    previewStream,
    lastAckTs,
    error,
    startTalking: () => void startTalking(),
    stopTalking,
    showVideo: (source, image) => void showVideo(source, image),
    sendText,
    clearText,
    release,
  };
}
