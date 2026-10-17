import { getUid } from "./session";
import type { Edition, EditionSummary, EventType, ProfileResponse, Topic } from "./types";

export const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function req<T>(path: string, init: RequestInit = {}): Promise<T> {
  const uid = getUid();
  const res = await fetch(`${API}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(uid ? { "X-User-Id": uid } : {}), ...(init.headers || {}) },
    cache: "no-store",
  });
  if (!res.ok) {
    const err = new Error(`${res.status} ${path}`) as Error & { status: number };
    err.status = res.status;
    throw err;
  }
  return res.json() as Promise<T>;
}

export type OnboardBody = {
  name?: string; city?: string; recent_read?: string; topics: string[]; other?: string;
  budget_min: 5 | 12 | 20; lang?: "en" | "ur";
};

export const api = {
  topics: () => req<{ topics: Topic[] }>("/api/topics"),
  users: () => req<{ users: Array<{ id: number; name: string | null; city: string | null; budget_min: number }> }>("/api/users"),
  onboard: (b: OnboardBody) => req<{ user_id: number }>("/api/onboard", { method: "POST", body: JSON.stringify(b) }),
  generate: () => req<Edition>("/api/editions/generate", { method: "POST" }),
  latest: () => req<Edition>("/api/editions/latest"),
  edition: (id: number | string) => req<Edition>(`/api/editions/${id}`),
  editions: () => req<{ editions: EditionSummary[] }>("/api/editions"),
  profile: () => req<ProfileResponse>("/api/profile"),
  adjust: (topic: string, delta: number) =>
    req("/api/profile/adjust", { method: "POST", body: JSON.stringify({ topic, delta }) }),
  /** Fire-and-forget engagement signal. Never throws, never blocks the UI. */
  event: (type: EventType, o: { edition_id?: number; article_id?: number; value?: number } = {}) => {
    req("/api/events", { method: "POST", body: JSON.stringify({ type, ...o }), keepalive: true }).catch(() => {});
  },
  /** Trigger Urdu translation of all headlines in an edition (cached server-side). */
  translate: (editionId: number) =>
    req<{ updated: number }>(`/api/editions/${editionId}/translate`, { method: "POST" }),
  pdfUrl: (id: number) => `${API}/api/editions/${id}/pdf?uid=${getUid() ?? ""}`,
};

