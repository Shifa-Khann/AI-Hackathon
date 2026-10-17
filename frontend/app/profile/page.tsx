"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";
import InterestGraph from "@/components/InterestGraph";
import { api } from "@/lib/api";
import type { ProfileResponse, Topic } from "@/lib/types";

const REGIONS = [
  { id: "pakistan",    label: "Pakistan",     flag: "PK" },
  { id: "south_asia", label: "South Asia",    flag: "SA" },
  { id: "middle_east",label: "Middle East",   flag: "ME" },
  { id: "global",     label: "Global",        flag: "GL" },
  { id: "tech",       label: "Tech & AI",     flag: "TC" },
  { id: "finance",    label: "Finance",       flag: "FN" },
];

export default function ProfilePage() {
  const router = useRouter();
  const [data, setData] = useState<ProfileResponse | null>(null);
  const [topicsList, setTopicsList] = useState<Topic[]>([]);
  const [labels, setLabels] = useState<Record<string, string>>({});
  const [view, setView] = useState<"before" | "now">("now");
  const [sel, setSel] = useState<string | null>(null);
  const [err, setErr] = useState(false);

  // Settings form state
  const [name, setName] = useState("");
  const [region, setRegion] = useState("global");
  const [selectedTopics, setSelectedTopics] = useState<string[]>([]);
  const [budget, setBudget] = useState<5 | 12 | 20>(12);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState<{ message: string; editionId?: number } | null>(null);
  const [saveError, setSaveError] = useState("");

  const load = useCallback(() => {
    api.profile()
      .then((res) => {
        setData(res);
        setName(res.user.name || "");
        setBudget((res.user.budget_min as 5 | 12 | 20) || 12);
        setRegion(res.user.region || res.profile.region || "global");
        // Initialize selected topics: use picked if available or high-weight topics
        const picked = res.profile.picked && res.profile.picked.length > 0
          ? res.profile.picked
          : Object.entries(res.profile.topics || {})
              .filter(([_, w]) => w >= 0.5)
              .map(([t]) => t);
        setSelectedTopics(picked);
      })
      .catch(() => setErr(true));
  }, []);

  useEffect(() => {
    load();
    api.topics()
      .then((r) => {
        setTopicsList(r.topics);
        setLabels(Object.fromEntries(r.topics.map((t) => [t.id, t.label])));
      })
      .catch(() => {});
  }, [load]);

  const toggleTopic = (id: string) => {
    setSelectedTopics((prev) =>
      prev.includes(id) ? prev.filter((t) => t !== id) : [...prev, id]
    );
  };

  const handleSaveSettings = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSaveSuccess(null);
    setSaveError("");
    try {
      const res = await api.updateSettings({
        name: name.trim() || undefined,
        region,
        topics: selectedTopics,
        budget_min: budget,
      });
      setSaving(false);
      setSaveSuccess({
        message: "Preferences saved! A fresh edition tailored to your new preferences has been prepared.",
        editionId: res.edition_id,
      });
      load();
      window.dispatchEvent(new Event("fold:user_changed"));
    } catch (e: any) {
      setSaving(false);
      setSaveError(e?.message || "Failed to save settings. Please try again.");
    }
  };

  const before = data?.history[0]?.topics ?? {};
  const now = data?.profile.topics ?? {};
  const ids = useMemo(() => Object.keys(now).sort(), [data]); // eslint-disable-line react-hooks/exhaustive-deps
  const shown = view === "before" ? before : now;

  const changes = useMemo(() =>
    ids.map((id) => ({ id, d: (now[id] ?? 0) - (before[id] ?? 0) })).filter((c) => Math.abs(c.d) >= 0.03).sort((a, b) => Math.abs(b.d) - Math.abs(a.d)).slice(0, 6),
  [ids, now, before]);

  const adjust = async (delta: number) => {
    if (!sel) return;
    await api.adjust(sel, delta);
    load();
  };

  if (err) {
    return (
      <main className="narrow empty">
        <h2>No account session</h2>
        <p>Please sign in to view your reader profile and settings.</p>
        <Link className="btn" href="/login">Sign In</Link>
      </main>
    );
  }

  if (!data) return <main className="wrap page"><p className="label">Loading…</p></main>;

  const n = data.history.length;

  return (
    <main className="wrap page">
      <div className="kicker">Reader Profile &amp; Preferences</div>
      <h1>Account Settings{data.user.name ? `, ${data.user.name}` : ""}</h1>
      <p style={{ color: "var(--ink-2)", margin: "0 0 32px", maxWidth: 660 }}>
        Customize your country focus, preferred news categories, and reading length anytime. Your next paper updates automatically.
      </p>

      {/* Settings Form */}
      <section style={{ background: "var(--paper-2)", border: "1px solid var(--rule)", padding: "24px 28px", borderRadius: 3, marginBottom: 48 }}>
        <form onSubmit={handleSaveSettings}>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 20, marginBottom: 20 }}>
            <div>
              <label className="label" style={{ display: "block", marginBottom: 6 }}>Reader Name</label>
              <input
                type="text"
                className="field"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Your name"
                style={{ width: "100%", background: "var(--paper)" }}
              />
            </div>
            <div>
              <label className="label" style={{ display: "block", marginBottom: 6 }}>Email Address</label>
              <input
                type="text"
                disabled
                className="field"
                value={data.user.email || "Private reader account"}
                style={{ width: "100%", background: "var(--paper)", opacity: 0.8, cursor: "not-allowed" }}
              />
            </div>
          </div>

          {/* Region Selector */}
          <div style={{ marginBottom: 24 }}>
            <label className="label" style={{ display: "block", marginBottom: 10 }}>Region &amp; Country Focus</label>
            <div className="region-grid">
              {REGIONS.map((r) => (
                <button
                  type="button"
                  key={r.id}
                  aria-pressed={region === r.id}
                  onClick={() => setRegion(r.id)}
                  className="region-btn"
                  style={{
                    border: `1px solid ${region === r.id ? "var(--accent)" : "var(--rule)"}`,
                    background: region === r.id ? "var(--accent-soft)" : "var(--paper)",
                    color: region === r.id ? "var(--accent)" : "var(--ink)",
                  }}
                >
                  <span className="region-code">{r.flag}</span>
                  <span className="region-label">{r.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Preferred News Categories */}
          <div style={{ marginBottom: 24 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 10 }}>
              <label className="label">Preferred News Categories</label>
              <span style={{ fontSize: 11, color: "var(--ink-2)" }}>{selectedTopics.length} selected</span>
            </div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
              {topicsList.map((t) => {
                const isSelected = selectedTopics.includes(t.id);
                return (
                  <button
                    type="button"
                    key={t.id}
                    onClick={() => toggleTopic(t.id)}
                    className="chip"
                    aria-pressed={isSelected}
                    style={{
                      cursor: "pointer",
                      fontSize: 12,
                      padding: "6px 12px",
                      background: isSelected ? "var(--accent-soft)" : "var(--paper)",
                      borderColor: isSelected ? "var(--accent)" : "var(--rule)",
                      color: isSelected ? "var(--accent)" : "var(--ink)",
                      fontWeight: isSelected ? 600 : 400,
                    }}
                  >
                    {t.label}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Reading Budget */}
          <div style={{ marginBottom: 24 }}>
            <label className="label" style={{ display: "block", marginBottom: 8 }}>Morning Reading Budget</label>
            <div className="budget" role="group">
              {[
                { min: 5 as const, label: "5 min · Quick" },
                { min: 12 as const, label: "12 min · Breakfast" },
                { min: 20 as const, label: "20 min · Broadsheet" },
              ].map((b) => (
                <button
                  type="button"
                  key={b.min}
                  aria-pressed={budget === b.min}
                  onClick={() => setBudget(b.min)}
                  style={{ padding: "10px 8px", background: "var(--paper)" }}
                >
                  <strong style={{ fontSize: 22 }}>{b.min}m</strong>
                  <span style={{ fontSize: 11 }}>{b.label}</span>
                </button>
              ))}
            </div>
          </div>

          {saveError && (
            <p role="alert" style={{ color: "var(--accent)", margin: "8px 0 16px", fontSize: 13 }}>
              {saveError}
            </p>
          )}

          {saveSuccess && (
            <div style={{ background: "rgba(47,125,79,.12)", border: "1px solid #2f7d4f", padding: "12px 16px", borderRadius: 2, margin: "8px 0 16px", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 8 }}>
              <span style={{ color: "#2f7d4f", fontSize: 13, fontWeight: 500 }}>
                {saveSuccess.message}
              </span>
              {saveSuccess.editionId && (
                <Link
                  href={`/paper/${saveSuccess.editionId}`}
                  className="btn sm"
                  style={{ background: "#2f7d4f", color: "#fff", borderColor: "#2f7d4f" }}
                >
                  Read Updated Edition &rarr;
                </Link>
              )}
            </div>
          )}

          <div style={{ display: "flex", gap: 12, alignItems: "center", marginTop: 8 }}>
            <button className="btn" type="submit" disabled={saving}>
              {saving ? "Saving changes…" : "Save Changes"}
            </button>
          </div>
        </form>
      </section>

      {/* Learning & Interest Graph Section */}
      <section style={{ borderTop: "1px solid var(--rule)", paddingTop: 36 }}>
        <div className="kicker">Algorithmic Learning Loop</div>
        <h2>What the paper has learned</h2>
        <p style={{ color: "var(--ink-2)", margin: "0 0 16px", maxWidth: 620 }}>
          Bigger circles represent higher editorial priority. Opening stories expands circles; skipping them shrinks them.
          Click any circle to manually nudge weights.
        </p>

        <div className="toolbar">
          <div className="seg" role="group" aria-label="Compare">
            <button aria-pressed={view === "before"} onClick={() => setView("before")}>At sign-up</button>
            <button aria-pressed={view === "now"} onClick={() => setView("now")}>Now</button>
          </div>
          <span className="label">{n} snapshot{n === 1 ? "" : "s"}</span>
        </div>

        <InterestGraph weights={shown} labels={labels} ids={ids} selected={sel} onSelect={setSel} />

        <div className="sel">
          {sel ? (
            <>
              <strong className="serif" style={{ fontSize: 22 }}>{labels[sel] ?? sel}</strong>
              <span className="label">{Math.round((now[sel] ?? 0) * 100)}% interest</span>
              <button className="btn sm" onClick={() => adjust(0.15)}>More of this</button>
              <button className="btn ghost sm" onClick={() => adjust(-0.15)}>Less of this</button>
            </>
          ) : <span className="label">Select a circle</span>}
        </div>

        {changes.length > 0 && (
          <section style={{ marginTop: 40, maxWidth: 560 }}>
            <div className="kicker">Since you signed up</div>
            {changes.map((c) => (
              <div key={c.id} style={{ display: "flex", justifyContent: "space-between", padding: "10px 0", borderBottom: "1px solid var(--rule)" }}>
                <span>{labels[c.id] ?? c.id}</span>
                <span style={{ color: c.d > 0 ? "var(--accent)" : "var(--ink-2)", fontVariantNumeric: "tabular-nums" }}>
                  {c.d > 0 ? "▲" : "▼"} {Math.abs(Math.round(c.d * 100))} pts
                </span>
              </div>
            ))}
          </section>
        )}
      </section>
    </main>
  );
}
