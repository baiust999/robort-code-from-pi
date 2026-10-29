import { useCallback, useEffect, useRef, useState } from 'react';
import type { ObjectDetector } from '@mediapipe/tasks-vision';

/** 5 Hz: half the camera's 10 FPS, so the laptop isn't busy on repeated frames. */
const DETECT_INTERVAL_MS = 200;
const SCORE_THRESHOLD = 0.4;
/** Frames in a row needed to raise, and to clear, "possible person", against flicker. */
const FRAMES_TO_RAISE = 3;
const FRAMES_TO_CLEAR = 5;
const ENABLED_KEY = 'robot.personDetection';
/**
 * Detection runs on the page's main thread, so a slow computer would make the
 * drive and stop buttons lag. Past this many ms per frame, averaged over
 * SLOW_FRAMES frames (after the first, which includes warm-up), it turns off.
 */
const SLOW_FRAME_MS = 150;
const SLOW_FRAMES = 5;

// Bundled under public/ (see scripts/copy-mediapipe.mjs): the field may have no internet.
const WASM_PATH = `${import.meta.env.BASE_URL}mediapipe/wasm`;
const MODEL_PATH = `${import.meta.env.BASE_URL}models/efficientdet_lite0.tflite`;

/** One person box in the video's own pixel coordinates. */
export interface PersonBox {
  x: number;
  y: number;
  width: number;
  height: number;
  score: number;
}

export interface PersonDetectionState {
  enabled: boolean;
  setEnabled: (on: boolean) => void;
  /** The model has loaded and detection can run. */
  ready: boolean;
  error: string | null;
  boxes: PersonBox[];
  /** A person was seen in several frames in a row; cleared after several without. */
  personPresent: boolean;
  /** Best score in the latest frame, or null with no person. */
  bestScore: number | null;
}

function loadEnabled(): boolean {
  try {
    return localStorage.getItem(ENABLED_KEY) !== 'off';
  } catch {
    return true;
  }
}

/**
 * The WebGL renderer, or null without WebGL. MediaPipe needs WebGL even with
 * the CPU delegate: without it the model loads, then every frame fails with
 * "reading 'activeTexture'".
 */
function webglRenderer(): string | null {
  const gl = document.createElement('canvas').getContext('webgl');
  if (!gl) return null;
  const info = gl.getExtension('WEBGL_debug_renderer_info');
  return String(gl.getParameter(info ? info.UNMASKED_RENDERER_WEBGL : gl.RENDERER));
}

async function createDetector(): Promise<ObjectDetector> {
  const renderer = webglRenderer();
  if (renderer === null) throw new Error('AI needs WebGL, which this browser has turned off or lacks');
  // On a software renderer the GPU delegate compiles its shaders on the page's
  // main thread for minutes, freezing the controls; the CPU delegate doesn't.
  const softwareGl = /swiftshader|llvmpipe|software/i.test(renderer);

  // Loaded on first use: it is most of the dashboard's size.
  const { FilesetResolver, ObjectDetector } = await import('@mediapipe/tasks-vision');
  const fileset = await FilesetResolver.forVisionTasks(WASM_PATH);
  const options = (delegate: 'GPU' | 'CPU') => ({
    baseOptions: { modelAssetPath: MODEL_PATH, delegate },
    runningMode: 'VIDEO' as const,
    scoreThreshold: SCORE_THRESHOLD,
    maxResults: 5,
    categoryAllowlist: ['person'],
  });
  if (!softwareGl) {
    try {
      return await ObjectDetector.createFromOptions(fileset, options('GPU'));
    } catch {
      // GPU delegate unavailable: fall through to the slower CPU one.
    }
  }
  return ObjectDetector.createFromOptions(fileset, options('CPU'));
}

/**
 * Person detection on the robot video, run in the operator's browser so the
 * Pi spends nothing on it. It only helps the operator look: it misses people
 * who are covered, lying down or in the dark.
 */
