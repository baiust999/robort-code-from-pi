import { useCallback, useEffect, useRef, useState } from 'react';
import type { TalkLink } from './useWebrtcVideo';

/** What the operator is showing on the robot display. */
export type VideoSource = 'none' | 'camera' | 'image' | 'screen';

/** Who holds the robot screen: this dashboard, another operator, or nobody. */
export type Floor = 'free' | 'you' | 'other';

/** What the robot's display shows: the Robot Screen kiosk, or the Pi desktop for VNC. */
export type DisplayMode = 'robot' | 'vnc';

export const SCREEN_TEXT_MAX = 280;
/** Limits on a tap-to-answer question; P2 enforces the same (talkback.py). */
export const QUESTION_OPTIONS_MIN = 2;
export const QUESTION_OPTIONS_MAX = 4;
export const QUESTION_OPTION_MAX = 40;

/** The question on the robot screen and what became of it, as P2 reports it. */
export interface QuestionStatus {
  id: number;
  text: string;
  options: string[];
  status: 'waiting' | 'answered' | 'expired' | 'cleared';
  /** Index into options once answered. */
  answer: number | null;
  /** Seconds until it times out, while waiting. */
  remainingS: number | null;
  /** Local clock when this status arrived, to count remainingS down from. */
  receivedAt: number;
}

/** Canvas size for still images, matched to the robot's 1024×600 display. */
const IMAGE_WIDTH = 1024;
const IMAGE_HEIGHT = 576;
/** Repaint interval for a still image; P2 repeats the last frame after 1 s. */
const IMAGE_REPAINT_MS = 500;

/** The looping voice message held by P2, as it reports it. */
export interface VoiceStatus {
  /** Bumped by P2 on every upload; null when no message is stored. */
  id: number | null;
  hasClip: boolean;
  playing: boolean;
  durationS: number | null;
}

export type VoiceCommand = 'voice_loop_start' | 'voice_loop_stop' | 'voice_clear';

