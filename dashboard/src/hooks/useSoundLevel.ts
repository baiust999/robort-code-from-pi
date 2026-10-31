import { useEffect, useState } from 'react';

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
      setLevelDb(LEVEL_FLOOR_DB);
      setPeakDb(LEVEL_FLOOR_DB);
      setNeedsGesture(false);
    };
  }, [connected, videoRef, retry]);

  return { levelDb, peakDb, needsGesture };
}
