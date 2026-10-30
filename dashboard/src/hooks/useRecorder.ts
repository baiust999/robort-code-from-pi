import { useCallback, useEffect, useRef, useState } from 'react';
import type { TalkLink } from './useWebrtcVideo';
import { download } from '../lib/download';
import { withDuration } from '../lib/fixDuration';
import {
  appendChunk,
  assembleRecording,
  deleteRecording,
  listRecordings,
  putMeta,
  type RecordingMeta,
} from '../lib/recordingStore';

/** MediaRecorder emits a chunk this often; also the most a crash can lose. */
const CHUNK_MS = 1000;
/** replaceTrack() fires no event, so the outgoing audio track is polled. */
const SENDER_POLL_MS = 250;
/**
 * How long the video may be down before the recording is ended and saved.
 * Short Wi-Fi drops recover by themselves and shouldn't split the recording.
 */
const RECONNECT_GRACE_MS = 15_000;
/**
 * Most playable first: MP4 with H.264 and AAC plays almost everywhere (Chrome
 * and Edge on Windows and Mac); then MP4 with Opus audio (Chromium without
 * AAC); WebM only where MP4 can't be recorded.
 */
const MIME_TYPES = [
  'video/mp4;codecs=avc1.42E01E,mp4a.40.2',
  'video/mp4;codecs=avc1,mp4a',
  'video/mp4;codecs=avc1,opus',
  'video/webm;codecs=vp8,opus',
  'video/webm',
  'video/mp4',
];

export interface RecorderState {
  supported: boolean;
  recording: boolean;
  elapsedMs: number;
  sizeBytes: number;
  /** False when this browser refused IndexedDB: a crash would lose the recording. */
  crashSafe: boolean;
  /** Last outcome or problem, shown under the video. */
  message: string | null;
  start: () => void;
  stop: () => void;
  /** Recordings kept in this browser, including any a crash cut off. */
  saved: RecordingMeta[];
  /** Downloads a kept recording again; a click, so the browser lets it through. */
  save: (meta: RecordingMeta) => void;
  remove: (meta: RecordingMeta) => void;
}

const fileName = (meta: RecordingMeta) =>
  `robot-session-${new Date(meta.startedAt).toISOString().replace(/[:.]/g, '-')}.${
    meta.mimeType.includes('mp4') ? 'mp4' : 'webm'
  }`;

/**
 * Records the session to this device: the robot's camera, with the robot's
 * mic and the operator's outgoing audio (talk-back mic or call-out clip)
 * mixed into one track. The mix reads whatever is on the audio sender, so
 * the recording holds what the robot actually played.
 *
 * Chunks go to IndexedDB as they arrive, and the file is downloaded on stop.
 * The browser may hold that download back, so the recording stays in
 * IndexedDB, listed for a click-to-save, until the operator deletes it.
 * Recording carries on through a short drop; if the video stays down past
 * RECONNECT_GRACE_MS, or the connection is replaced (a reconnect makes a new
 * stream), it stops and saves rather than continuing on a dead track.
 */
