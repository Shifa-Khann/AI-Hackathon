"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { api, type SavedArticle } from "@/lib/api";
import { getToken } from "@/lib/session";

export default function SavedPage() {
  const [list, setList] = useState<SavedArticle[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");

  const loadSaved = () => {
    if (!getToken()) {
      setLoading(false);
      return;
    }
    setLoading(true);
    api.savedArticles()
      .then((r) => {
        setList(r.saved);
        setLoading(false);
      })
      .catch(() => {
        setErr("Could not load your saved articles. Please make sure you are signed in.");
        setLoading(false);
      });
  };

  useEffect(() => {
    loadSaved();
    const onSavedChanged = () => loadSaved();
    window.addEventListener("fold:saved_changed", onSavedChanged);
    window.addEventListener("fold:user_changed", onSavedChanged);
    return () => {
      window.removeEventListener("fold:saved_changed", onSavedChanged);
      window.removeEventListener("fold:user_changed", onSavedChanged);
    };
  }, []);

  const removeArticle = async (articleId: number) => {
    try {
      await api.unsaveArticle(articleId);
      setList((prev) => (prev ? prev.filter((a) => a.article_id !== articleId && a.id !== articleId) : []));
      window.dispatchEvent(
        new CustomEvent("fold:saved_changed", {
          detail: { article_id: articleId, saved: false },
        })
      );
    } catch {
      // ignore
    }
  };

  if (!getToken()) {
    return (
      <main className="narrow empty">
        <h2>Reader Account Required</h2>
        <p>Sign in to view and manage your private bookmarked news articles.</p>
        <Link className="btn" href="/login">Sign In</Link>
      </main>
    );
  }

  return (
    <main className="wrap page">
      <div className="kicker">Personal Archive</div>
      <h1>Saved News</h1>
      <p style={{ color: "var(--ink-2)", margin: "0 0 32px", maxWidth: 600 }}>
        Articles you&apos;ve bookmarked from your daily editions. Private to your account and stored forever.
      </p>

      {loading && <p className="label">Loading your saved stories…</p>}

      {err && (
        <div className="empty">
          <h2>Notice</h2>
          <p>{err}</p>
          <Link className="btn" href="/login">Sign In</Link>
        </div>
      )}

      {!loading && !err && list && list.length === 0 && (
        <div className="empty">
          <h2>No saved stories yet</h2>
          <p style={{ maxWidth: 440, margin: "8px auto 24px" }}>
            Whenever you see an interesting story in your morning paper, click the bookmark icon to save it here for later.
          </p>
          <Link className="btn" href="/paper">Read Today&apos;s Paper</Link>
        </div>
      )}

      {!loading && !err && list && list.length > 0 && (
        <div className="grid c3" style={{ borderTop: "1px solid var(--ink)", paddingTop: 16 }}>
          {list.map((item) => (
            <article key={item.saved_id} className="story" style={{ padding: "20px 20px 24px 0" }}>
              {item.image_url && (
                <div className="story-img" style={{ marginBottom: 12 }}>
                  <img src={item.image_url} alt={item.headline} loading="lazy" />
                </div>
              )}
              <div className="meta" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span>{item.source} · {item.read_min} min</span>
                <button
                  onClick={() => removeArticle(item.article_id || item.id)}
                  className="linkbtn"
                  style={{ color: "var(--accent)", fontSize: 11 }}
                  title="Remove from saved"
                >
                  Remove
                </button>
              </div>
              <h3 style={{ fontSize: 20, margin: "6px 0 8px" }}>
                {item.headline}
              </h3>
              <p className="dek" style={{ fontSize: 14, lineHeight: 1.5, margin: "0 0 14px" }}>
                {item.dek}
              </p>
              <div className="acts">
                <a
                  className="linkbtn"
                  href={item.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{ color: "var(--ink)" }}
                >
                  Read original &rarr;
                </a>
              </div>
            </article>
          ))}
        </div>
      )}
    </main>
  );
}