export interface TalkbackState {
  /** Mic and camera need a secure context; images and text work regardless. */
  mediaDevicesAvailable: boolean;
  screenOnline: boolean;
  /** P2 accepts talk, video, text and display switches from this session (it has the key). */
  canControl: boolean;
  floor: Floor;
  /** As reported by P2, so it reflects switches made on the robot too. */
  displayMode: DisplayMode;
  talking: boolean;
  /** The laptop mic is open and attached; until then a press only enables it. */
  micReady: boolean;
  videoSource: VideoSource;
  /** The outgoing video track, for a local preview. */
  previewStream: MediaStream | null;
  /** Timestamp of the last message the robot screen confirmed showing. */
  lastAckTs: number | null;
  question: QuestionStatus | null;
  voice: VoiceStatus | null;
  error: string | null;
  startTalking: () => void;
  stopTalking: () => void;
  showVideo: (source: VideoSource, image?: File) => void;
  /** Returns the message timestamp (matched against lastAckTs), or null if not sent. */
  sendText: (text: string) => number | null;
  clearText: () => void;
  /** Returns false if the question could not be sent. */
  askQuestion: (text: string, options: string[]) => boolean;
  clearQuestion: () => void;
  release: () => void;
  setDisplayMode: (mode: DisplayMode) => void;
  /** Start/stop/clear the robot-side voice loop; returns false if not sent. */
  sendVoiceCommand: (command: VoiceCommand) => boolean;
  setError: (error: string | null) => void;
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
 * permission prompt. The first action (talk, show video, send text or a
 * question) claims the robot screen; P2 refuses it while another operator
 * holds it.
 */
export function useTalkback(link: TalkLink | null): TalkbackState {
  const mediaDevicesAvailable =
    typeof window !== 'undefined' && window.isSecureContext && !!navigator.mediaDevices;

  const [screenOnline, setScreenOnline] = useState(false);
  const [canControl, setCanControl] = useState(false);
  const [floor, setFloor] = useState<Floor>('free');
  const [displayMode, setDisplayModeState] = useState<DisplayMode>('robot');
  const [talking, setTalking] = useState(false);
  const [micReady, setMicReady] = useState(false);
  const [videoSource, setVideoSource] = useState<VideoSource>('none');
  const [previewStream, setPreviewStream] = useState<MediaStream | null>(null);
  const [lastAckTs, setLastAckTs] = useState<number | null>(null);
  const [question, setQuestion] = useState<QuestionStatus | null>(null);
  const [voice, setVoice] = useState<VoiceStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  const micRef = useRef<MediaStreamTrack | null>(null);
  const micRequest = useRef<Promise<void> | null>(null);
  // Bumped when the connection is torn down, so a getUserMedia that
  // resolves afterwards doesn't attach its track to the new connection.
  const micGeneration = useRef(0);
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
    send({
      type: 'media_state',
      talking: talkingRef.current,
      video: sourceRef.current,
    });
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
        setCanControl(msg.can_control === true);
        setFloor((msg.floor as Floor) ?? 'free');
        setDisplayModeState(msg.display_mode === 'vnc' ? 'vnc' : 'robot');
      } else if (msg.type === 'screen_ack') {
        setLastAckTs(typeof msg.ts === 'number' ? msg.ts : null);
      } else if (msg.type === 'question_dismissed') {
        setQuestion((q) => (q && q.id === Number(msg.id) ? null : q));
      } else if (msg.type === 'question_status') {
        setQuestion({
          id: Number(msg.id),
          text: String(msg.text ?? ''),
          options: Array.isArray(msg.options) ? msg.options.map(String) : [],
          status: msg.status as QuestionStatus['status'],
          answer: typeof msg.answer === 'number' ? msg.answer : null,
          remainingS: typeof msg.remaining_s === 'number' ? msg.remaining_s : null,
          receivedAt: Date.now(),
        });
      } else if (msg.type === 'voice_status') {
        setVoice({
          id: typeof msg.id === 'number' ? msg.id : null,
          hasClip: msg.has_clip === true,
          playing: msg.playing === true,
          durationS: typeof msg.duration_s === 'number' ? msg.duration_s : null,
        });
      } else if (msg.type === 'floor_denied') {
        setError('Another operator is using the robot screen.');
      } else if (msg.type === 'view_only') {
        setError('View only: enter the controller key to talk to the victim.');
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
      micGeneration.current++;
      micRequest.current = null;
      micRef.current?.stop();
      micRef.current = null;
      setMicReady(false);
      stopVideoTrack();
      talkingRef.current = false;
      sourceRef.current = 'none';
      setTalking(false);
      setVideoSource('none');
      setScreenOnline(false);
      setCanControl(false);
      setFloor('free');
      setDisplayModeState('robot');
      setLastAckTs(null);
      setQuestion(null);
    };
  }, [link, stopVideoTrack]);

  // Opens the laptop mic (muted) and attaches it to the connection. Only
  // one request runs at a time.
  const acquireMic = useCallback(() => {
    if (!link) return Promise.resolve();
    if (!micRequest.current) {
      const generation = micGeneration.current;
      micRequest.current = (async () => {
        try {
          const stream = await navigator.mediaDevices.getUserMedia({
            audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true },
          });
          const track = stream.getAudioTracks()[0];
          if (generation !== micGeneration.current) {
            track.stop();
            return;
          }
          track.enabled = false;
          micRef.current = track;
          await link.audioSender.replaceTrack(track);
          setMicReady(true);
        } catch (err) {
          if (generation === micGeneration.current) micRequest.current = null;
          throw err;
        }
      })();
    }
    return micRequest.current;
  }, [link]);

  // If the browser already allows the mic, open it as soon as the link is
  // up, so the very first press talks instead of waiting on getUserMedia.
  useEffect(() => {
    if (!link || !mediaDevicesAvailable || !navigator.permissions) return;
    navigator.permissions
      .query({ name: 'microphone' as PermissionName })
      .then((status) => {
        if (status.state === 'granted') return acquireMic();
      })
      .catch(() => {}); // unsupported query or mic failure: the first press will ask
  }, [link, mediaDevicesAvailable, acquireMic]);

  const startTalking = useCallback(async () => {
    if (!link) return;
    if (!mediaDevicesAvailable) {
      setError('Microphone needs HTTPS or the Chrome insecure-origin flag.');
      return;
    }
    setError(null);
    if (!micRef.current) {
      // The permission prompt takes focus from the button and cancels the
      // hold, so this press only enables the mic; the next one talks.
      try {
        await acquireMic();
      } catch (err) {
        setError(err instanceof Error ? `Microphone: ${err.message}` : 'Microphone unavailable');
      }
      return;
    }
    talkingRef.current = true;
    setTalking(true);
    micRef.current.enabled = true;
    sendMediaState();
  }, [link, mediaDevicesAvailable, acquireMic, sendMediaState]);

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

  const askQuestion = useCallback(
    (text: string, options: string[]) => {
      const q = text.trim().slice(0, SCREEN_TEXT_MAX);
      const opts = options.map((o) => o.trim().slice(0, QUESTION_OPTION_MAX)).filter(Boolean);
      if (!q || opts.length < QUESTION_OPTIONS_MIN || opts.length > QUESTION_OPTIONS_MAX) return false;
      setError(null);
      return send({ type: 'question_ask', text: q, options: opts });
    },
    [send],
  );

  const clearQuestion = useCallback(() => {
    send({ type: 'question_clear' });
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

  // No optimistic update: the radio follows P2's talk_status, so it only
  // shows a mode the robot has actually switched to.
  const setDisplayMode = useCallback(
    (mode: DisplayMode) => {
      if (!send({ type: 'display_mode', mode })) setError('Not connected to the robot.');
    },
    [send],
  );

  const sendVoiceCommand = useCallback(
    (command: VoiceCommand) => {
      const sent = send({ type: command });
      if (!sent) setError('Not connected to the robot.');
      return sent;
    },
    [send],
  );

  return {
    mediaDevicesAvailable,
    screenOnline,
    canControl,
    floor,
    displayMode,
    talking,
    micReady,
    videoSource,
    previewStream,
    lastAckTs,
    question,
    voice,
    error,
    startTalking: () => void startTalking(),
    stopTalking,
    showVideo: (source, image) => void showVideo(source, image),
    sendText,
    clearText,
    askQuestion,
    clearQuestion,
    release,
    setDisplayMode,
    sendVoiceCommand,
    setError,
  };
}
