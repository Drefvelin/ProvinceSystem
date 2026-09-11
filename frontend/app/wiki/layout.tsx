import Link from "next/link";

import { WikiSearch } from "@/app/components/wiki";
import { navItemsForCategory, overviewNavItem, populatedCategories } from "./data";

export default function WikiLayout({ children }: { children: React.ReactNode }) {
  const categories = populatedCategories();

  return (
    <div className="mx-auto flex min-h-[calc(100dvh-var(--tfmc-header-h))] max-w-6xl flex-col gap-6 px-6 py-10 lg:flex-row">
      <aside className="relative z-30 shrink-0 lg:sticky lg:top-[calc(var(--tfmc-header-h)+2.5rem)] lg:flex lg:max-h-[calc(100dvh-var(--tfmc-header-h)-5rem)] lg:w-56 lg:self-start lg:flex-col">
        <p className="font-[family-name:var(--font-fraunces)] text-sm uppercase tracking-widest text-[var(--tfmc-mist)]">
          Gameplay Guide
        </p>
        <WikiSearch />
        <nav className="mt-3 flex flex-row flex-wrap gap-1 lg:min-h-0 lg:flex-1 lg:flex-col lg:flex-nowrap lg:gap-0 lg:overflow-y-auto lg:overscroll-contain lg:pr-2 lg:[scrollbar-gutter:stable]">
          <Link
            href={overviewNavItem.href}
            className="rounded px-2 py-1.5 text-sm text-[var(--tfmc-stone)] transition-colors hover:bg-[color-mix(in_srgb,var(--tfmc-cream)_8%,transparent)] hover:text-[var(--tfmc-cream)]"
          >
            {overviewNavItem.label}
          </Link>

          {categories.map((category) => (
            <div key={category.key} className="flex flex-row flex-wrap items-center gap-1 lg:mt-4 lg:flex-col lg:items-stretch lg:gap-0">
              <p className="px-2 py-1.5 font-[family-name:var(--font-fraunces)] text-[11px] uppercase tracking-widest text-[var(--tfmc-mist)]">
                {category.label}
              </p>
              {navItemsForCategory(category.key).map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="flex items-center gap-1.5 rounded px-2 py-1.5 text-sm text-[var(--tfmc-stone)] transition-colors hover:bg-[color-mix(in_srgb,var(--tfmc-cream)_8%,transparent)] hover:text-[var(--tfmc-cream)]"
                >
                  {item.label}
                </Link>
              ))}
            </div>
          ))}
        </nav>
      </aside>

      <main className="min-w-0 flex-1">
        {children}
      </main>
    </div>
  );
}
