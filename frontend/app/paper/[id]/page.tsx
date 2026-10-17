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
  const [err, setErr] = useState(false);

  useEffect(() => {
    setEd(null);
    api.edition(id).then(setEd).catch(() => setErr(true));
  }, [id]);

  if (err) return (
    <main className="narrow empty"><h2>Edition not found</h2><p>It may belong to another reader.</p><Link className="btn" href="/archive">Go to archive</Link></main>
  );
  if (!ed) return <Loader title="Fetching the paper…" />;
  return <Paper key={ed.id} edition={ed} />;
}
