"use client";
import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import InterestGraph from "@/components/InterestGraph";
import { api } from "@/lib/api";
import type { ProfileResponse } from "@/lib/types";

export default function ProfilePage() {
  const [data, setData] = useState<ProfileResponse | null>(null);
  const [labels, setLabels] = useState<Record<string, string>>({});
  const [view, setView] = useState<"before" | "now">("now");
  const [sel, setSel] = useState<string | null>(null);
  const [err, setErr] = useState(false);

  const load = useCallback(() => api.profile().then(setData).catch(() => setErr(true)), []);
  useEffect(() => {
    load();
    api.topics().then((r) => setLabels(Object.fromEntries(r.topics.map((t) => [t.id, t.label])))).catch(() => {});
  }, [load]);

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

  if (err) return <main className="narrow empty"><h2>No profile yet</h2><p>Set up your paper first.</p><Link className="btn" href="/start">Make my paper</Link></main>;
  if (!data) return <main className="wrap page"><p className="label">Loading…</p></main>;

  const n = data.history.length;
  return (
    <main className="wrap page">
      <div className="kicker">Profile</div>
      <h1>What the paper has learned{data.user.name ? `, ${data.user.name}` : ""}</h1>
      <p style={{ color: "var(--ink-2)", margin: 0, maxWidth: 620 }}>
        Bigger circles are stronger interests. Open a story and the circle grows; skip it and it shrinks.
        Click any circle to nudge it yourself.
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
              <span style={{ color: c.d > 0 ? "var(--accent)" : "var(--ink-2)", fontVariantNumeric: "tabular-nums" }}>{c.d > 0 ? "▲" : "▼"} {Math.abs(Math.round(c.d * 100))} pts</span>
            </div>
          ))}
        </section>
      )}
    </main>
  );
}
