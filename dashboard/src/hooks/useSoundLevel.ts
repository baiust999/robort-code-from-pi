import { useEffect, useRef, useState } from 'react';

const SAMPLE_MS = 100;
/** The quietest level shown; silence reads as this, not -Infinity. */
export const LEVEL_FLOOR_DB = -80;
/** How fast the peak tick falls back, in dB per second. */
const PEAK_DECAY_DB_PER_S = 10;

export interface SoundLevelState {
  /** Robot mic loudness in dBFS, sampled every 100 ms; LEVEL_FLOOR_DB when silent. */
  levelDb: number;
  peakDb: number;
  /** The browser holds audio until the operator clicks somewhere on the page. */
  needsGesture: boolean;
  /** Recent levels, newest last, for baselines (about the last 5 s). */
  history: React.RefObject<number[]>;
}

/**
 * Loudness of the robot microphone, from the audio track on the robot video
 * stream. It works while the operator has the robot mic muted, so a faint
 * knock still shows on the meter.
 */
export function useSoundLevel(
  videoRef: React.RefObject<HTMLVideoElement | null>,
  connected: boolean,
): SoundLevelState {
  const [levelDb, setLevelDb] = useState(LEVEL_FLOOR_DB);
  const [peakDb, setPeakDb] = useState(LEVEL_FLOOR_DB);
  const [needsGesture, setNeedsGesture] = useState(false);
  const history = useRef<number[]>([]);
  // Bumped to look again when the audio track hasn't arrived yet.
  const [retry, setRetry] = useState(0);

  useEffect(() => {
    if (!connected) return;
    const stream = videoRef.current?.srcObject;
    const track = stream instanceof MediaStream ? stream.getAudioTracks()[0] : undefined;
    if (!track) {
      const timer = setTimeout(() => setRetry((n) => n + 1), 500);
      return () => clearTimeout(timer);
    }

    const ctx = new AudioContext();
    const source = ctx.createMediaStreamSource(new MediaStream([track]));
    const analyser = ctx.createAnalyser();
    analyser.fftSize = 2048;
    source.connect(analyser);
    const samples = new Float32Array(analyser.fftSize);
    let peak = LEVEL_FLOOR_DB;

    // Chrome starts an AudioContext suspended until the page has been clicked.
    const resume = () => {
      ctx.resume().then(() => setNeedsGesture(ctx.state !== 'running')).catch(() => {});
    };
    setNeedsGesture(ctx.state !== 'running');
    resume();
    window.addEventListener('pointerdown', resume);

    const timer = setInterval(() => {
      if (ctx.state !== 'running') return;
      analyser.getFloatTimeDomainData(samples);
      let sum = 0;
      for (const s of samples) sum += s * s;
      const rms = Math.sqrt(sum / samples.length);
      const db = Math.max(LEVEL_FLOOR_DB, rms > 0 ? 20 * Math.log10(rms) : LEVEL_FLOOR_DB);
      peak = Math.max(db, peak - (PEAK_DECAY_DB_PER_S * SAMPLE_MS) / 1000);
      history.current.push(db);
      if (history.current.length > 50) history.current.shift();
      setLevelDb(db);
      setPeakDb(peak);
    }, SAMPLE_MS);

    return () => {
      clearInterval(timer);
      window.removeEventListener('pointerdown', resume);
      source.disconnect();
      ctx.close().catch(() => {});
      history.current = [];
      setLevelDb(LEVEL_FLOOR_DB);
      setPeakDb(LEVEL_FLOOR_DB);
      setNeedsGesture(false);
    };
  }, [connected, videoRef, retry]);

  return { levelDb, peakDb, needsGesture, history };
}

/** How long after a call-out to watch for a reply. */
const LISTEN_WINDOW_MS = 10_000;
/** Samples before the call-out used as the quiet baseline (2 s). */
const BASELINE_SAMPLES = 20;
/** A reply is this much louder than the baseline. A first guess: tune on the robot. */
export const REPLY_RISE_DB = 10;

function median(values: number[]): number {
  const sorted = [...values].sort((a, b) => a - b);
  return sorted[Math.floor(sorted.length / 2)];
}

/**
 * After a call-out, watches the robot mic for a reply: anything REPLY_RISE_DB
 * louder than the 2 s before the call-out. Nothing is judged while the clip
 * plays, since the robot mic hears its own speaker.
 */
export function useReplyListener(
  callingOut: boolean,
  sound: SoundLevelState,
  onReply: (riseDb: number) => void,
): { listening: boolean } {
  const [listening, setListening] = useState(false);
  const baseline = useRef<number | null>(null);
  const until = useRef(0);
  const replied = useRef(false);
  const wasCalling = useRef(false);
  const onReplyRef = useRef(onReply);
  onReplyRef.current = onReply;

  useEffect(() => {
    if (callingOut && !wasCalling.current) {
      const recent = sound.history.current.slice(-BASELINE_SAMPLES);
      baseline.current = recent.length > 0 ? median(recent) : null;
      setListening(false);
    } else if (!callingOut && wasCalling.current && baseline.current !== null) {
      until.current = Date.now() + LISTEN_WINDOW_MS;
      replied.current = false;
      setListening(true);
    }
    wasCalling.current = callingOut;
  }, [callingOut, sound.history]);

  useEffect(() => {
    if (!listening) return;
    if (Date.now() > until.current) {
      setListening(false);
      return;
    }
    const rise = sound.levelDb - (baseline.current ?? LEVEL_FLOOR_DB);
    if (!replied.current && rise >= REPLY_RISE_DB) {
      replied.current = true;
      onReplyRef.current(Math.round(rise));
    }
  }, [listening, sound.levelDb]);

  // levelDb may stop changing in total silence; end the window on time anyway.
  useEffect(() => {
    if (!listening) return;
    const timer = setTimeout(() => setListening(false), Math.max(0, until.current - Date.now()));
    return () => clearTimeout(timer);
  }, [listening]);

  return { listening };
}