export function usePersonDetection(
  videoRef: React.RefObject<HTMLVideoElement | null>,
  active: boolean,
): PersonDetectionState {
  const [enabled, setEnabledState] = useState(loadEnabled);
  const [ready, setReady] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [boxes, setBoxes] = useState<PersonBox[]>([]);
  const [personPresent, setPersonPresent] = useState(false);
  const [bestScore, setBestScore] = useState<number | null>(null);
  const detectorRef = useRef<ObjectDetector | null>(null);

  const setEnabled = useCallback((on: boolean) => {
    setEnabledState(on);
    // Turning it back on tries again; a lasting problem reports itself again.
    if (on) setError(null);
    try {
      localStorage.setItem(ENABLED_KEY, on ? 'on' : 'off');
    } catch {
      // storage blocked: the choice just isn't remembered
    }
  }, []);

  // Load the model the first time detection is wanted, and keep it.
  useEffect(() => {
    if (!enabled || detectorRef.current) return;
    let cancelled = false;
    createDetector()
      .then((detector) => {
        if (cancelled) {
          detector.close();
          return;
        }
        detectorRef.current = detector;
        setReady(true);
      })
      .catch((err: unknown) => {
        if (!cancelled) setError(err instanceof Error ? err.message : 'could not load the AI model');
      });
    return () => {
      cancelled = true;
    };
  }, [enabled]);

  useEffect(() => () => detectorRef.current?.close(), []);

  useEffect(() => {
    const clear = () => {
      setBoxes([]);
      setPersonPresent(false);
      setBestScore(null);
    };
    if (!enabled || !active || !ready) {
      clear();
      return;
    }
    let timer: ReturnType<typeof setTimeout> | null = null;
    let lastFrameTime = -1;
    let hits = 0;
    let misses = 0;
    let present = false;
    let timedFrames: number[] = [];
    let firstFrame = true;

    const tick = () => {
      const video = videoRef.current;
      const detector = detectorRef.current;
      if (!video || !detector || document.hidden) {
        timer = setTimeout(tick, DETECT_INTERVAL_MS);
        return;
      }
      if (video.readyState < 2 || video.videoWidth === 0 || video.currentTime === lastFrameTime) {
        timer = setTimeout(tick, DETECT_INTERVAL_MS);
        return;
      }
      lastFrameTime = video.currentTime;

      let found: PersonBox[];
      const started = performance.now();
      try {
        found = detector.detectForVideo(video, performance.now()).detections.flatMap((d) =>
          d.boundingBox
            ? [
                {
                  x: d.boundingBox.originX,
                  y: d.boundingBox.originY,
                  width: d.boundingBox.width,
                  height: d.boundingBox.height,
                  score: d.categories[0]?.score ?? 0,
                },
              ]
            : [],
        );
      } catch (err) {
        // Stops here; turning AI off and on again retries.
        setError(`AI stopped: ${err instanceof Error ? err.message : 'detection failed'}`);
        clear();
        return;
      }
      const took = performance.now() - started;
      if (!firstFrame) timedFrames = [...timedFrames.slice(1 - SLOW_FRAMES), took];
      firstFrame = false;
      const average = timedFrames.reduce((a, b) => a + b, 0) / timedFrames.length;
      if (timedFrames.length >= SLOW_FRAMES && average > SLOW_FRAME_MS) {
        setError(`AI turned off: too slow on this computer (${Math.round(average)} ms a frame); the controls must stay responsive`);
        setEnabled(false);
        return;
      }
      // Leave the main thread free at least half the time.
      timer = setTimeout(tick, Math.max(DETECT_INTERVAL_MS, 2 * took));

      if (found.length > 0) {
        hits += 1;
        misses = 0;
      } else {
        misses += 1;
        hits = 0;
      }
      if (!present && hits >= FRAMES_TO_RAISE) present = true;
      if (present && misses >= FRAMES_TO_CLEAR) present = false;

      // No one in view, frame after frame: keep the same array so nothing re-renders.
      setBoxes((prev) => (found.length === 0 && prev.length === 0 ? prev : found));
      setPersonPresent(present);
      setBestScore(found.length > 0 ? Math.max(...found.map((b) => b.score)) : null);
    };
    tick();
    return () => {
      if (timer !== null) clearTimeout(timer);
      clear();
    };
  }, [enabled, active, ready, videoRef, setEnabled]);

  return { enabled, setEnabled, ready, error, boxes, personPresent, bestScore };
}
