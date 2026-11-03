import type { PersonBox } from '../hooks/usePersonDetection';
import { download } from './download';

/*
 * E18 evaluation capture (tools/eval/README.md).
 *
 * The detector runs in this browser, so the only place its real output exists
 * is here. This module writes one frame and the boxes that detector returned
 * on that same frame to the operator's Downloads folder, where
 * tools/eval/detector_import.py picks them up. It exists so that the E18
 * numbers come from the deployed detector rather than from a second copy of
 * the model run offline, which would be a different measurement.
 *
 * It is off unless the operator asks for it (`?evalcapture=1` once, or
 * localStorage robot.evalCapture = 'on'), so the shipped dashboard an operator
 * drives is unchanged: no extra button, no extra work per frame.
 *
 * The frame is written without the box overlay drawn on it. The annotator has
 * to draw ground truth on a clean frame; a frame with the detector's own boxes
 * burnt in would tell them the answer.
 */

const ENABLED_KEY = 'robot.evalCapture';
const JPEG_QUALITY = 0.92;
export const EXPORT_SCHEMA = 'robot-e18-detector-export/1';

/** The detector as it is configured in usePersonDetection.ts. */
export interface DetectorInfo {
  model_name: string;
  /** Keep in step with @mediapipe/tasks-vision in dashboard/package.json. */
  model_version: string;
  delegate: string;
  score_threshold: number;
  max_results: number;
  category_allowlist: string[];
}

export interface EvalCapture {
  boxes: PersonBox[];
  inferMs: number;
  videoWidth: number;
  videoHeight: number;
  /** The video's own timestamp for the frame the detector ran on. */
  currentTimeS: number;
  detector: DetectorInfo;
  frame: Blob | null;
}

/** True when this browser has been put into E18 capture mode. */
export function evalCaptureEnabled(): boolean {
  try {
    if (new URLSearchParams(window.location.search).get('evalcapture') === '1') {
      localStorage.setItem(ENABLED_KEY, 'on');
      return true;
    }
    return localStorage.getItem(ENABLED_KEY) === 'on';
  } catch {
    return false;
  }
}

/** A frame id that sorts chronologically and is safe in a file name. */
export function frameId(at: Date = new Date()): string {
  return `e18-${at.toISOString().replace(/[-:]/g, '').replace('.', '')}`;
}

/** The frame the detector just ran on, as a JPEG, with no overlay drawn. */
export async function captureCleanFrame(video: HTMLVideoElement): Promise<Blob | null> {
  if (!video.videoWidth) return null;
  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext('2d');
  if (!ctx) return null;
  ctx.drawImage(video, 0, 0);
  return new Promise<Blob | null>((resolve) => canvas.toBlob(resolve, 'image/jpeg', JPEG_QUALITY));
}

/**
 * The record detector_import.py reads. Coordinates are converted from the
 * detector's (originX, originY, width, height) to (x_min, y_min, x_max, y_max)
 * here, in the video's own pixel space, which is the space the exported JPEG
 * is written in, so the annotator and the detector share one coordinate frame.
 */
export function exportRecord(id: string, capture: EvalCapture, at: Date = new Date()) {
  return {
    schema: EXPORT_SCHEMA,
    frame_id: id,
    image_file: `${id}.jpg`,
    captured_utc: at.toISOString(),
    video: {
      width: capture.videoWidth,
      height: capture.videoHeight,
      current_time_s: Number(capture.currentTimeS.toFixed(3)),
    },
    detector: capture.detector,
    infer_ms: Number(capture.inferMs.toFixed(1)),
    n_boxes: capture.boxes.length,
    predictions: capture.boxes.map((box, index) => ({
      pred_id: `p${index + 1}`,
      x_min: Number(box.x.toFixed(2)),
      y_min: Number(box.y.toFixed(2)),
      x_max: Number((box.x + box.width).toFixed(2)),
      y_max: Number((box.y + box.height).toFixed(2)),
      confidence: Number(box.score.toFixed(4)),
    })),
    frame_written: capture.frame !== null,
    user_agent: typeof navigator === 'undefined' ? '' : navigator.userAgent,
  };
}

/**
 * Writes the frame and its record to Downloads. Both carry the same frame id,
 * so a lost half is obvious: the importer rejects a record whose image is
 * missing rather than scoring a prediction against a frame nobody can see.
 */
export function downloadEvalCapture(capture: EvalCapture, at: Date = new Date()): string {
  const id = frameId(at);
  const record = exportRecord(id, capture, at);
  if (capture.frame) download(capture.frame, `${id}.jpg`);
  download(new Blob([JSON.stringify(record, null, 2)], { type: 'application/json' }), `${id}.json`);
  return id;
}