export function useRecorder(
  remoteStream: MediaStream | null,
  talkLink: TalkLink | null,
  connected: boolean,
): RecorderState {
  const supported = typeof MediaRecorder !== 'undefined';
  const [recording, setRecording] = useState(false);
  const [elapsedMs, setElapsedMs] = useState(0);
  const [sizeBytes, setSizeBytes] = useState(0);
  const [crashSafe, setCrashSafe] = useState(true);
  const [message, setMessage] = useState<string | null>(null);
  const [saved, setSaved] = useState<RecordingMeta[]>([]);

  // Ends the recording in progress; the argument says why, for the message.
  const stopRef = useRef<((reason?: string) => void) | null>(null);
  const talkLinkRef = useRef(talkLink);
  talkLinkRef.current = talkLink;

  useEffect(() => {
    listRecordings().then(setSaved, () => {});
  }, []);

  const start = useCallback(() => {
    if (!supported || stopRef.current || !remoteStream) return;
    const video = remoteStream.getVideoTracks()[0];
    if (!video || video.readyState === 'ended') {
      setMessage('No robot video to record');
      return;
    }
    setMessage(null);

    const ctx = new AudioContext();
    const mix = ctx.createMediaStreamDestination();
    const robotAudio = remoteStream.getAudioTracks()[0];
    if (robotAudio) ctx.createMediaStreamSource(new MediaStream([robotAudio])).connect(mix);

    let sentTrack: MediaStreamTrack | null = null;
    let sentNode: MediaStreamAudioSourceNode | null = null;
    const followSender = () => {
      const track = talkLinkRef.current?.audioSender.track ?? null;
      if (track === sentTrack) return;
      sentNode?.disconnect();
      sentNode = null;
      sentTrack = track;
      if (track && track.readyState === 'live') {
        sentNode = ctx.createMediaStreamSource(new MediaStream([track]));
        sentNode.connect(mix);
      }
    };
    followSender();
    const poll = setInterval(followSender, SENDER_POLL_MS);

    const mimeType = MIME_TYPES.find((t) => MediaRecorder.isTypeSupported(t));
    const rec = new MediaRecorder(new MediaStream([video, ...mix.stream.getAudioTracks()]), {
      ...(mimeType ? { mimeType } : {}),
      // Chrome's MP4 writes data only at keyframes, which from a camera can
      // be minutes apart: without this a crash could lose the whole
      // recording. Browsers without the option ignore it.
      videoKeyFrameIntervalDuration: CHUNK_MS,
    } as MediaRecorderOptions);
    const meta: RecordingMeta = {
      id: crypto.randomUUID(),
      startedAt: Date.now(),
      mimeType: rec.mimeType,
      finished: false,
    };
    const chunks: Blob[] = [];
    let size = 0;
    let stored = putMeta(meta).then(() => true, () => false);
    stored.then(setCrashSafe);

    // The media starts when the recorder does, not at the click.
    let mediaStart = meta.startedAt;
    rec.onstart = () => {
      mediaStart = Date.now();
    };

    rec.ondataavailable = (e) => {
      if (!e.data.size) return;
      const seq = chunks.length;
      chunks.push(e.data);
      size += e.data.size;
      setSizeBytes(size);
      // Chained so chunks land in order and the finished mark comes last.
      stored = stored.then((ok) =>
        ok ? appendChunk(meta.id, seq, e.data, Date.now() - mediaStart).then(() => true, () => false) : false,
      );
      stored.then((ok) => { if (!ok) setCrashSafe(false); });
    };

    let stopReason: string | undefined;
    rec.onstop = () => {
      clearInterval(poll);
      clearInterval(clock);
      ctx.close().catch(() => {});
      setRecording(false);
      if (!chunks.length) {
        setMessage('Recording was empty, nothing saved');
        stored.then(() => deleteRecording(meta.id)).catch(() => {});
        return;
      }
      const durationMs = Date.now() - mediaStart;
      withDuration(new Blob(chunks, { type: meta.mimeType }), durationMs).then((file) => download(file, fileName(meta)));
      setMessage(`Recording saved${stopReason ? ` (${stopReason})` : ''}: ${fileName(meta)}`);
      const done = { ...meta, finished: true, durationMs };
      stored.then((ok) => {
        // A partial copy (storage failed midway) would later pass for a
        // crashed recording; the full file was just downloaded, so drop it.
        if (!ok) {
          deleteRecording(meta.id).catch(() => {});
          return;
        }
        putMeta(done).catch(() => {});
        setSaved((list) => [...list, done]);
      });
    };

    const clock = setInterval(() => setElapsedMs(Date.now() - meta.startedAt), 500);
    stopRef.current = (reason) => {
      stopRef.current = null;
      stopReason = reason;
      if (rec.state !== 'inactive') rec.stop();
    };
    try {
      rec.start(CHUNK_MS);
    } catch (err) {
      stopRef.current = null;
      clearInterval(poll);
      clearInterval(clock);
      ctx.close().catch(() => {});
      stored.then(() => deleteRecording(meta.id)).catch(() => {});
      setMessage(`Could not start recording: ${err instanceof Error ? err.message : err}`);
      return;
    }
    setElapsedMs(0);
    setSizeBytes(0);
    setRecording(true);
  }, [supported, remoteStream]);

  const stop = useCallback(() => stopRef.current?.(), []);

  // The robot's stream is replaced on reconnect; a recording can't follow it.
  useEffect(() => () => stopRef.current?.('video connection lost'), [remoteStream]);
  useEffect(() => {
    if (connected || !recording) return;
    const timer = setTimeout(() => stopRef.current?.('video connection lost'), RECONNECT_GRACE_MS);
    return () => clearTimeout(timer);
  }, [connected, recording]);

  const save = useCallback((meta: RecordingMeta) => {
    assembleRecording(meta)
      .then((blob) => {
        if (blob) download(blob, fileName(meta));
        else setMessage('That recording is empty');
      })
      .catch(() => setMessage('Could not read the recording'));
  }, []);

  const remove = useCallback((meta: RecordingMeta) => {
    deleteRecording(meta.id).catch(() => {});
    setSaved((list) => list.filter((m) => m.id !== meta.id));
  }, []);

  return { supported, recording, elapsedMs, sizeBytes, crashSafe, message, start, stop, saved, save, remove };
}
