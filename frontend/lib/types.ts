export type Topic = { id: string; label: string };

export type Item = {
  id: number; article_id: number; slot: number; section: string;
  headline: string; dek: string; why: string; source: string; url: string;
  image_url: string | null; topics: string[]; read_min: number;
  is_blind_spot: boolean; headline_ur: string | null; dek_ur?: string | null; why_ur?: string | null;
};

export type QuizQ = { q: string; options: string[]; answer: number; article_id: number };

export type Edition = {
  id: number; number: number; date: string; editor_note: string; todo: string; read_min: number;
  plan: { hero?: number; columns?: number; hero_style?: string; sections?: string[] };
  items: Item[]; quiz: QuizQ[];
};

export type EditionSummary = { id: number; number: number; date: string; story_count: number; read_min: number; lead_headline: string };

export type Profile = {
  topics: Record<string, number>; picked: string[]; entities: string[]; tone: string; avoid: string[];
  summary: string; quote: string; blind_appetite: number;
};

export type ProfileResponse = {
  user: { id: number; name: string | null; city: string | null; budget_min: number; lang: string };
  profile: Profile;
  history: { label: string; created_at: string; topics: Record<string, number> }[];
};

export type EventType =
  | "open" | "skip" | "unskip" | "dwell" | "quiz_correct" | "quiz_wrong" | "more_challenge" | "less_challenge";
