/*
 * MediaRecorder writes its files as a live stream: Chrome's WebM has no
 * Duration and its fragmented MP4 declares a duration of 0. Players that
 * read only the header then show no length (no usable seek bar) or a
 * wrong one. These patch the length into the file header. For MP4 the
 * length is read from the media's own timestamps; for WebM the caller's
 * estimate is used. Only the header is rewritten; the media data is left
 * as it is, and a file that doesn't look as expected is returned unchanged.
 */

/** The headers sit in the first chunk; this much is plenty. */
const HEAD_BYTES = 256 * 1024;

export async function withDuration(blob: Blob, estimateMs: number): Promise<Blob> {
  try {
    const head = new Uint8Array(await blob.slice(0, HEAD_BYTES).arrayBuffer());
    const mp4 = blob.type.includes('mp4');
    const durationMs = (mp4 && (await mp4MediaMs(blob, head))) || estimateMs;
    if (!(durationMs > 0)) return blob;
    const fixed = mp4 ? fixMp4(head, durationMs) : fixWebm(head, durationMs);
    return fixed ? new Blob([fixed, blob.slice(HEAD_BYTES)], { type: blob.type }) : blob;
  } catch {
    return blob;
  }
}

// --- WebM (EBML) ---------------------------------------------------------

const SEGMENT = 0x18538067;
const INFO = 0x1549a966;
const TIMECODE_SCALE = 0x2ad7b1;
const DURATION = 0x4489;

/** An EBML element ID keeps its length-marker bits. */
function readId(b: Uint8Array, at: number): { id: number; len: number } | null {
  const first = b[at];
  const len = first >= 0x80 ? 1 : first >= 0x40 ? 2 : first >= 0x20 ? 3 : first >= 0x10 ? 4 : 0;
  if (!len || at + len > b.length) return null;
  let id = 0;
  for (let i = 0; i < len; i++) id = id * 256 + b[at + i];
  return { id, len };
}

/** An EBML size; `unknown` is the all-ones value of a live stream. */
function readSize(b: Uint8Array, at: number): { size: number; len: number; unknown: boolean } | null {
  const first = b[at];
  let len = 1;
  while (len <= 8 && !(first & (0x80 >> (len - 1)))) len++;
  if (len > 8 || at + len > b.length) return null;
  let size = first & (0xff >> len);
  let allOnes = size === 0xff >> len;
  for (let i = 1; i < len; i++) {
    size = size * 256 + b[at + i];
    allOnes &&= b[at + i] === 0xff;
  }
  return { size, len, unknown: allOnes };
}

/** Writes `size` into an existing size field of `len` bytes, if it fits. */
function writeSize(b: Uint8Array, at: number, len: number, size: number): boolean {
  if (size >= 2 ** (7 * len) - 1) return false;
  let v = size;
  for (let i = len - 1; i >= 0; i--) {
    b[at + i] = v % 256;
    v = Math.floor(v / 256);
  }
  b[at] |= 0x80 >> (len - 1);
  return true;
}

function fixWebm(head: Uint8Array<ArrayBuffer>, durationMs: number): Uint8Array<ArrayBuffer> | null {
  // EBML header, then the Segment.
  const ebml = readId(head, 0);
  const ebmlSize = ebml && readSize(head, ebml.len);
  if (!ebml || !ebmlSize) return null;
  let at = ebml.len + ebmlSize.len + ebmlSize.size;
  const seg = readId(head, at);
  const segSize = seg && readSize(head, at + seg.len);
  if (!seg || seg.id !== SEGMENT || !segSize) return null;
  const segSizeAt = at + seg.len;
  at = segSizeAt + segSize.len;

  // Find Info among the Segment's first children.
  while (at < head.length) {
    const el = readId(head, at);
    const sz = el && readSize(head, at + el.len);
    if (!el || !sz || sz.unknown) return null;
    const body = at + el.len + sz.len;
    if (el.id !== INFO) {
      at = body + sz.size;
      continue;
    }
    if (body + sz.size > head.length) return null;
    // Duration is in TimecodeScale units (default 1 ms).
    let scale = 1_000_000;
    for (let p = body; p < body + sz.size; ) {
      const c = readId(head, p);
      const cs = c && readSize(head, p + c.len);
      if (!c || !cs) return null;
      const cb = p + c.len + cs.len;
      if (c.id === DURATION) return null; // already has one
      if (c.id === TIMECODE_SCALE) {
        scale = 0;
        for (let i = 0; i < cs.size; i++) scale = scale * 256 + head[cb + i];
      }
      p = cb + cs.size;
    }
    const dur = new Uint8Array(11);
    dur.set([0x44, 0x89, 0x88]);
    new DataView(dur.buffer).setFloat64(3, (durationMs * 1_000_000) / scale);

    const out = new Uint8Array(head.length + dur.length);
    const end = body + sz.size;
    out.set(head.subarray(0, end));
    out.set(dur, end);
    out.set(head.subarray(end), end + dur.length);
    if (!writeSize(out, at + el.len, sz.len, sz.size + dur.length)) return null;
    if (!segSize.unknown && !writeSize(out, segSizeAt, segSize.len, segSize.size + dur.length)) return null;
    return out;
  }
  return null;
}

