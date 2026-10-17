"use client";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import Loader from "@/components/Loader";
import Paper from "@/components/Paper";
import { api } from "@/lib/api";
import type { Edition } from "@/lib/types";

export default function EditionPage() {
  const { id } = useParams<{ id: string }>();
  const [ed, setEd] = useState<Edition | null>(null);
  const [err, setErr] = useState<"unauthorized" | "notfound" | null>(null);

  useEffect(() => {
    setEd(null);
    setErr(null);
    api.edition(id)
      .then(setEd)
      .catch((e: any) => {
        if (e?.status === 401) {
          setErr("unauthorized");
        } else {
          setErr("notfound");
        }
      });
  }, [id]);

  if (err === "unauthorized") return (
    <main className="narrow empty">
      <h2>Please Sign In</h2>
      <p>You need to be signed in to read this edition.</p>
      <div className="row" style={{ marginTop: 16 }}>
        <Link className="btn" href="/login">Sign In</Link>
        <Link className="btn ghost" href="/start">New Reader Setup</Link>
      </div>
    </main>
  );

  if (err === "notfound") return (
    <main className="narrow empty">
      <h2>Edition not found</h2>
      <p>This edition may belong to another reader or has expired.</p>
      <div className="row" style={{ marginTop: 16 }}>
        <Link className="btn" href="/paper">Today's Paper</Link>
        <Link className="btn ghost" href="/archive">Go to Archive</Link>
      </div>
    </main>
  );

  if (!ed) return <Loader title="Fetching the paper…" />;
  return <Paper key={ed.id} edition={ed} />;
}

