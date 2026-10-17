"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { api } from "@/lib/api";
import { setUid } from "@/lib/session";

export default function LoginPage() {
  const router = useRouter();
  const [tab, setTab] = useState<"login" | "signup">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [budget, setBudget] = useState<5 | 12 | 20>(12);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setBusy(true);

    try {
      if (tab === "login") {
        const res = await api.login({ email, password });
        setUid(res.user_id);
        if (typeof window !== "undefined") {
          window.dispatchEvent(new Event("fold:user_changed"));
        }
        router.push("/paper");
      } else {
        const res = await api.signup({ email, password, name: name.trim() || undefined, budget_min: budget });
        setUid(res.user_id);
        if (typeof window !== "undefined") {
          window.dispatchEvent(new Event("fold:user_changed"));
        }
        router.push("/paper");
      }
    } catch (err: any) {
      setBusy(false);
      setError(err?.message || "Invalid credentials. Please try again.");
    }
  };

  const loginDemo = async (demoName: "Ayesha" | "Bilal") => {
    setError("");
    setBusy(true);
    try {
      const res = await api.login({ email: demoName.toLowerCase(), password: "password123" });
      setUid(res.user_id);
      if (typeof window !== "undefined") {
        window.dispatchEvent(new Event("fold:user_changed"));
      }
      router.push("/paper");
    } catch {
      setBusy(false);
      setError(`Could not log in as ${demoName}.`);
    }
  };

  return (
    <main className="narrow onb">
      <div className="kicker">Reader Account</div>
      <h1 style={{ marginBottom: 12 }}>{tab === "login" ? "Sign in to The Fold" : "Create your reader account"}</h1>
      <p className="sub" style={{ marginBottom: 24 }}>
        {tab === "login"
          ? "Access your personal morning newspaper and reading history."
          : "Register to get a daily finite newspaper shaped by your reading."}
      </p>

      {/* Tabs */}
      <div style={{ display: "flex", gap: 10, marginBottom: 24, borderBottom: "1px solid var(--rule)", paddingBottom: 10 }}>
        <button
          className="linkbtn"
          style={{
            fontSize: 14,
            color: tab === "login" ? "var(--accent)" : "var(--ink-2)",
            borderBottom: tab === "login" ? "2px solid var(--accent)" : "none",
            paddingBottom: 6,
          }}
          onClick={() => { setTab("login"); setError(""); }}
        >
          Sign In
        </button>
        <button
          className="linkbtn"
          style={{
            fontSize: 14,
            color: tab === "signup" ? "var(--accent)" : "var(--ink-2)",
            borderBottom: tab === "signup" ? "2px solid var(--accent)" : "none",
            paddingBottom: 6,
          }}
          onClick={() => { setTab("signup"); setError(""); }}
        >
          Create Account
        </button>
      </div>

      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        {tab === "signup" && (
          <div>
            <label className="label" htmlFor="name" style={{ display: "block", marginBottom: 6 }}>
              Full Name (optional)
            </label>
            <input
              id="name"
              type="text"
              className="field"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Ayesha Khan"
            />
          </div>
        )}

        <div>
          <label className="label" htmlFor="email" style={{ display: "block", marginBottom: 6 }}>
            Email address
          </label>
          <input
            id="email"
            type="email"
            required
            className="field"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
          />
        </div>

        <div>
          <label className="label" htmlFor="password" style={{ display: "block", marginBottom: 6 }}>
            Password
          </label>
          <input
            id="password"
            type="password"
            required
            className="field"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
          />
        </div>

        {tab === "signup" && (
          <div style={{ marginTop: 8 }}>
            <label className="label" style={{ display: "block", marginBottom: 8 }}>
              Morning Reading Budget
            </label>
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
                  style={{ padding: "12px 6px" }}
                >
                  <strong style={{ fontSize: 24 }}>{b.min}m</strong>
                  <span style={{ fontSize: 11 }}>{b.label}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {error && (
          <p role="alert" style={{ color: "var(--accent)", margin: "4px 0", fontSize: 13 }}>
            {error}
          </p>
        )}

        <div className="row" style={{ marginTop: 12 }}>
          <button className="btn" type="submit" disabled={busy}>
            {busy ? "Please wait…" : tab === "login" ? "Sign In" : "Create Account & Print"}
          </button>
          <Link href="/start" className="btn ghost">
            Or Use Step-by-Step Setup
          </Link>
        </div>
      </form>

      {/* Quick Demo Access */}
      <section style={{ marginTop: 48, paddingTop: 24, borderTop: "1px solid var(--rule)" }}>
        <div className="kicker">Demo Readers</div>
        <p style={{ fontSize: 13, color: "var(--ink-2)", margin: "4px 0 14px" }}>
          Instant 1-click test sign in with pre-generated editions:
        </p>
        <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
          <button className="chip" onClick={() => loginDemo("Ayesha")} disabled={busy}>
            👤 <strong>Ayesha</strong> (Islamabad · Tech & AI)
          </button>
          <button className="chip" onClick={() => loginDemo("Bilal")} disabled={busy}>
            👤 <strong>Bilal</strong> (Karachi · Markets & Economy)
          </button>
        </div>
      </section>
    </main>
  );
}