// --- MP4 (ISO BMFF) ------------------------------------------------------

interface Box {
  type: string;
  start: number;
  size: number;
  header: number;
}

function boxes(view: DataView, start: number, end: number): Box[] {
  const out: Box[] = [];
  for (let at = start; at + 8 <= end; ) {
    let size = view.getUint32(at);
    let header = 8;
    if (size === 1) {
      size = Number(view.getBigUint64(at + 8));
      header = 16;
    } else if (size === 0) {
      size = end - at;
    }
    if (size < header) break;
    const type = String.fromCharCode(...new Uint8Array(view.buffer, view.byteOffset + at + 4, 4));
    out.push({ type, start: at, size, header });
    at += size;
  }
  return out;
}

const child = (view: DataView, box: Box, type: string) =>
  boxes(view, box.start + box.header, box.start + box.size).find((b) => b.type === type);

/** Writes a 32- or 64-bit duration field. */
function setDuration(view: DataView, at: number, version: number, value: number) {
  if (version === 1) view.setBigUint64(at, BigInt(value));
  else view.setUint32(at, Math.min(value, 0xffffffff));
}

function fixMp4(head: Uint8Array<ArrayBuffer>, durationMs: number): Uint8Array<ArrayBuffer> | null {
  const view = new DataView(head.buffer, head.byteOffset, head.byteLength);
  const top = boxes(view, 0, head.length);
  const moov = top.find((b) => b.type === 'moov');
  if (!moov || moov.header !== 8 || moov.start + moov.size > head.length) return null;
  // Track data offsets must be relative to each moof, or inserting bytes
  // before the fragments would break them.
  for (const moof of top.filter((b) => b.type === 'moof')) {
    if (moof.start + moof.size > head.length) break;
    for (const traf of boxes(view, moof.start + 8, moof.start + moof.size).filter((b) => b.type === 'traf')) {
      const tfhd = child(view, traf, 'tfhd');
      if (tfhd && view.getUint32(tfhd.start + 8) & 0x000001) return null;
    }
  }

  const mvhd = child(view, moov, 'mvhd');
  if (!mvhd) return null;
  const mvhdVersion = head[mvhd.start + 8];
  const timescale = view.getUint32(mvhd.start + (mvhdVersion === 1 ? 28 : 20));
  if (!timescale) return null;
  const duration = Math.round((durationMs * timescale) / 1000);
  setDuration(view, mvhd.start + (mvhdVersion === 1 ? 32 : 24), mvhdVersion, duration);
  for (const trak of boxes(view, moov.start + 8, moov.start + moov.size).filter((b) => b.type === 'trak')) {
    const tkhd = child(view, trak, 'tkhd');
    if (!tkhd) continue;
    const v = head[tkhd.start + 8];
    setDuration(view, tkhd.start + (v === 1 ? 36 : 28), v, duration);
  }

  // A fragmented file's overall length belongs in mvex/mehd.
  const mvex = child(view, moov, 'mvex');
  if (!mvex || mvex.header !== 8) return head;
  const mehd = child(view, mvex, 'mehd');
  if (mehd) {
    setDuration(view, mehd.start + 12, head[mehd.start + 8], duration);
    return head;
  }
  const add = new Uint8Array(16);
  const av = new DataView(add.buffer);
  av.setUint32(0, 16);
  add.set([0x6d, 0x65, 0x68, 0x64], 4); // 'mehd', version 0, flags 0
  av.setUint32(12, Math.min(duration, 0xffffffff));
  const at = mvex.start + 8;
  const out = new Uint8Array(head.length + add.length);
  out.set(head.subarray(0, at));
  out.set(add, at);
  out.set(head.subarray(at), at + add.length);
  const ov = new DataView(out.buffer);
  ov.setUint32(mvex.start, mvex.size + add.length);
  ov.setUint32(moov.start, moov.size + add.length);
  return out;
}

/** Reads a box's children from a buffer that holds the whole box. */
const childrenOf = (view: DataView, box: Box) => boxes(view, box.start + box.header, box.start + box.size);

