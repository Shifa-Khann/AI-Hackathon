"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { api } from "@/lib/api";
import { clearUid, getUid, setUid } from "@/lib/session";

const LINKS = [
  { href: "/paper", label: "Today" },
  { href: "/archive", label: "Archive" },
  { href: "/profile", label: "Profile" },
];

export default function Nav() {
  const path = usePathname() || "";
  const router = useRouter();
  const [currentUser, setCurrentUser] = useState<string | null>(null);
  const [userList, setUserList] = useState<Array<{ id: number; name: string | null; budget_min: number }>>([]);
  const [open, setOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const uid = getUid();
    if (uid) {
      api.profile().then((r) => setCurrentUser(r.user.name || `Reader #${r.user.id}`)).catch(() => setCurrentUser(null));
    } else {
      setCurrentUser(null);
    }
  }, [path]);

  const toggleMenu = () => {
    if (!open) {
      api.users().then((r) => setUserList(r.users)).catch(() => {});
    }
    setOpen((o) => !o);
  };

  const switchUser = (id: number) => {
    setUid(id);
    setOpen(false);
    window.location.href = `/paper?refresh=${Date.now()}`;
  };

  const logout = () => {
    clearUid();
    setCurrentUser(null);
    setOpen(false);
    router.push("/");
  };

  // Close popup if clicking outside
  useEffect(() => {
    const onDocClick = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", onDocClick);
    return () => document.removeEventListener("mousedown", onDocClick);
  }, []);

  return (
    <nav className="nav" aria-label="Main">
      <div className="wrap">
        <Link href="/" className="brand">The Fold</Link>
        <div className="links" style={{ alignItems: "center" }}>
          {LINKS.map((l) => (
            <Link key={l.href} href={l.href} className={path.startsWith(l.href) ? "on" : ""}>{l.label}</Link>
          ))}

          {/* User Account / Switcher */}
          <div ref={menuRef} style={{ position: "relative", marginLeft: 8 }}>
            <button
              onClick={toggleMenu}
              className="chip"
              style={{
                fontSize: 11,
                padding: "4px 10px",
                display: "inline-flex",
                alignItems: "center",
                gap: 5,
                borderColor: open ? "var(--ink)" : "var(--rule)",
                background: "var(--paper-2)",
              }}
              title="Switch reader profile"
              aria-expanded={open}
            >
              <span>👤</span>
              <span>{currentUser ? currentUser : "Sign In"}</span>
              <span style={{ fontSize: 9 }}>▼</span>
            </button>

            {open && (
              <div
                style={{
                  position: "absolute",
                  right: 0,
                  top: "100%",
                  marginTop: 6,
                  background: "var(--paper)",
                  border: "1px solid var(--rule)",
                  boxShadow: "0 8px 24px rgba(0,0,0,0.12)",
                  borderRadius: 3,
                  minWidth: 220,
                  zIndex: 100,
                  padding: 8,
                }}
              >
                <div className="label" style={{ padding: "6px 10px 4px", borderBottom: "1px solid var(--rule)" }}>
                  Reader Accounts
                </div>
                <div style={{ maxHeight: 200, overflowY: "auto", margin: "4px 0" }}>
                  {userList.map((u) => {
                    const isCur = String(u.id) === getUid();
                    return (
                      <button
                        key={u.id}
                        onClick={() => switchUser(u.id)}
                        style={{
                          width: "100%",
                          textAlign: "left",
                          padding: "8px 10px",
                          border: 0,
                          background: isCur ? "var(--accent-soft)" : "transparent",
                          color: isCur ? "var(--accent)" : "var(--ink)",
                          fontSize: 13,
                          borderRadius: 2,
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                          cursor: "pointer",
                        }}
                      >
                        <span style={{ fontWeight: isCur ? 700 : 500 }}>
                          {u.name || `Reader #${u.id}`}
                        </span>
                        <span style={{ fontSize: 11, color: "var(--ink-2)" }}>
                          {u.budget_min}m
                        </span>
                      </button>
                    );
                  })}
                </div>

                <div style={{ borderTop: "1px solid var(--rule)", paddingTop: 6, display: "flex", flexDirection: "column", gap: 4 }}>
                  <Link
                    href="/start"
                    onClick={() => setOpen(false)}
                    className="linkbtn"
                    style={{ padding: "6px 10px", color: "var(--accent)", fontSize: 11 }}
                  >
                    + New Reader (Sign Up)
                  </Link>
                  {currentUser && (
                    <button
                      onClick={logout}
                      className="linkbtn"
                      style={{ textAlign: "left", padding: "6px 10px", fontSize: 11, color: "var(--ink-2)" }}
                    >
                      Log Out (Guest Mode)
                    </button>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}

