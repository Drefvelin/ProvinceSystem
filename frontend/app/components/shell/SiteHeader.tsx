"use client";

import Link from "next/link";

import { useAccessibleMaps } from "@/app/hooks/useAccessibleMaps";
import type { MapId } from "@/app/components/map/types";
import { STAFF_MAP_PAGE_ROUTES } from "@/lib/map/api";

const staticLinks = [
  { href: "/", label: "Home" },
  { href: "/map/main", label: "Map" },
  { href: "/skins", label: "Skins" },
  { href: "/drinks", label: "Drinks" },
  { href: "/character", label: "Character" },
] as const;

function staffNavLinks(
  maps: { id: string; display_name: string; public: boolean }[]
) {
  return maps
    .filter((entry) => !entry.public && entry.id !== "main")
    .map((entry) => {
      const href = STAFF_MAP_PAGE_ROUTES[entry.id as MapId];
      if (!href) return null;
      return { href, label: entry.display_name };
    })
    .filter((item): item is { href: string; label: string } => item !== null);
}

export default function SiteHeader() {
  const { maps, loading } = useAccessibleMaps();
  const staffLinks = loading ? [] : staffNavLinks(maps);

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
        {staffLinks.map(({ href, label }) => (
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
