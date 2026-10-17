const UID_KEY = "fold_uid";
const TOKEN_KEY = "fold_token";
const USER_KEY = "fold_user";

export function getToken(): string | null {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

export function getUid(): string | null {
  try {
    return localStorage.getItem(UID_KEY);
  } catch {
    return null;
  }
}

export function setSession(token: string, uid: string | number, user?: any) {
  try {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(UID_KEY, String(uid));
    if (user) {
      localStorage.setItem(USER_KEY, JSON.stringify(user));
    }
  } catch {
    /* private mode */
  }
}

export function setUid(uid: string | number) {
  try {
    localStorage.setItem(UID_KEY, String(uid));
  } catch {
    /* private mode */
  }
}

export function clearSession() {
  try {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(UID_KEY);
    localStorage.removeItem(USER_KEY);
    sessionStorage.clear();
  } catch {
    /* ignore */
  }
}

export const clearUid = clearSession;
