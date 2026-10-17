"use client";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { Edition, Item } from "@/lib/types";
import EndOfPaper from "./EndOfPaper";
import Story from "./Story";

export default function Paper({ edition }: { edition: Edition }) {
  const router = useRouter();
  const [pct, setPct] = useState(0);
  const [generating, setGenerating] = useState(false);
  const [urdu, setUrdu] = useState(false);
  const [translating, setTranslating] = useState(false);
  const [urduItems, setUrduItems] = useState<Record<number, { headline: string; dek: string; why?: string }>>({});

  useEffect(() => {
    const on = () => {
      const h = document.documentElement;
      setPct(Math.min(100, (h.scrollTop / Math.max(1, h.scrollHeight - h.clientHeight)) * 100));
    };
    window.addEventListener("scroll", on, { passive: true });
    return () => window.removeEventListener("scroll", on);
  }, []);

  const [savedSet, setSavedSet] = useState<Set<number>>(new Set());

  useEffect(() => {
    api.savedIds()
      .then((r) => setSavedSet(new Set(r.saved_ids)))
      .catch(() => {});

    const onSavedChanged = (e: any) => {
      const { article_id, saved } = e.detail || {};
      if (article_id !== undefined) {
        setSavedSet((prev) => {
          const next = new Set(prev);
          if (saved) next.add(article_id);
          else next.delete(article_id);
          return next;
        });
      }
    };
    window.addEventListener("fold:saved_changed", onSavedChanged);
    return () => window.removeEventListener("fold:saved_changed", onSavedChanged);
  }, []);

  const next = async () => {
    setGenerating(true);
    try {
      const ed = await api.generate();
      window.scrollTo({ top: 0 });
      router.push(`/paper/${ed.id}`);
    } finally {
      setGenerating(false);
    }
  };

  const toggleUrdu = async () => {
    if (!urdu && Object.keys(urduItems).length === 0) {
      setTranslating(true);
      try {
        await api.translate(edition.id);
        // Fetch the updated edition to get Urdu headlines, deks, and whys
        const fresh = await api.edition(edition.id);
        const map: Record<number, { headline: string; dek: string; why?: string }> = {};
        for (const it of fresh.items) {
          if (it.headline_ur) {
            map[it.id] = {
              headline: it.headline_ur,
              dek: it.dek_ur || it.dek,
              why: it.why_ur || it.why,
            };
          }
        }
        setUrduItems(map);
      } catch {
        // Silently fall back to English
      } finally {
        setTranslating(false);
      }
    }
    setUrdu((u) => !u);
  };

  const applyUrdu = (item: Item): Item => {
    if (!urdu) return item;
    const tr = urduItems[item.id] || (item.headline_ur ? { headline: item.headline_ur, dek: item.dek_ur || item.dek, why: item.why_ur || item.why } : null);
    if (!tr) return item;
    return { ...item, headline: tr.headline, dek: tr.dek, why: tr.why || item.why };
  };


  const normal = edition.items.filter((i) => !i.is_blind_spot);
  const blind = edition.items.find((i) => i.is_blind_spot);
  const [lead, ...rest] = normal;
  const cols = edition.plan?.columns === 2 ? "c2" : "c3";
  const wide = edition.plan?.hero_style === "wide";
  const side = wide ? [] : rest.slice(0, 2);
  const grid = wide ? rest : rest.slice(2);
  const when = new Date(edition.date + "T00:00:00").toLocaleDateString("en-GB", {
    weekday: "long", day: "numeric", month: "long", year: "numeric",
  });

  return (
    <main className="wrap">
      <div className="progressbar" style={{ width: `${pct}%` }} aria-hidden />
      <header className="masthead">
        <div className="label" style={{ marginBottom: 6 }}>A paper that ends</div>
        <h1>The Fold</h1>
      </header>
      <div className="dateline">
        <span>{when}</span>
        <span><b>Edition No. {edition.number}</b></span>
        <span>{edition.items.length} stories · {edition.read_min} min</span>
      </div>

      {edition.editor_note && <p className="note">{edition.editor_note}</p>}
      {edition.todo && <div className="todo"><b>One thing to do today</b> {edition.todo}</div>}
      <div className="actions-top">
        <a className="btn ghost sm" href={api.pdfUrl(edition.id)} target="_blank" rel="noopener noreferrer">
          Download PDF
        </a>
        <button
          className="btn ghost sm"
          onClick={toggleUrdu}
          disabled={translating}
          title="Toggle Urdu headlines"
          aria-pressed={urdu}
          style={urdu ? { borderColor: "var(--accent)", color: "var(--accent)" } : undefined}
        >
          {translating ? "Translating…" : urdu ? "اردو (فعال)" : "اردو"}
        </button>
      </div>

      {lead && (
        <section className={`front ${wide ? "wide" : ""}`}>
          <div className="lead">
            <Story item={applyUrdu(lead)} editionId={edition.id} lead saved={savedSet.has(lead.article_id)} />
          </div>
          {side.length > 0 && (
            <div className="side">
              {side.map((s) => (
                <div key={s.id} style={{ paddingBottom: 24 }}>
                  <Story item={applyUrdu(s)} editionId={edition.id} saved={savedSet.has(s.article_id)} />
                </div>
              ))}
            </div>
          )}
        </section>
      )}

      {grid.length > 0 && (
        <section className={`grid ${cols}`}>
          {grid.map((s) => (
            <Story key={s.id} item={applyUrdu(s)} editionId={edition.id} saved={savedSet.has(s.article_id)} />
          ))}
        </section>
      )}

      {blind && <Story item={applyUrdu(blind)} editionId={edition.id} saved={savedSet.has(blind.article_id)} />}

      <EndOfPaper edition={edition} onNext={next} generating={generating} />
    </main>
  );
}
