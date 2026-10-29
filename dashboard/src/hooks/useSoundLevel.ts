import { useEffect, useRef, useState } from 'react';

const SAMPLE_MS = 100;
/**
 * The meter redraws at most this often, showing the loudest sample since the
 * last redraw, so a short knock still shows. Redrawing on every sample cost
 * the dashboard about as much as everything else on the page put together.
 */
const DISPLAY_MS = 250;
/** Skip a redraw that would move the meter by less than this. */
const DISPLAY_STEP_DB = 1;
/** The quietest level shown; silence reads as this, not -Infinity. */
export const LEVEL_FLOOR_DB = -80;
/** How fast the peak tick falls back, in dB per second. */
const PEAK_DECAY_DB_PER_S = 10;

export interface SoundLevelState {
  /** Robot mic loudness in dBFS, the loudest of the last 250 ms; LEVEL_FLOOR_DB when silent. */
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
    let loudest = LEVEL_FLOOR_DB;
    let shownLevel = LEVEL_FLOOR_DB;
    let shownPeak = LEVEL_FLOOR_DB;
    let lastShown = 0;

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

      loudest = Math.max(loudest, db);
      const now = performance.now();
      if (now - lastShown < DISPLAY_MS) return;
      lastShown = now;
      if (Math.abs(loudest - shownLevel) >= DISPLAY_STEP_DB || Math.abs(peak - shownPeak) >= DISPLAY_STEP_DB) {
        shownLevel = loudest;
        shownPeak = peak;
        setLevelDb(loudest);
        setPeakDb(peak);
      }
      loudest = LEVEL_FLOOR_DB;
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

/** Without a baseline from before the call-out, judge only after this many meter updates (over 1 s). */
const MIN_WINDOW_SAMPLES = 5;

/**
 * After a call-out, watches the robot mic for a reply: anything REPLY_RISE_DB
 * louder than the 2 s before the call-out. If there was no sound before it
 * (the meter only starts once the page has been clicked, and the call-out
 * click may be the first), the quietest moment of the window stands in.
 * Nothing is judged while the clip plays, since the robot mic hears its own
 * speaker.
 */
export function useReplyListener(
  callingOut: boolean,
  sound: SoundLevelState,
  onReply: (riseDb: number) => void,
): { listening: boolean } {
  const [listening, setListening] = useState(false);
  const baseline = useRef<number | null>(null);
  const windowMin = useRef(Infinity);
  const windowSamples = useRef(0);
  const until = useRef(0);
  const replied = useRef(false);
  const wasCalling = useRef(false);
  const onReplyRef = useRef(onReply);
  useEffect(() => {
    onReplyRef.current = onReply;
  }, [onReply]);

  useEffect(() => {
    if (callingOut && !wasCalling.current) {
      const recent = sound.history.current.slice(-BASELINE_SAMPLES);
      baseline.current = recent.length > 0 ? median(recent) : null;
      setListening(false);
    } else if (!callingOut && wasCalling.current) {
      until.current = Date.now() + LISTEN_WINDOW_MS;
      replied.current = false;
      windowMin.current = Infinity;
      windowSamples.current = 0;
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
    windowSamples.current += 1;
    windowMin.current = Math.min(windowMin.current, sound.levelDb);
    let reference = baseline.current;
    if (reference === null) {
      if (windowSamples.current < MIN_WINDOW_SAMPLES) return;
      reference = windowMin.current;
    }
    const rise = sound.levelDb - reference;
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
