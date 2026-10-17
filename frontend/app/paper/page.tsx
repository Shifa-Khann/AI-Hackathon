"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import Loader from "@/components/Loader";
import Paper from "@/components/Paper";
import { api } from "@/lib/api";
import { getUid } from "@/lib/session";
import type { Edition } from "@/lib/types";

/** /paper -> smoothly render the latest edition, printing one if the reader has none yet. */
export default function Today() {
  const router = useRouter();
  const [state, setState] = useState<"loading" | "nouser" | "error">("loading");
  const [msg, setMsg] = useState("Fetching your morning edition…");
  const [edition, setEdition] = useState<Edition | null>(null);

  useEffect(() => {
    const uid = getUid();
    if (!uid) {
      setState("nouser");
      return;
    }
    let cancelled = false;

    (async () => {
      try {
        let ed: Edition;
        try {
          ed = await api.latest();
        } catch (e: any) {
          if (e?.status === 404) {
            setMsg("Printing your first morning edition… (this takes a few seconds)");
            ed = await api.generate();
          } else {
            throw e;
          }
        }
        if (!cancelled && ed) {
          setEdition(ed);
          // Silently update URL to the canonical edition path without triggering full page reload
          if (typeof window !== "undefined") {
            window.history.replaceState(null, "", `/paper/${ed.id}`);
          }
        }
      } catch (e: any) {
        if (!cancelled) {
          setState(e?.status === 401 ? "nouser" : "error");
        }
      }
    })();

    return () => {
      cancelled = true;
    };
  }, []);

  if (edition) return <Paper key={edition.id} edition={edition} />;
  if (state === "loading") return <Loader title={msg} />;

  return (
    <main className="narrow empty">
      <h2>{state === "nouser" ? "Sign in to read your paper" : "Can't reach the press"}</h2>
      <p>
        {state === "nouser"
          ? "Log in or create a reader account to view your personalized daily paper."
          : "Could not connect to the printing press. Ensure the backend server is running on port 8000."}
      </p>
      <div className="row" style={{ marginTop: 16 }}>
        {state === "nouser" ? (
          <>
            <Link className="btn" href="/login">Sign In / Register</Link>
            <Link className="btn ghost" href="/start">New Reader Setup</Link>
          </>
        ) : (
          <button className="btn" onClick={() => window.location.reload()}>Try Again</button>
        )}
      </div>
    </main>
  );
}

