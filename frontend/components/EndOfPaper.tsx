"use client";
import Link from "next/link";
import { useState } from "react";
import { api } from "@/lib/api";
import type { Edition } from "@/lib/types";

type Props = { edition: Edition; onNext: () => void; generating: boolean };

export default function EndOfPaper({ edition, onNext, generating }: Props) {
  const [answers, setAnswers] = useState<Record<number, number>>({});
  const done = edition.quiz.length > 0 && Object.keys(answers).length === edition.quiz.length;
  const score = edition.quiz.reduce((s, q, i) => s + (answers[i] === q.answer ? 1 : 0), 0);

  const pick = (i: number, o: number) => {
    if (answers[i] !== undefined) return;
    setAnswers((a) => ({ ...a, [i]: o }));
    const q = edition.quiz[i];
    api.event(o === q.answer ? "quiz_correct" : "quiz_wrong", { edition_id: edition.id, article_id: q.article_id });
  };

  return (
    <section className="end" aria-labelledby="end-h">
      <h2 id="end-h">That&apos;s the paper.</h2>
      <p className="sub">You&apos;re done for today. {edition.items.length} stories, about {edition.read_min} minutes.</p>
      <div className="btns">
        <a className="btn" href={api.pdfUrl(edition.id)} target="_blank" rel="noopener noreferrer">Download PDF</a>
        <Link className="btn ghost" href="/profile">See what it learned</Link>
        <button className="btn ghost" onClick={onNext} disabled={generating}>{generating ? "Printing…" : "Print another edition now"}</button>
      </div>

      {edition.quiz.length > 0 && (
        <div className="quiz">
          <div className="kicker">Recall</div>
          <h3>Can you name what you read?</h3>
          <p style={{ color: "var(--ink-2)", margin: 0 }}>Three questions. Your answers help shape tomorrow&apos;s paper.</p>
          {edition.quiz.map((q, i) => (
            <div className="q" key={i}>
              <p>{i + 1}. {q.q}</p>
              {q.options.map((o, oi) => {
                const chosen = answers[i];
                const cls = chosen === undefined ? "" : oi === q.answer ? "right" : chosen === oi ? "wrong" : "";
                return (
                  <button key={oi} className={`opt ${cls}`} disabled={chosen !== undefined} onClick={() => pick(i, oi)}>{o}</button>
                );
              })}
            </div>
          ))}
          {done && <div className="score">{score} of {edition.quiz.length} — {score === edition.quiz.length ? "you really read it." : score > 0 ? "not bad." : "tomorrow, then."}</div>}
        </div>
      )}
    </section>
  );
}
