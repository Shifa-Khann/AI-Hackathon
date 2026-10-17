const KEY = "fold_uid";

export function getUid(): string | null {
  try { return localStorage.getItem(KEY); } catch { return null; }
}
export function setUid(uid: string | number) {
  try { localStorage.setItem(KEY, String(uid)); } catch { /* private mode */ }
}
export function clearUid() {
  try { localStorage.removeItem(KEY); } catch { /* ignore */ }
}
