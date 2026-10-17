"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { api } from "@/lib/api";
import { clearSession, getToken } from "@/lib/session";

const LINKS = [
  { href: "/paper", label: "Today" },
  { href: "/saved", label: "Saved" },
  { href: "/archive", label: "Archive" },
  { href: "/profile", label: "Profile" },
];

export default function Nav() {
  const path = usePathname() || "";
  const router = useRouter();
  const [currentUser, setCurrentUser] = useState<{ name: string; email?: string } | null>(null);
  const [open, setOpen] = useState(false);
  const [theme, setTheme] = useState<"light" | "dark">("light");
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const saved = localStorage.getItem("thefold_theme") as "light" | "dark" | null;
    const initial = saved || "light";
    setTheme(initial);
    document.documentElement.setAttribute("data-theme", initial);
  }, []);

  const toggleTheme = () => {
    const next = theme === "light" ? "dark" : "light";
    setTheme(next);
    localStorage.setItem("thefold_theme", next);
    document.documentElement.setAttribute("data-theme", next);
  };

  useEffect(() => {
    const update = () => {
      const token = getToken();
      if (token) {
        api.profile()
          .then((r) => {
            setCurrentUser({
              name: r.user.name || "Reader",
              email: r.user.email || undefined,
            });
          })
          .catch(() => setCurrentUser(null));
      } else {
        setCurrentUser(null);
      }
    };
    update();
    window.addEventListener("fold:user_changed", update);
    return () => window.removeEventListener("fold:user_changed", update);
  }, [path]);

  const toggleMenu = () => {
    if (!currentUser) {
      router.push("/login");
      return;
    }
    setOpen((o) => !o);
  };

  const logout = async () => {
    try {
      await api.logout();
    } catch {
      // ignore
    }
    clearSession();
    setCurrentUser(null);
    setOpen(false);
    window.dispatchEvent(new Event("fold:user_changed"));
    router.push("/login");
  };

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

          {/* Theme Toggle — text only */}
          <button
            onClick={toggleTheme}
            className="chip"
            style={{ fontSize: 11, padding: "4px 10px", cursor: "pointer", background: "var(--paper-2)", display: "inline-flex", alignItems: "center", gap: 4 }}
            title={theme === "light" ? "Switch to Dark Mode" : "Switch to Light Mode"}
            aria-label="Toggle theme"
          >
            <span style={{ fontSize: 10, textTransform: "uppercase", letterSpacing: "0.08em", fontWeight: 600 }}>
              {theme === "light" ? "Dark" : "Light"}
            </span>
          </button>

          {/* User Account Menu — Private, No other users exposed */}
          <div ref={menuRef} style={{ position: "relative" }}>
            <button
              onClick={toggleMenu}
              className="chip"
              style={{
                fontSize: 11,
                padding: "4px 12px",
                display: "inline-flex",
                alignItems: "center",
                gap: 6,
                borderColor: open ? "var(--ink)" : "var(--rule)",
                background: "var(--paper-2)",
              }}
              title={currentUser ? "My Account" : "Sign in to The Fold"}
              aria-expanded={open}
            >
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/>
              </svg>
              <span>{currentUser ? currentUser.name : "Sign In"}</span>
              {currentUser && <span style={{ fontSize: 9 }}>&#9660;</span>}
            </button>

            {open && currentUser && (
              <div style={{ position: "absolute", right: 0, top: "100%", marginTop: 6, background: "var(--paper)", border: "1px solid var(--rule)", boxShadow: "0 8px 24px rgba(0,0,0,0.14)", borderRadius: 3, minWidth: 220, zIndex: 100, padding: 8 }}>
                <div style={{ padding: "8px 10px", borderBottom: "1px solid var(--rule)", marginBottom: 6 }}>
                  <div style={{ fontWeight: 600, fontSize: 13, color: "var(--ink)" }}>{currentUser.name}</div>
                  {currentUser.email && (
                    <div style={{ fontSize: 11, color: "var(--ink-2)", overflow: "hidden", textOverflow: "ellipsis" }}>
                      {currentUser.email}
                    </div>
                  )}
                </div>

                <div style={{ display: "flex", flexDirection: "column", gap: 3 }}>
                  <Link
                    href="/saved"
                    onClick={() => setOpen(false)}
                    className="linkbtn"
                    style={{ padding: "6px 10px", color: "var(--ink)", fontSize: 12, textAlign: "left" }}
                  >
                    Saved News
                  </Link>
                  <Link
                    href="/profile"
                    onClick={() => setOpen(false)}
                    className="linkbtn"
                    style={{ padding: "6px 10px", color: "var(--ink)", fontSize: 12, textAlign: "left" }}
                  >
                    Profile &amp; Settings
                  </Link>
                  <Link
                    href="/archive"
                    onClick={() => setOpen(false)}
                    className="linkbtn"
                    style={{ padding: "6px 10px", color: "var(--ink)", fontSize: 12, textAlign: "left" }}
                  >
                    Archive
                  </Link>
                </div>

                <div style={{ borderTop: "1px solid var(--rule)", marginTop: 6, paddingTop: 6 }}>
                  <button
                    onClick={logout}
                    className="linkbtn"
                    style={{ width: "100%", textAlign: "left", padding: "6px 10px", fontSize: 12, color: "var(--accent)" }}
                  >
                    Sign Out
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
