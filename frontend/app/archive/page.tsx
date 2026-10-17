"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { EditionSummary } from "@/lib/types";

export default function Archive() {
  const [list, setList] = useState<EditionSummary[] | null>(null);
  const [err, setErr] = useState(false);

  useEffect(() => { api.editions().then((r) => setList(r.editions)).catch(() => setErr(true)); }, []);

  return (
    <main className="wrap page">
      <div className="kicker">Archive</div>
      <h1>Past editions</h1>
      <p style={{ color: "var(--ink-2)", margin: 0 }}>Every paper you&apos;ve been printed, newest first.</p>

      {err && <div className="empty"><h2>No archive yet</h2><p>Set up your paper first.</p><Link className="btn" href="/start">Make my paper</Link></div>}
      {list && list.length === 0 && <div className="empty"><h2>Nothing printed yet</h2><Link className="btn" href="/paper">Print today&apos;s edition</Link></div>}
      {list && list.length > 0 && (
        <div className="archive-list">
          {list.map((e) => (
            <div key={e.id} className="archive-row">
              <Link href={`/paper/${e.id}`} className="no" style={{ textDecoration: "none" }}>No. {e.number}</Link>
              <Link href={`/paper/${e.id}`} style={{ textDecoration: "none" }}>
                <h3>{e.lead_headline}</h3>
                <div className="m">{new Date(e.date + "T00:00:00").toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric" })} · {e.story_count} stories · {e.read_min} min</div>
              </Link>
              <a className="linkbtn pdf" href={api.pdfUrl(e.id)} target="_blank" rel="noopener noreferrer">PDF ↓</a>
            </div>
          ))}
        </div>
      )}
    </main>
  );
}
