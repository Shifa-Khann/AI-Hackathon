"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import Loader from "@/components/Loader";
import { api } from "@/lib/api";
import { getUid } from "@/lib/session";

/** /paper -> redirect to the latest edition, printing one if the reader has none yet. */
export default function Today() {
  const router = useRouter();
  const [state, setState] = useState<"loading" | "nouser" | "error">("loading");

  useEffect(() => {
    if (!getUid()) { setState("nouser"); return; }
    (async () => {
      try {
        let ed;
        try { ed = await api.latest(); }
        catch (e) { if ((e as { status?: number }).status === 404) ed = await api.generate(); else throw e; }
        router.replace(`/paper/${ed.id}`);
      } catch (e) {
        setState((e as { status?: number }).status === 401 ? "nouser" : "error");
      }
    })();
  }, [router]);

  if (state === "loading") return <Loader />;
  return (
    <main className="narrow empty">
      <h2>{state === "nouser" ? "Let's set your paper first" : "Can't reach the press"}</h2>
      <p>{state === "nouser" ? "It takes about a minute." : "Check that the backend is running on port 8000."}</p>
      <Link className="btn" href="/start">Make my paper</Link>
    </main>
  );
}
