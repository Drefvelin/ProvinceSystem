import Link from "next/link";
import { navItems } from "./data";

export default function WikiLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="mx-auto flex min-h-[calc(100dvh-var(--tfmc-header-h))] max-w-6xl flex-col gap-6 px-6 py-10 lg:flex-row">
      <aside className="shrink-0 lg:w-56">
        <p className="font-[family-name:var(--font-fraunces)] text-sm uppercase tracking-widest text-[var(--tfmc-mist)]">
          Gameplay Guide
        </p>
        <nav className="mt-3 flex flex-row flex-wrap gap-1 lg:sticky lg:top-[calc(var(--tfmc-header-h)+2.5rem)] lg:flex-col">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="rounded px-2 py-1.5 text-sm text-[var(--tfmc-stone)] transition-colors hover:bg-[color-mix(in_srgb,var(--tfmc-cream)_8%,transparent)] hover:text-[var(--tfmc-cream)]"
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </aside>

      <main className="min-w-0 flex-1">{children}</main>
    </div>
  );
}
