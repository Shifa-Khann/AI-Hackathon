"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { getUid, setUid } from "@/lib/session";

export default function Landing() {
  const [hasUser, setHasUser] = useState(false);

  useEffect(() => {
    // demo helper: /?uid=2 switches persona
    const q = new URLSearchParams(window.location.search).get("uid");
    if (q && /^\d+$/.test(q)) {
      setUid(q);
      window.location.replace("/paper");
      return;
    }
    setHasUser(!!getUid());
  }, []);

  return (
    <main className="wrap">
      <section className="hero-landing">
        <div className="label" style={{ marginBottom: 20 }}>Your morning paper</div>
        <h1>The Fold</h1>
        <div className="tagline">A paper that ends.</div>
        <p className="lede">
          The articles that matter to you, from across the web, set into one edition — sized to your morning, and finished when you are.
        </p>
        <div style={{ display: "flex", gap: 12, justifyContent: "center", flexWrap: "wrap" }}>
          <Link href="/start" className="btn">Make my paper</Link>
          {hasUser && <Link href="/paper" className="btn ghost">Read today&apos;s edition</Link>}
        </div>
      </section>
      <section className="pillars" aria-label="What makes it different">
        <div>
          <div className="kicker">01</div>
          <h3>It ends.</h3>
          <p>No infinite scroll. Your edition fits the minutes you have, then closes with a clear full stop.</p>
        </div>
        <div>
          <div className="kicker">02</div>
          <h3>It explains itself.</h3>
          <p>Every story says why it&apos;s there, in your own words or from what you actually read.</p>
        </div>
        <div>
          <div className="kicker">03</div>
          <h3>It learns.</h3>
          <p>Skip a topic and tomorrow&apos;s paper changes. Watch your interest graph grow with every edition.</p>
        </div>
      </section>
    </main>
  );
}
