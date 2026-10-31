import { useSyncExternalStore } from 'react';
import type { VictimMark } from './protocol';
import { download } from './download';

/*
 * Snapshots live only on the device that took them, never on the robot. They
 * are kept in this browser's IndexedDB, so they survive a reload and do not
 * depend on the browser letting a download through, and mirrored here as
 * object URLs for links. Other dashboards have none.
 */
const DB_NAME = 'robot-victims';
const STORE = 'snapshots';
const localSnapshots = new Map<string, { blob: Blob; url: string }>();
const listeners = new Set<() => void>();
let version = 0;

function remember(id: string, blob: Blob) {
  if (localSnapshots.has(id)) return;
  localSnapshots.set(id, { blob, url: URL.createObjectURL(blob) });
  version += 1;
  listeners.forEach((l) => l());
}

function openDb(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, 1);
    req.onupgradeneeded = () => req.result.createObjectStore(STORE);
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

async function storeSnapshot(id: string, blob: Blob): Promise<void> {
  const db = await openDb();
  await new Promise<void>((resolve, reject) => {
    const tx = db.transaction(STORE, 'readwrite');
    tx.objectStore(STORE).put(blob, id);
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
  });
  db.close();
}

async function loadSnapshots(): Promise<void> {
  const db = await openDb();
  const tx = db.transaction(STORE, 'readonly');
  const store = tx.objectStore(STORE);
  const [keys, blobs] = await Promise.all(
    [store.getAllKeys(), store.getAll()].map(
      (req) => new Promise<unknown[]>((resolve, reject) => {
        req.onsuccess = () => resolve(req.result);
        req.onerror = () => reject(req.error);
      }),
    ),
  );
  db.close();
  keys.forEach((k, i) => remember(String(k), blobs[i] as Blob));
}

// Without IndexedDB (a private window, blocked storage) snapshots last until a reload.
loadSnapshots().catch(() => {});

/** Re-renders the caller when a snapshot is added or loaded. */
export function useLocalSnapshots(): number {
  return useSyncExternalStore(
    (l) => {
      listeners.add(l);
      return () => listeners.delete(l);
    },
    () => version,
  );
}

/** Drops a deleted mark's snapshot from this browser. Files already in Downloads stay. */
export async function forgetSnapshot(id: string): Promise<void> {
  const local = localSnapshots.get(id);
  if (local) {
    URL.revokeObjectURL(local.url);
    localSnapshots.delete(id);
    version += 1;
    listeners.forEach((l) => l());
  }
  const db = await openDb();
  await new Promise<void>((resolve, reject) => {
    const tx = db.transaction(STORE, 'readwrite');
    tx.objectStore(STORE).delete(id);
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
  });
  db.close();
}

export const localSnapshotUrl = (id: string) => localSnapshots.get(id)?.url ?? null;

const value = (v: number | null, unit = '') => (v === null ? 'unknown' : `${v}${unit}`);

/** The mark as plain text, readable on any device with no app. */
export function victimRecordText(m: VictimMark): string {
  let position: string;
  if (m.gps_fix && m.lat !== null && m.lon !== null) position = `${m.lat}, ${m.lon} (GPS fix, ${value(m.gps_sats)} satellites)`;
  else if (m.last_fix) position = `${m.last_fix[0]}, ${m.last_fix[1]} (no fix at the mark: last known position)`;
  else position = 'no position';
  return [
    'Victim mark',
    `Id:        ${m.id}`,
    `Time:      ${new Date(m.ts).toLocaleString()} (${new Date(m.ts).toISOString()})`,
    `Note:      ${m.note || '(no note)'}`,
    `Position:  ${position}`,
    `Camera:    pan ${value(m.pan_angle, ' deg')}, tilt ${value(m.tilt_angle, ' deg')}`,
    `AI score:  ${m.ai_score === null ? 'no person seen' : `${Math.round(m.ai_score * 100)}%`}`,
    `Snapshot:  ${localSnapshots.has(m.id) ? `victim-${m.id}.jpg` : 'none on this device'}`,
    '',
  ].join('\n');
}

export const downloadVictimPhoto = (m: VictimMark) => {
  const local = localSnapshots.get(m.id);
  if (local) download(local.blob, `victim-${m.id}.jpg`);
};

export const downloadVictimRecord = (m: VictimMark) =>
  download(new Blob([victimRecordText(m)], { type: 'text/plain' }), `victim-${m.id}.txt`);

/**
 * Keeps a new mark's snapshot in this browser, then downloads the photo and a
 * text record. Resolves to whether the snapshot was stored to survive a reload.
 */
export async function saveVictimToDevice(m: VictimMark, snapshot?: Blob | null): Promise<boolean> {
  if (snapshot) remember(m.id, snapshot);
  const stored = snapshot ? storeSnapshot(m.id, snapshot).then(() => true, () => false) : Promise.resolve(false);
  // Downloads go first, while the operator's click still counts as a gesture;
  // the photo before the text, so a held-back second download is the text.
  downloadVictimPhoto(m);
  downloadVictimRecord(m);
  return stored;
}
