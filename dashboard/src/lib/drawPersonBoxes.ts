import type { PersonBox } from '../hooks/usePersonDetection';

/** At or above this score the box is red (strong); below it, orange (weak: take a closer look). */
const STRONG_SCORE = 0.7;
const STRONG_COLOR = '#ef4444';
const WEAK_COLOR = '#f97316';

/** Draws person boxes, given in video pixels, scaled by `scale` and shifted by (dx, dy). */
export function drawPersonBoxes(
  ctx: CanvasRenderingContext2D,
  boxes: PersonBox[],
  scale: number,
  dx: number,
  dy: number,
) {
  ctx.lineWidth = 2;
  ctx.font = '600 13px system-ui, sans-serif';
  ctx.textBaseline = 'top';
  for (const b of boxes) {
    const color = b.score >= STRONG_SCORE ? STRONG_COLOR : WEAK_COLOR;
    const x = dx + b.x * scale;
    const y = dy + b.y * scale;
    ctx.strokeStyle = color;
    ctx.strokeRect(x, y, b.width * scale, b.height * scale);
    const label = `Person ${Math.round(b.score * 100)}%`;
    const labelY = Math.max(0, y - 18);
    ctx.fillStyle = color;
    ctx.fillRect(x, labelY, ctx.measureText(label).width + 8, 18);
    ctx.fillStyle = '#fff';
    ctx.fillText(label, x + 4, labelY + 2);
  }
}
