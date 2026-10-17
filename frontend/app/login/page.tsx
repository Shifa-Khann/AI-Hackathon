"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { api } from "@/lib/api";
import { setSession } from "@/lib/session";

const REGIONS = [
  { id: "pakistan",    label: "Pakistan",     flag: "PK", topics: ["politics_pk","economy_pk","ai","cricket","startups"] },
  { id: "south_asia", label: "South Asia",    flag: "SA", topics: ["geopolitics","economy_pk","ai","cricket","climate"] },
  { id: "middle_east",label: "Middle East",   flag: "ME", topics: ["geopolitics","markets","energy","ai","startups"] },
  { id: "global",     label: "Global",        flag: "GL", topics: ["ai","markets","startups","geopolitics","science"] },
  { id: "tech",       label: "Tech & AI",     flag: "TC", topics: ["ai","software","cybersecurity","startups","design"] },
  { id: "finance",    label: "Finance",       flag: "FN", topics: ["markets","economy_pk","crypto","startups","business"] },
];

const TOPIC_LABELS: Record<string, string> = {
  ai: "AI", politics_pk: "Pakistan Politics", economy_pk: "Economy (PK)", cricket: "Cricket",
  startups: "Startups", geopolitics: "Geopolitics", climate: "Climate", energy: "Energy",
  markets: "Markets", science: "Science", software: "Software", cybersecurity: "Cybersecurity",
  design: "Design", crypto: "Crypto", business: "Business", football: "Football",
  health: "Health", books: "Books", space: "Space",
};

export default function LoginPage() {
  const router = useRouter();
  const [tab, setTab] = useState<"login" | "signup">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [budget, setBudget] = useState<5 | 12 | 20>(12);
  const [region, setRegion] = useState<string>("pakistan");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const selectedRegion = REGIONS.find((r) => r.id === region) ?? REGIONS[0];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      if (tab === "login") {
        const res = await api.login({ email, password });
        setSession(res.token, res.user_id, res);
        window.dispatchEvent(new Event("fold:user_changed"));
        router.push("/paper");
      } else {
        const res = await api.signup({
          email, password,
          name: name.trim() || undefined,
          budget_min: budget,
          region,
          topics: selectedRegion.topics,
        });
        setSession(res.token, res.user_id, res);
        window.dispatchEvent(new Event("fold:user_changed"));
        router.push("/paper");
      }
    } catch (err: any) {
      setBusy(false);
      setError(err?.message || "Invalid credentials. Please try again.");
    }
  };

  return (
    <main className="narrow onb">
      <div className="kicker">Reader Account</div>
      <h1 style={{ marginBottom: 12 }}>
        {tab === "login" ? "Sign in to The Fold" : "Create your reader account"}
      </h1>
      <p className="sub" style={{ marginBottom: 24 }}>
        {tab === "login"
          ? "Access your personal morning newspaper and reading history."
          : "Register to get a daily finite newspaper shaped by your reading."}
      </p>

      {/* Tabs */}
      <div style={{ display: "flex", gap: 10, marginBottom: 24, borderBottom: "1px solid var(--rule)", paddingBottom: 10 }}>
        <button
          className="linkbtn"
          style={{ fontSize: 14, color: tab === "login" ? "var(--accent)" : "var(--ink-2)", borderBottom: tab === "login" ? "2px solid var(--accent)" : "none", paddingBottom: 6 }}
          onClick={() => { setTab("login"); setError(""); }}
        >
          Sign In
        </button>
        <button
          className="linkbtn"
          style={{ fontSize: 14, color: tab === "signup" ? "var(--accent)" : "var(--ink-2)", borderBottom: tab === "signup" ? "2px solid var(--accent)" : "none", paddingBottom: 6 }}
          onClick={() => { setTab("signup"); setError(""); }}
        >
          Create Account
        </button>
      </div>

      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        {tab === "signup" && (
          <div>
            <label className="label" htmlFor="name" style={{ display: "block", marginBottom: 6 }}>Full Name (optional)</label>
            <input id="name" type="text" className="field" value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. Ayesha Khan" />
          </div>
        )}

        <div>
          <label className="label" htmlFor="email" style={{ display: "block", marginBottom: 6 }}>Email address</label>
          <input id="email" type="email" required className="field" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" />
        </div>

        <div>
          <label className="label" htmlFor="password" style={{ display: "block", marginBottom: 6 }}>Password</label>
          <input id="password" type="password" required className="field" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" />
        </div>

        {tab === "signup" && (
          <>
            {/* Region selector */}
            <div>
              <label className="label" style={{ display: "block", marginBottom: 10 }}>Your Region &amp; News Focus</label>
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
                      background: region === r.id ? "var(--accent-soft)" : "var(--paper-2)",
                      color: region === r.id ? "var(--accent)" : "var(--ink)",
                    }}
                  >
                    <span className="region-code">{r.flag}</span>
                    <span className="region-label">{r.label}</span>
                  </button>
                ))}
              </div>
              {/* Preview topics for selected region */}
              <div style={{ marginTop: 10, display: "flex", flexWrap: "wrap", gap: 6 }}>
                {selectedRegion.topics.map((t) => (
                  <span key={t} style={{ fontSize: 11, padding: "3px 8px", border: "1px solid var(--rule)", borderRadius: 2, color: "var(--ink-2)", letterSpacing: "0.08em", textTransform: "uppercase" }}>
                    {TOPIC_LABELS[t] ?? t}
                  </span>
                ))}
              </div>
            </div>

            {/* Budget selector */}
            <div style={{ marginTop: 4 }}>
              <label className="label" style={{ display: "block", marginBottom: 8 }}>Morning Reading Budget</label>
              <div className="budget" role="group">
                {[
                  { min: 5 as const, label: "5 min · Quick" },
                  { min: 12 as const, label: "12 min · Breakfast" },
                  { min: 20 as const, label: "20 min · Broadsheet" },
                ].map((b) => (
                  <button type="button" key={b.min} aria-pressed={budget === b.min} onClick={() => setBudget(b.min)} style={{ padding: "12px 6px" }}>
                    <strong style={{ fontSize: 24 }}>{b.min}m</strong>
                    <span style={{ fontSize: 11 }}>{b.label}</span>
                  </button>
                ))}
              </div>
            </div>
          </>
        )}

        {error && (
          <p role="alert" style={{ color: "var(--accent)", margin: "4px 0", fontSize: 13 }}>{error}</p>
        )}

        <div className="row" style={{ marginTop: 12 }}>
          <button className="btn" type="submit" disabled={busy}>
            {busy ? "Please wait…" : tab === "login" ? "Sign In" : "Create Account"}
          </button>
          <Link href="/start" className="btn ghost">Step-by-Step Setup</Link>
        </div>
      </form>
    </main>
  );
}

