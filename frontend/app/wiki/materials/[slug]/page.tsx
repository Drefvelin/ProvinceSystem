import Link from "next/link";
import { notFound } from "next/navigation";
import CraftingGrid from "../../../components/wiki/CraftingGrid";
import { getMaterialBySlug, materialCatalog } from "../../data";

export function generateStaticParams() {
  return Array.from(materialCatalog.values()).map((m) => ({ slug: m.slug }));
}

export default async function MaterialDetailPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const material = getMaterialBySlug(slug);
  if (!material) notFound();

  return (
    <article className="max-w-3xl">
      <Link href="/wiki/materials" className="text-xs text-[var(--tfmc-mist)] hover:text-[var(--tfmc-cream)]">
        &larr; Back to Materials
      </Link>

      <div className="mt-3 flex items-center gap-4">
        {material.texture ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={material.texture}
            alt={material.name}
            className="h-16 w-16 [image-rendering:pixelated]"
          />
        ) : null}
        <h1 className="font-[family-name:var(--font-fraunces)] text-3xl text-[var(--tfmc-cream)] sm:text-4xl">
          {material.name}
        </h1>
      </div>

      {material.lore ? (
        <p className="mt-3 text-sm italic text-[var(--tfmc-mist)]">{material.lore}</p>
      ) : null}

      <h2 className="mt-8 font-[family-name:var(--font-fraunces)] text-xl text-[var(--tfmc-cream)]">
        How to acquire
      </h2>
      {material.recipe ? (
        <div className="mt-4">
          <CraftingGrid recipe={material.recipe} />
        </div>
      ) : (
        <p className="mt-1 text-sm text-[var(--tfmc-mist)]">
          No crafting recipe — this material comes from loot, mining, or mobs, not a crafting
          station.
        </p>
      )}

      <h2 className="mt-8 font-[family-name:var(--font-fraunces)] text-xl text-[var(--tfmc-cream)]">
        What can be crafted from it
      </h2>
      {material.usedIn.length ? (
        <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
          {material.usedIn.map((r) => (
            <CraftingGrid key={r.key} recipe={r} />
          ))}
        </div>
      ) : (
        <p className="mt-1 text-sm text-[var(--tfmc-mist)]">
          Nothing on the Gameplay Guide currently lists this as an ingredient.
        </p>
      )}
    </article>
  );
}
