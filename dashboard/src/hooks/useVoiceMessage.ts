import { useCallback, useEffect, useRef, useState } from 'react';
import { uploadVoice } from '../lib/api';
import type { TalkbackState } from './useTalkback';

/** Recording stops by itself at this length; P2 accepts a little more. */
export const VOICE_MAX_S = 30;

export interface VoiceMessageState {
  recording: boolean;
  /** Seconds recorded so far, while recording. */
  elapsedS: number;
  /** Object URL of this browser's recording, for the preview player. */
  previewUrl: string | null;
  /** The robot holds the recording made here (not an older or another operator's). */
  uploaded: boolean;
  busy: boolean;
  startRecording: () => void;
  stopRecording: () => void;
  startPlay: () => void;
  stopPlay: () => void;
  clear: () => void;
}

function pickMimeType(): string | undefined {
  for (const type of ['audio/webm;codecs=opus', 'audio/ogg;codecs=opus', 'audio/webm', 'audio/mp4']) {
    if (typeof MediaRecorder !== 'undefined' && MediaRecorder.isTypeSupported(type)) return type;
  }
  return undefined;
}

/**
 * A voice message the robot repeats until told to stop (e.g. while driving to
 * a victim). It is recorded here, uploaded to P2 once, and looped by P2 on the
 * robot speaker, so playback doesn't depend on this dashboard staying
 * connected. Start/stop/clear go over the talk data channel.
 */
export function useVoiceMessage(talk: TalkbackState, controllerKey: string | null): VoiceMessageState {
  const [recording, setRecording] = useState(false);
  const [elapsedS, setElapsedS] = useState(0);
  const [clip, setClip] = useState<Blob | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  // P2's id for the upload of `clip`; compared with talk.voice.id.
  const [uploadedId, setUploadedId] = useState<number | null>(null);
  const [busy, setBusy] = useState(false);

  const recorderRef = useRef<MediaRecorder | null>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const { setError, sendVoiceCommand, voice } = talk;

  useEffect(() => {
    if (!clip) {
      setPreviewUrl(null);
      return;
    }
    const url = URL.createObjectURL(clip);
    setPreviewUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [clip]);

  const stopRecording = useCallback(() => {
    if (recorderRef.current?.state === 'recording') recorderRef.current.stop();
  }, []);

  // Never leave the mic open after the panel goes away.
  useEffect(
    () => () => {
      if (timerRef.current !== null) clearInterval(timerRef.current);
      const rec = recorderRef.current;
      if (rec && rec.state !== 'inactive') rec.stop();
      rec?.stream.getTracks().forEach((t) => t.stop());
    },
    [],
  );

  const startRecording = useCallback(async () => {
    if (recorderRef.current?.state === 'recording') return;
    setError(null);
    let stream: MediaStream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({
        audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true },
      });
    } catch {
      setError('Voice message: microphone not available.');
      return;
    }
    const mimeType = pickMimeType();
    const recorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined);
    const chunks: Blob[] = [];
    const started = Date.now();
    recorder.ondataavailable = (e) => {
      if (e.data.size > 0) chunks.push(e.data);
    };
    recorder.onstop = () => {
      stream.getTracks().forEach((t) => t.stop());
      if (timerRef.current !== null) clearInterval(timerRef.current);
      timerRef.current = null;
      recorderRef.current = null;
      setRecording(false);
      if (Date.now() - started < 500 || chunks.length === 0) {
        setError('Voice message too short; hold on and speak, then press Stop.');
        return;
      }
      setClip(new Blob(chunks, { type: recorder.mimeType || mimeType || 'audio/webm' }));
      setUploadedId(null);
    };
    recorderRef.current = recorder;
    recorder.start();
    setElapsedS(0);
    setRecording(true);
    timerRef.current = setInterval(() => {
      const s = (Date.now() - started) / 1000;
      setElapsedS(Math.floor(s));
      if (s >= VOICE_MAX_S) stopRecording();
    }, 250);
  }, [setError, stopRecording]);

  const uploaded = clip !== null && uploadedId !== null && voice?.id === uploadedId;

  const startPlay = useCallback(async () => {
    setError(null);
    if (!uploaded) {
      if (!clip) {
        // Nothing recorded here: replay what the robot already holds, if anything.
        if (voice?.hasClip) sendVoiceCommand('voice_loop_start');
        return;
      }
      setBusy(true);
      try {
        const { id } = await uploadVoice(controllerKey, clip);
        setUploadedId(id);
      } catch (err) {
        setError(`Voice message: ${err instanceof Error ? err.message : 'upload failed'}`);
        return;
      } finally {
        setBusy(false);
      }
    }
    sendVoiceCommand('voice_loop_start');
  }, [clip, controllerKey, sendVoiceCommand, setError, uploaded, voice?.hasClip]);

  const stopPlay = useCallback(() => {
    sendVoiceCommand('voice_loop_stop');
  }, [sendVoiceCommand]);

  const clear = useCallback(() => {
    stopRecording();
    setClip(null);
    setUploadedId(null);
    if (voice?.hasClip) sendVoiceCommand('voice_clear');
  }, [sendVoiceCommand, stopRecording, voice?.hasClip]);

  return {
    recording,
    elapsedS,
    previewUrl,
    uploaded,
    busy,
    startRecording: () => void startRecording(),
    stopRecording,
    startPlay: () => void startPlay(),
    stopPlay,
    clear,
  };
}
