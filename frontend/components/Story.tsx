"use client";
import Image from "next/image";
import { useEffect, useRef, useState } from "react";
import { api } from "@/lib/api";
import type { Item } from "@/lib/types";

type Props = { item: Item; editionId: number; lead?: boolean };

export default function Story({ item, editionId, lead }: Props) {
  const [skipped, setSkipped] = useState(false);
  const [why, setWhy] = useState(false);
  const [challenge, setChallenge] = useState<"" | "more" | "less">("");
  const [imgError, setImgError] = useState(false);
  const ref = useRef<HTMLElement>(null);

  // dwell: report seconds when the story was >= 60% visible, once, on leave/unmount
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    let since = 0, total = 0, sent = false;
    const flush = () => { if (since) { total += (Date.now() - since) / 1000; since = 0; } };
    const send = () => {
      flush();
      if (!sent && total >= 8) { sent = true; api.event("dwell", { edition_id: editionId, article_id: item.article_id, value: Math.round(total) }); }
    };
    const io = new IntersectionObserver(([e]) => {
      if (e.intersectionRatio >= 0.6) { if (!since) since = Date.now(); } else flush();
    }, { threshold: [0, 0.6, 1] });
    io.observe(el);
    const onHide = () => document.visibilityState === "hidden" && send();
    document.addEventListener("visibilitychange", onHide);
    window.addEventListener("pagehide", send);
    return () => { io.disconnect(); document.removeEventListener("visibilitychange", onHide); window.removeEventListener("pagehide", send); send(); };
  }, [editionId, item.article_id]);

  const skip = () => { setSkipped(true); api.event("skip", { edition_id: editionId, article_id: item.article_id }); };
  const undo = () => { setSkipped(false); api.event("unskip", { edition_id: editionId, article_id: item.article_id }); };
  const open = () => api.event("open", { edition_id: editionId, article_id: item.article_id });
  const give = (c: "more" | "less") => { setChallenge(c); api.event(c === "more" ? "more_challenge" : "less_challenge", { edition_id: editionId }); };

  const H = lead ? "h2" : "h3";
  const isUrdu = /[\u0600-\u06FF]/.test(item.headline);
  const showImage = !skipped && item.image_url && !imgError;

  return (
    <article
      ref={ref}
      dir={isUrdu ? "rtl" : "ltr"}
      className={`story ${lead ? "lead-story" : ""} ${skipped ? "skipped" : ""} ${item.is_blind_spot ? "blind" : ""} ${isUrdu ? "urdu-mode" : ""}`}
    >
      {/* Photo — only on lead or if image available and not skipped */}
      {showImage && (
        <div className={`story-img${lead ? " story-img-lead" : ""}`}>
          <img
            src={item.image_url!}
            alt={item.headline}
            loading="lazy"
            onError={() => setImgError(true)}
          />
        </div>
      )}

      <div className="kicker">
        {item.is_blind_spot
          ? (isUrdu ? "بلائنڈ اسپاٹ — آپ کی معمول کی پڑھائی سے باہر" : "Blind spot — outside your usual reading")
          : item.section}
      </div>

      <H style={isUrdu ? { fontFamily: '"Noto Nastaliq Urdu", serif', lineHeight: 1.5, fontSize: lead ? 32 : 22 } : undefined}>
        {item.headline}
      </H>

      {!skipped && (
        <p className="dek" style={isUrdu ? { fontFamily: '"Noto Nastaliq Urdu", serif', fontSize: 16, lineHeight: 1.9 } : undefined}>
          {item.dek}
        </p>
      )}

      <div className="meta">{item.source} · {item.read_min} {isUrdu ? "منٹ" : "min"}</div>

      {skipped ? (
        <div className="skipnote">Skipped — less like this. <button className="linkbtn" onClick={undo}>Undo</button></div>
      ) : (
        <div className="acts">
          <a
            className="linkbtn"
            href={item.url}
            target="_blank"
            rel="noopener noreferrer"
            onClick={open}
            style={{ color: "var(--ink)" }}
          >
            Read original &rarr;
          </a>
          <button className="linkbtn" aria-expanded={why} onClick={() => setWhy((w) => !w)}>Why this?</button>
          <button className="linkbtn" onClick={skip}>Skip</button>
        </div>
      )}

      {why && !skipped && <p className="why">{item.why}</p>}

      {item.is_blind_spot && !skipped && (
        <div className="challenge">
          <span>How much challenge?</span>
          <button className="btn ghost sm" aria-pressed={challenge === "more"} onClick={() => give("more")}>More</button>
          <button className="btn ghost sm" aria-pressed={challenge === "less"} onClick={() => give("less")}>Less</button>
          {challenge && <span>Noted.</span>}
        </div>
      )}
    </article>
  );
}
