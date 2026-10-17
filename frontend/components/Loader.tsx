"use client";
import { useEffect, useState } from "react";

const STEPS = [
  "Reading your interests",
  "Gathering today's articles",
  "Tagging topics and entities",
  "Scoring for relevance and freshness",
  "Fitting the paper to your time",
  "Writing headlines and notes",
  "Setting your type",
];

export default function Loader({ title = "Setting your type…" }: { title?: string }) {
  const [n, setN] = useState(0);
  useEffect(() => {
    const t = setInterval(() => setN((x) => Math.min(x + 1, STEPS.length - 1)), 750);
    return () => clearInterval(t);
  }, []);
  return (
    <div className="loader" role="status" aria-live="polite">
      <div className="mast">{title}</div>
      <ul>
        {STEPS.map((s, i) => (
          <li key={s} className={i < n ? "done" : i === n ? "cur" : ""}>{s}</li>
        ))}
      </ul>
    </div>
  );
}
