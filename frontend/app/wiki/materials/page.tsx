import Link from "next/link";
import CraftingGrid from "../../components/wiki/CraftingGrid";
import { dropOnlyMaterials, materialRecipes, slugify } from "../data";

const stationOrder = [
  "Ingot Station",
  "Alchemy Station",
  "Magic Station",
  "Engineer Station",
  "Medicine Station",
];

export default function MaterialsPage() {
  const byStation = stationOrder.map((station) => ({
    station,
    recipes: materialRecipes.filter((r) => r.station === station),
  }));

  return (
    <article className="max-w-4xl">
      <h1 className="font-[family-name:var(--font-fraunces)] text-3xl text-[var(--tfmc-cream)] sm:text-4xl">
        Materials
      </h1>
      <p className="mt-2 text-sm text-[var(--tfmc-mist)]">
        The custom material catalogue used across every crafting station on the server —
        ingots, herbal alchemy components, magical cores, and more. Icons shown are the exact
        item textures players see in their inventory.
      </p>

      <div className="mt-6 rounded-md border border-[color-mix(in_srgb,var(--tfmc-cream)_12%,transparent)] bg-[color-mix(in_srgb,var(--tfmc-forest)_45%,transparent)] p-4">
        <p className="text-sm text-[var(--tfmc-mist)]">
          Special case — <span className="text-[var(--tfmc-cream)]">Leather</span> is crafted with a
          single Saddle placed in the centre slot of the grid, every other slot left empty.
        </p>
      </div>

      {byStation.map(({ station, recipes }) =>
        recipes.length ? (
          <section key={station} className="mt-10">
            <h2 className="font-[family-name:var(--font-fraunces)] text-xl text-[var(--tfmc-cream)]">
              {station}
            </h2>
            <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
              {recipes.map((r) => (
                <CraftingGrid key={r.key} recipe={r} />
              ))}
            </div>
          </section>
        ) : null
      )}

      <section className="mt-10">
        <h2 className="font-[family-name:var(--font-fraunces)] text-xl text-[var(--tfmc-cream)]">
          Drop / gather only
        </h2>
        <p className="mt-1 text-sm text-[var(--tfmc-mist)]">
          These materials have no crafting recipe — they come from loot, mining, or mobs.
        </p>
        <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4">
          {dropOnlyMaterials.map((m) => (
            <Link
              key={m.name}
              href={`/wiki/materials/${slugify(m.name)}`}
              title={m.lore}
              className="group flex items-center gap-2 rounded-md border border-[color-mix(in_srgb,var(--tfmc-accent)_35%,transparent)] bg-[color-mix(in_srgb,var(--tfmc-forest-deep)_55%,transparent)] p-2 shadow-[0_2px_0_rgba(0,0,0,0.5)] transition-all duration-150 hover:-translate-y-0.5 hover:scale-105 hover:shadow-[0_4px_0_rgba(0,0,0,0.5),0_8px_14px_rgba(0,0,0,0.4)]"
            >
              {m.texture ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={m.texture}
                  alt={m.name}
                  className="h-8 w-8 shrink-0 [image-rendering:pixelated] transition-transform duration-150 group-hover:scale-105"
                />
              ) : (
                <div className="h-8 w-8 shrink-0 border border-[color-mix(in_srgb,var(--tfmc-cream)_18%,transparent)]" />
              )}
              <span className="text-xs text-[var(--tfmc-stone)] group-hover:text-[var(--tfmc-cream)]">
                {m.name}
              </span>
            </Link>
          ))}
        </div>
      </section>
    </article>
  );
}