/** Per track: timescale (mdhd) and default sample duration (trex). */
function trackInfo(view: DataView, moov: Box) {
  const tracks = new Map<number, { timescale: number; defaultDuration: number }>();
  for (const trak of childrenOf(view, moov).filter((b) => b.type === 'trak')) {
    const tkhd = child(view, trak, 'tkhd');
    const mdia = child(view, trak, 'mdia');
    const mdhd = mdia && child(view, mdia, 'mdhd');
    if (!tkhd || !mdhd) continue;
    const id = view.getUint32(tkhd.start + (view.getUint8(tkhd.start + 8) === 1 ? 28 : 20));
    const timescale = view.getUint32(mdhd.start + (view.getUint8(mdhd.start + 8) === 1 ? 28 : 20));
    tracks.set(id, { timescale, defaultDuration: 0 });
  }
  const mvex = child(view, moov, 'mvex');
  for (const trex of mvex ? childrenOf(view, mvex).filter((b) => b.type === 'trex') : []) {
    const t = tracks.get(view.getUint32(trex.start + 12));
    if (t) t.defaultDuration = view.getUint32(trex.start + 20);
  }
  return tracks;
}

/** Start and end, in seconds, of each track's samples in one moof. */
function fragmentSpan(view: DataView, moof: Box, tracks: ReturnType<typeof trackInfo>) {
  const spans: { start: number; end: number }[] = [];
  for (const traf of childrenOf(view, moof).filter((b) => b.type === 'traf')) {
    const tfhd = child(view, traf, 'tfhd');
    const tfdt = child(view, traf, 'tfdt');
    if (!tfhd || !tfdt) continue;
    const track = tracks.get(view.getUint32(tfhd.start + 12));
    if (!track?.timescale) continue;
    // tfhd optional fields, in order, after track_ID.
    const tfhdFlags = view.getUint32(tfhd.start + 8) & 0xffffff;
    let at = tfhd.start + 16;
    if (tfhdFlags & 0x01) at += 8; // base_data_offset
    if (tfhdFlags & 0x02) at += 4; // sample_description_index
    const defaultDuration = tfhdFlags & 0x08 ? view.getUint32(at) : track.defaultDuration;
    const base =
      view.getUint8(tfdt.start + 8) === 1
        ? Number(view.getBigUint64(tfdt.start + 12))
        : view.getUint32(tfdt.start + 12);
    let total = 0;
    for (const trun of childrenOf(view, traf).filter((b) => b.type === 'trun')) {
      const flags = view.getUint32(trun.start + 8) & 0xffffff;
      const count = view.getUint32(trun.start + 12);
      let p = trun.start + 16;
      if (flags & 0x01) p += 4; // data_offset
      if (flags & 0x04) p += 4; // first_sample_flags
      const perSample = ((flags & 0x100 ? 1 : 0) + (flags & 0x200 ? 1 : 0) + (flags & 0x400 ? 1 : 0) + (flags & 0x800 ? 1 : 0)) * 4;
      for (let i = 0; i < count; i++, p += perSample) total += flags & 0x100 ? view.getUint32(p) : defaultDuration;
    }
    spans.push({ start: base / track.timescale, end: (base + total) / track.timescale });
  }
  return spans;
}

/**
 * The media length of a fragmented MP4 in ms: from the first fragment's
 * start to the last one's end. Only box headers are read, plus the first
 * and last moof, so a long recording is not loaded into memory.
 */
async function mp4MediaMs(blob: Blob, head: Uint8Array<ArrayBuffer>): Promise<number | null> {
  const headView = new DataView(head.buffer, head.byteOffset, head.byteLength);
  const moov = boxes(headView, 0, head.length).find((b) => b.type === 'moov');
  if (!moov || moov.start + moov.size > head.length) return null;
  const tracks = trackInfo(headView, moov);

  let first: { start: number; size: number } | null = null;
  let last: { start: number; size: number } | null = null;
  let previous: { start: number; size: number } | null = null;
  for (let at = 0; at + 8 <= blob.size; ) {
    const h = new DataView(await blob.slice(at, at + 16).arrayBuffer());
    let size = h.getUint32(0);
    if (size === 1 && h.byteLength >= 16) size = Number(h.getBigUint64(8));
    else if (size === 0) size = blob.size - at;
    if (size < 8) return null;
    const type = String.fromCharCode(h.getUint8(4), h.getUint8(5), h.getUint8(6), h.getUint8(7));
    const complete = at + size <= blob.size;
    if (type === 'moof') {
      if (!complete) break;
      first ??= { start: at, size };
      previous = last;
      last = { start: at, size };
    } else if (type === 'mdat' && !complete) {
      // A file cut off mid-fragment: the last moof lists samples that are
      // missing, so the length ends with the fragment before it.
      last = previous;
      break;
    }
    at += size;
  }
  if (!first || !last) return null;

  const span = async (f: { start: number; size: number }) => {
    const view = new DataView(await blob.slice(f.start, f.start + f.size).arrayBuffer());
    return fragmentSpan(view, { type: 'moof', start: 0, size: f.size, header: 8 }, tracks);
  };
  const starts = (await span(first)).map((s) => s.start);
  const ends = (await span(last)).map((s) => s.end);
  if (!starts.length || !ends.length) return null;
  const ms = (Math.max(...ends) - Math.min(...starts)) * 1000;
  return ms > 0 ? Math.round(ms) : null;
}
