// Copies MediaPipe's WASM runtime into public/ so person detection works
// with no internet: the dashboard must not load it from a CDN in the field.
import { cpSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const target = join(root, 'public', 'mediapipe', 'wasm');
mkdirSync(target, { recursive: true });
cpSync(join(root, 'node_modules', '@mediapipe', 'tasks-vision', 'wasm'), target, { recursive: true });
