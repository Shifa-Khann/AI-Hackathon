"use client";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import Loader from "@/components/Loader";
import { api } from "@/lib/api";
import { setUid } from "@/lib/session";
import type { Topic } from "@/lib/types";

const BUDGETS: { min: 5 | 12 | 20; note: string }[] = [
  { min: 5, note: "Headlines & essentials" },
  { min: 12, note: "A proper breakfast read" },
  { min: 20, note: "The full broadsheet" },
];

export default function Start() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [recent, setRecent] = useState("");
  const [name, setName] = useState("");
  const [picked, setPicked] = useState<string[]>([]);
  const [other, setOther] = useState("");
  const [budget, setBudget] = useState<5 | 12 | 20>(12);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    api.topics().then((r) => setTopics(r.topics)).catch(() => setError("Can't reach the server. Is the backend running on :8000?"));
  }, []);

  const toggle = (id: string) => setPicked((p) => (p.includes(id) ? p.filter((x) => x !== id) : [...p, id]));

  async function finish() {
    setBusy(true);
    setError("");
    try {
      const { user_id } = await api.onboard({ name: name.trim() || undefined, recent_read: recent.trim() || undefined, topics: picked, other: other.trim() || undefined, budget_min: budget });
      setUid(user_id);
      const ed = await api.generate();
      router.push(`/paper/${ed.id}`);
    } catch {
      setBusy(false);
      setError("Something went wrong setting your paper. Please try again.");
    }
  }

  if (busy) return <Loader />;

  return (
    <main className="narrow onb">
      <div className="progress" aria-hidden>
        {[0, 1, 2].map((i) => <span key={i} className={i <= step ? "on" : ""} />)}
      </div>

      {step === 0 && (
        <section>
          <div className="kicker">Step 1 of 3</div>
          <h1>What did you read recently that stuck with you?</h1>
          <p className="sub">A sentence is plenty. It helps us choose your first stories — and we&apos;ll quote it back to explain why.</p>
          <label className="label" htmlFor="recent" style={{ display: "block", marginBottom: 8 }}>Optional</label>
          <textarea id="recent" className="field" value={recent} onChange={(e) => setRecent(e.target.value)} placeholder="e.g. A piece on how AI policy is changing Pakistan's startup scene…" />
          <div style={{ marginTop: 16 }}>
            <label className="label" htmlFor="name" style={{ display: "block", marginBottom: 8 }}>What should we call you? (optional)</label>
            <input id="name" className="field" value={name} onChange={(e) => setName(e.target.value)} placeholder="Your name" />
          </div>
          <div className="row"><button className="btn" onClick={() => setStep(1)}>Continue</button></div>
        </section>
      )}

      {step === 1 && (
        <section>
          <div className="kicker">Step 2 of 3</div>
          <h1>What do you like to follow?</h1>
          <p className="sub">Pick a few. You can always change this later — your reading will refine it.</p>
          <div className="chips">
            {topics.map((t) => (
              <button key={t.id} className="chip" aria-pressed={picked.includes(t.id)} onClick={() => toggle(t.id)}>{t.label}</button>
            ))}
          </div>
          <div style={{ marginTop: 20 }}>
            <label className="label" htmlFor="other" style={{ display: "block", marginBottom: 8 }}>Something else?</label>
            <input id="other" className="field" value={other} onChange={(e) => setOther(e.target.value)} placeholder="e.g. chess, semiconductors, urban planning" />
          </div>
          <div className="row">
            <button className="btn ghost" onClick={() => setStep(0)}>Back</button>
            <button className="btn" disabled={picked.length === 0 && !other.trim() && !recent.trim()} onClick={() => setStep(2)}>Continue</button>
          </div>
        </section>
      )}

      {step === 2 && (
        <section>
          <div className="kicker">Step 3 of 3</div>
          <h1>How long is your morning?</h1>
          <p className="sub">We&apos;ll size the paper to fit — and end it there.</p>
          <div className="budget" role="group" aria-label="Reading time">
            {BUDGETS.map((b) => (
              <button key={b.min} aria-pressed={budget === b.min} onClick={() => setBudget(b.min)}>
                <strong>{b.min}</strong><span>minutes · {b.note}</span>
              </button>
            ))}
          </div>
          {error && <p role="alert" style={{ color: "var(--accent)", marginTop: 20 }}>{error}</p>}
          <div className="row">
            <button className="btn ghost" onClick={() => setStep(1)}>Back</button>
            <button className="btn" onClick={finish}>Print my first edition</button>
          </div>
        </section>
      )}
      {step !== 2 && error && <p role="alert" style={{ color: "var(--accent)", marginTop: 20 }}>{error}</p>}
    </main>
  );
}
