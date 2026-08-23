"use client";

import Link from "next/link";

const staticLinks = [
  { href: "/", label: "Home" },
  { href: "/map/main", label: "Map" },
  { href: "/skins", label: "Skins" },
  { href: "/drinks", label: "Drinks" },
  { href: "/profile", label: "Profile" },
] as const;

export default function SiteHeader() {
  return (
    <header
      className="sticky top-0 z-[100] flex h-14 items-center border-b border-[color-mix(in_srgb,var(--tfmc-cream)_12%,transparent)] bg-[color-mix(in_srgb,var(--tfmc-forest-deep)_92%,transparent)] px-4 backdrop-blur-md sm:px-6"
      style={{ height: "var(--tfmc-header-h)" }}
    >
      <Link
        href="/"
        className="font-[family-name:var(--font-fraunces)] text-lg tracking-wide text-[var(--tfmc-cream)] transition-opacity hover:opacity-80"
      >
        TFMC
      </Link>
      <nav className="ml-auto flex items-center gap-5 sm:gap-8" aria-label="Main">
        {staticLinks.map(({ href, label }) => (
          <Link
            key={href}
            href={href}
            className="text-sm font-medium text-[var(--tfmc-stone)] transition-colors hover:text-[var(--tfmc-cream)]"
          >
            {label}
          </Link>
        ))}
      </nav>
    </header>
  );
}
