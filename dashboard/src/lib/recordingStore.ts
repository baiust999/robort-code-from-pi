import { withDuration } from './fixDuration';

/*
 * Session recordings, kept chunk by chunk in this browser's IndexedDB so a
 * crash or reload mid-recording loses at most the last second or two. A finished
 * recording stays here until the operator deletes it, because the browser
 * may hold back the automatic download. Like victim snapshots, recordings
 * never go to the robot.
 */
const DB_NAME = 'robot-recordings';
const CHUNKS = 'chunks';
const META = 'meta';

export interface RecordingMeta {
  id: string;
  startedAt: number;
  mimeType: string;
  /** False while recording, and for one a crash cut off. */
  finished: boolean;
  /** Length so far, updated with every chunk; written into the file header on save. */
  durationMs?: number;
}

function openDb(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, 1);
    req.onupgradeneeded = () => {
      req.result.createObjectStore(CHUNKS);
      req.result.createObjectStore(META, { keyPath: 'id' });
    };
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

function done(tx: IDBTransaction): Promise<void> {
  return new Promise((resolve, reject) => {
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
    tx.onabort = () => reject(tx.error);
  });
}

function result<T>(req: IDBRequest<T>): Promise<T> {
  return new Promise((resolve, reject) => {
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

/** Every chunk key of one recording, in order: [id, seq]. */
const range = (id: string) => IDBKeyRange.bound([id, 0], [id, Number.MAX_SAFE_INTEGER]);

export async function putMeta(meta: RecordingMeta): Promise<void> {
  const db = await openDb();
  const tx = db.transaction(META, 'readwrite');
  tx.objectStore(META).put(meta);
  await done(tx);
  db.close();
}

export async function appendChunk(id: string, seq: number, chunk: Blob, durationMs: number): Promise<void> {
  const db = await openDb();
  const tx = db.transaction([CHUNKS, META], 'readwrite');
  tx.objectStore(CHUNKS).put(chunk, [id, seq]);
  // The length goes with the chunk, so a recording a crash cut off still has one.
  const metas = tx.objectStore(META);
  const req = metas.get(id);
  req.onsuccess = () => {
    if (req.result) metas.put({ ...req.result, durationMs });
  };
  await done(tx);
  db.close();
}

/** The stored recording as one file with its length set, or null if no chunks were kept. */
export async function assembleRecording(meta: RecordingMeta): Promise<Blob | null> {
  const db = await openDb();
  const tx = db.transaction([CHUNKS, META], 'readonly');
  const [chunks, stored] = await Promise.all([
    result(tx.objectStore(CHUNKS).getAll(range(meta.id))),
    result(tx.objectStore(META).get(meta.id)),
  ]);
  db.close();
  if (!chunks.length) return null;
  const durationMs = (stored as RecordingMeta | undefined)?.durationMs ?? meta.durationMs ?? 0;
  return withDuration(new Blob(chunks as Blob[], { type: meta.mimeType }), durationMs);
}

export async function deleteRecording(id: string): Promise<void> {
  const db = await openDb();
  const tx = db.transaction([CHUNKS, META], 'readwrite');
  tx.objectStore(CHUNKS).delete(range(id));
  tx.objectStore(META).delete(id);
  await done(tx);
  db.close();
}

/** Every recording kept in this browser, oldest first. */
export async function listRecordings(): Promise<RecordingMeta[]> {
  const db = await openDb();
  const metas = await result(db.transaction(META, 'readonly').objectStore(META).getAll());
  db.close();
  return (metas as RecordingMeta[]).sort((a, b) => a.startedAt - b.startedAt);
}
