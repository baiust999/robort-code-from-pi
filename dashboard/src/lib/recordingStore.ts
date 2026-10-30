/*
 * Session recordings, kept chunk by chunk in this browser's IndexedDB so a
 * crash or reload mid-recording loses at most the last second. A finished
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

export async function appendChunk(id: string, seq: number, chunk: Blob): Promise<void> {
  const db = await openDb();
  const tx = db.transaction(CHUNKS, 'readwrite');
  tx.objectStore(CHUNKS).put(chunk, [id, seq]);
  await done(tx);
  db.close();
}

/** The stored recording as one file, or null if no chunks were kept. */
export async function assembleRecording(meta: RecordingMeta): Promise<Blob | null> {
  const db = await openDb();
  const chunks = await result(db.transaction(CHUNKS, 'readonly').objectStore(CHUNKS).getAll(range(meta.id)));
  db.close();
  return chunks.length ? new Blob(chunks as Blob[], { type: meta.mimeType }) : null;
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
