import Link from "next/link";

import { navItemsForCategory, populatedCategories } from "./data";

export default function WikiOverviewPage() {
  return (
    <div className="max-w-2xl">
      <h1 className="font-[family-name:var(--font-fraunces)] text-3xl text-[var(--tfmc-cream)] sm:text-4xl">
        Gameplay Guide
      </h1>
      <p className="mt-2 text-sm text-[var(--tfmc-mist)]">
        TFMC Season 5: crafting stations, recipes, and mechanics for the custom systems on
        the server. More sections will be added as the season goes on.
      </p>

      {populatedCategories().map((category) => (
        <section key={category.key} className="mt-8">
          <h2 className="font-[family-name:var(--font-fraunces)] text-xl text-[var(--tfmc-cream)]">
            {category.label}
          </h2>
          <p className="mt-1 text-sm text-[var(--tfmc-mist)]">{category.blurb}</p>

          <div className="mt-4 flex flex-col gap-3">
            {navItemsForCategory(category.key).map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="rounded-md border border-[color-mix(in_srgb,var(--tfmc-cream)_12%,transparent)] bg-[color-mix(in_srgb,var(--tfmc-forest)_45%,transparent)] p-4 transition-colors hover:border-[var(--tfmc-accent)]"
              >
                <p className="flex items-center gap-2 font-[family-name:var(--font-fraunces)] text-lg text-[var(--tfmc-cream)]">
                  {item.label}
                </p>
                <p className="mt-1 text-sm text-[var(--tfmc-mist)]">{item.blurb}</p>
              </Link>
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}
