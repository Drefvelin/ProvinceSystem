import Link from "next/link";
import { stations } from "../data";

export default function StationsPage() {
  return (
    <article className="max-w-4xl">
      <h1 className="font-[family-name:var(--font-fraunces)] text-3xl text-[var(--tfmc-cream)] sm:text-4xl">
        Crafting Stations
      </h1>
      <p className="mt-2 text-sm text-[var(--tfmc-mist)]">
        Every station used by the recipes on this guide. Stations with a real in-world model show
        an interactive 3D preview — drag to rotate.
      </p>

      <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2">
        {stations.map((s) => (
          <Link
            key={s.slug}
            href={`/wiki/stations/${s.slug}`}
            className="group rounded-md border border-[color-mix(in_srgb,var(--tfmc-cream)_12%,transparent)] bg-[color-mix(in_srgb,var(--tfmc-forest)_45%,transparent)] p-4 transition-colors hover:border-[var(--tfmc-accent)]"
          >
            <div className="flex items-center gap-3">
              <div className="relative h-10 w-10 shrink-0">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={s.icon}
                  alt={s.name}
                  className="h-10 w-10 [image-rendering:pixelated] transition-transform duration-150 group-hover:scale-110"
                />
                {s.model ? (
                  <span className="absolute -bottom-1 -right-1 rounded bg-[color-mix(in_srgb,var(--tfmc-accent)_35%,var(--tfmc-forest-deep))] px-1 text-[9px] font-semibold text-[var(--tfmc-cream)]">
                    3D
                  </span>
                ) : null}
              </div>
              <p className="font-[family-name:var(--font-fraunces)] text-lg text-[var(--tfmc-cream)]">
                {s.name}
              </p>
            </div>
            <p className="mt-2 text-sm text-[var(--tfmc-mist)]">{s.blurb}</p>
          </Link>
        ))}
      </div>
    </article>
  );
}
