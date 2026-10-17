"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const LINKS = [
  { href: "/paper", label: "Today" },
  { href: "/archive", label: "Archive" },
  { href: "/profile", label: "Profile" },
];

export default function Nav() {
  const path = usePathname() || "";
  return (
    <nav className="nav" aria-label="Main">
      <div className="wrap">
        <Link href="/" className="brand">The Fold</Link>
        <div className="links">
          {LINKS.map((l) => (
            <Link key={l.href} href={l.href} className={path.startsWith(l.href) ? "on" : ""}>{l.label}</Link>
          ))}
        </div>
      </div>
    </nav>
  );
}
