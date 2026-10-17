"use client";
import Image from "next/image";
import { useEffect, useRef, useState } from "react";
import { api } from "@/lib/api";
import type { Item } from "@/lib/types";

type Props = { item: Item; editionId: number; lead?: boolean; saved?: boolean };

export default function Story({ item, editionId, lead, saved: initialSaved }: Props) {
  const [skipped, setSkipped] = useState(false);
  const [why, setWhy] = useState(false);
  const [challenge, setChallenge] = useState<"" | "more" | "less">("");
  const [imgError, setImgError] = useState(false);
  const [isSaved, setIsSaved] = useState(!!initialSaved);
  const ref = useRef<HTMLElement>(null);

  useEffect(() => {
    if (initialSaved !== undefined) {
      setIsSaved(initialSaved);
    }
  }, [initialSaved]);

  const toggleSave = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    const next = !isSaved;
    setIsSaved(next);
    try {
      if (next) {
        await api.saveArticle(item.article_id);
      } else {
        await api.unsaveArticle(item.article_id);
      }
      window.dispatchEvent(
        new CustomEvent("fold:saved_changed", {
          detail: { article_id: item.article_id, saved: next },
        })
      );
    } catch {
      setIsSaved(!next);
    }
  };

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

const SECTION_URDU: Record<string, string> = {
  "Top Story": "اہم ترین خبر",
  "World": "عالمی خبریں",
  "Technology": "ٹیکنالوجی",
  "Economy": "معیشت",
  "Science": "سائنس",
  "Culture": "ثقافت",
  "Sports": "کھیل",
  "Opinion": "رائے و تجزیہ",
  "Health": "صحت",
  "Markets": "مارکیٹ",
  "Politics": "سیاست",
  "Startups": "اسٹارٹ اپس",
  "Design": "ڈیزائن",
  "Cricket": "کرکٹ",
};

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
          : (isUrdu ? (SECTION_URDU[item.section] || item.section) : item.section)}
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
        <div className="skipnote">
          {isUrdu ? "چھوڑ دیا گیا — اب ایسی کم خبریں دکھائی جائیں گی۔" : "Skipped — less like this."}{" "}
          <button className="linkbtn" onClick={undo}>{isUrdu ? "واپس" : "Undo"}</button>
        </div>
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
            {isUrdu ? "اصل خبر پڑھیں ←" : "Read original →"}
          </a>
          <button
            className="linkbtn save-btn"
            onClick={toggleSave}
            title={isSaved ? (isUrdu ? "محفوظ شدہ خبر ہٹائیں" : "Remove from saved") : (isUrdu ? "یہ خبر محفوظ کریں" : "Save article")}
            style={{ display: "inline-flex", alignItems: "center", gap: 5, color: isSaved ? "var(--accent)" : "var(--ink)" }}
            aria-pressed={isSaved}
          >
            <svg
              width="13"
              height="13"
              viewBox="0 0 24 24"
              fill={isSaved ? "currentColor" : "none"}
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" />
            </svg>
            <span>{isSaved ? (isUrdu ? "محفوظ شدہ" : "Saved") : (isUrdu ? "محفوظ کریں" : "Save")}</span>
          </button>
          <button className="linkbtn" aria-expanded={why} onClick={() => setWhy((w) => !w)}>
            {isUrdu ? "یہ خبر کیوں؟" : "Why this?"}
          </button>
          <button className="linkbtn" onClick={skip}>
            {isUrdu ? "چھوڑیں" : "Skip"}
          </button>
        </div>
      )}

      {why && !skipped && (
        <p className="why" style={isUrdu ? { fontFamily: '"Noto Nastaliq Urdu", serif', fontSize: 15, lineHeight: 1.8 } : undefined}>
          {item.why}
        </p>
      )}

      {item.is_blind_spot && !skipped && (
        <div className="challenge">
          <span>{isUrdu ? "کتنا چیلنج چاہیے؟" : "How much challenge?"}</span>
          <button className="btn ghost sm" aria-pressed={challenge === "more"} onClick={() => give("more")}>
            {isUrdu ? "زیادہ" : "More"}
          </button>
          <button className="btn ghost sm" aria-pressed={challenge === "less"} onClick={() => give("less")}>
            {isUrdu ? "کم" : "Less"}
          </button>
          {challenge && <span>{isUrdu ? "نوٹ کر لیا گیا۔" : "Noted."}</span>}
        </div>
      )}
    </article>
  );
}
