import { clearSession, getToken, getUid } from "./session";
import type { Edition, EditionSummary, EventType, ProfileResponse, Topic } from "./types";

export const API = "";
// Direct backend URL if specified; otherwise routes through Next.js rewrites (/api/...)
const BACKEND_ORIGIN = (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/+$/, "");

async function req<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = getToken();
  const uid = getUid();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(token ? { "Authorization": `Bearer ${token}` } : {}),
    ...(uid ? { "X-User-Id": uid } : {}),
    ...((init.headers as Record<string, string>) || {}),
  };

  const res = await fetch(`${API}${path}`, {
    ...init,
    headers,
    cache: "no-store",
  });

  if (res.status === 401 && typeof window !== "undefined" && !path.startsWith("/api/auth/login") && !path.startsWith("/api/auth/signup")) {
    clearSession();
    window.dispatchEvent(new Event("fold:user_changed"));
  }

  if (!res.ok) {
    let message = `${res.status} ${path}`;
    try {
      const body = await res.clone().json();
      if (body?.detail) message = Array.isArray(body.detail)
        ? body.detail.map((d: any) => d?.msg ?? d).join(", ")
        : String(body.detail);
    } catch {}
    const err = new Error(message) as Error & { status: number };
    err.status = res.status;
    throw err;
  }
  return res.json() as Promise<T>;
}

export type OnboardBody = {
  name?: string;
  city?: string;
  recent_read?: string;
  topics: string[];
  other?: string;
  budget_min: 5 | 12 | 20;
  lang?: "en" | "ur";
};

export type SavedArticle = {
  saved_id: number;
  saved_at: string;
  article_id: number;
  id: number;
  url: string;
  headline: string;
  dek: string;
  source: string;
  image_url: string | null;
  read_min: number;
  topics: string[];
  published_at?: string;
};

export const api = {
  topics: () => req<{ topics: Topic[] }>("/api/topics"),
  login: (body: { email: string; password: string }) =>
    req<{ user_id: number; name: string; email: string; token: string }>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  signup: (body: { email: string; password: string; name?: string; budget_min?: number; region?: string; topics?: string[] }) =>
    req<{ user_id: number; name: string; email: string; token: string }>("/api/auth/signup", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  logout: () => req<{ ok: boolean }>("/api/auth/logout", { method: "POST" }),
  onboard: (b: OnboardBody) =>
    req<{ user_id: number; token: string }>("/api/onboard", {
      method: "POST",
      body: JSON.stringify(b),
    }),
  generate: () => req<Edition>("/api/editions/generate", { method: "POST" }),
  latest: () => req<Edition>("/api/editions/latest"),
  edition: (id: number | string) => req<Edition>(`/api/editions/${id}`),
  editions: () => req<{ editions: EditionSummary[] }>("/api/editions"),
  profile: () => req<ProfileResponse>("/api/profile"),
  updateSettings: (body: { name?: string; region?: string; topics?: string[]; budget_min?: number }) =>
    req<{ ok: boolean; user: any; profile: any; edition_id: number; edition: Edition }>("/api/profile/settings", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  adjust: (topic: string, delta: number) =>
    req("/api/profile/adjust", { method: "POST", body: JSON.stringify({ topic, delta }) }),

  // Saved news bookmarks
  savedArticles: () => req<{ saved: SavedArticle[] }>("/api/saved"),
  savedIds: () => req<{ saved_ids: number[] }>("/api/saved/ids"),
  saveArticle: (articleId: number) =>
    req<{ saved: boolean; article_id: number }>(`/api/saved/${articleId}`, { method: "POST" }),
  unsaveArticle: (articleId: number) =>
    req<{ saved: boolean; article_id: number }>(`/api/saved/${articleId}`, { method: "DELETE" }),

  /** Fire-and-forget engagement signal. Never throws, never blocks the UI. */
  event: (type: EventType, o: { edition_id?: number; article_id?: number; value?: number } = {}) => {
    req("/api/events", { method: "POST", body: JSON.stringify({ type, ...o }), keepalive: true }).catch(() => {});
  },
  /** Trigger Urdu translation of all headlines in an edition (cached server-side). */
  translate: (editionId: number) =>
    req<{ updated: number }>(`/api/editions/${editionId}/translate`, { method: "POST" }),
  pdfUrl: (id: number) => {
    const tok = getToken();
    const uid = getUid();
    const authParam = tok ? `token=${tok}` : (uid ? `uid=${uid}` : "");
    return `${BACKEND_ORIGIN}/api/editions/${id}/pdf?${authParam}`;
  },
};
