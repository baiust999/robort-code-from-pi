/**
 * The controller key, remembered in this browser only.
 *
 * Storage can be unavailable (private window, blocked site data), in which
 * case the key simply lasts until the page is reloaded.
 */

const STORAGE_KEY = 'robot.controllerKey';

export function loadControllerKey(): string | null {
  try {
    return window.localStorage.getItem(STORAGE_KEY) || null;
  } catch {
    return null;
  }
}

export function saveControllerKey(key: string | null): void {
  try {
    if (key) window.localStorage.setItem(STORAGE_KEY, key);
    else window.localStorage.removeItem(STORAGE_KEY);
  } catch {
    // Not persisted; still used for this page load.
  }
}
