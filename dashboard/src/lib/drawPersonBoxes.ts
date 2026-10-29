import type { PersonBox } from '../hooks/usePersonDetection';

const BOX_COLOR = '#ef4444';

/** Draws person boxes, given in video pixels, scaled by `scale` and shifted by (dx, dy). */
export function drawPersonBoxes(
  ctx: CanvasRenderingContext2D,
  boxes: PersonBox[],
  scale: number,
  dx: number,
  dy: number,
) {
  ctx.lineWidth = 2;
  ctx.strokeStyle = BOX_COLOR;
  ctx.font = '600 13px system-ui, sans-serif';
  ctx.textBaseline = 'top';
  for (const b of boxes) {
    const x = dx + b.x * scale;
    const y = dy + b.y * scale;
    ctx.strokeRect(x, y, b.width * scale, b.height * scale);
    const label = `Person ${Math.round(b.score * 100)}%`;
    const labelY = Math.max(0, y - 18);
    ctx.fillStyle = BOX_COLOR;
    ctx.fillRect(x, labelY, ctx.measureText(label).width + 8, 18);
    ctx.fillStyle = '#fff';
    ctx.fillText(label, x + 4, labelY + 2);
  }
}
