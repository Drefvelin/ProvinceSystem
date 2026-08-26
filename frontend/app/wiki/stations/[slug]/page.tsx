import Link from "next/link";
import { notFound } from "next/navigation";
import CraftingGrid from "../../../components/wiki/CraftingGrid";
import StationModelViewer from "../../../components/wiki/StationModelViewer";
import SimpleCubeViewer from "../../../components/wiki/SimpleCubeViewer";
import { getRecipesForStation, getStationBySlug, stations } from "../../data";

export function generateStaticParams() {
  return stations.map((s) => ({ slug: s.slug }));
}

export default async function StationDetailPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const station = getStationBySlug(slug);
  if (!station) notFound();

  const recipes = getRecipesForStation(station.name);

  return (
    <article className="max-w-4xl">
      <Link href="/wiki/stations" className="text-xs text-[var(--tfmc-mist)] hover:text-[var(--tfmc-cream)]">
        &larr; Back to Stations
      </Link>

      <h1 className="mt-3 font-[family-name:var(--font-fraunces)] text-3xl text-[var(--tfmc-cream)] sm:text-4xl">
        {station.name}
      </h1>
      <p className="mt-2 text-sm text-[var(--tfmc-mist)]">{station.blurb}</p>

      <div className="mt-6">
        {station.model ? (
          <StationModelViewer modelUrl={station.model.url} textureUrl={station.model.texture} />
        ) : station.cubeFaces ? (
          <SimpleCubeViewer faces={station.cubeFaces} />
        ) : (
          <div className="flex h-40 flex-col items-center justify-center gap-2 rounded-md border border-[color-mix(in_srgb,var(--tfmc-cream)_12%,transparent)] bg-[color-mix(in_srgb,var(--tfmc-forest-deep)_60%,transparent)]">
            {station.fallbackTexture ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={station.fallbackTexture}
                alt={station.name}
                className="h-12 w-12 [image-rendering:pixelated]"
              />
            ) : null}
            <p className="text-xs text-[var(--tfmc-mist)]">
              {station.vanillaBlock
                ? `This is a vanilla ${station.vanillaBlock.name} — no custom model.`
                : "No 3D model found for this station."}
            </p>
          </div>
        )}
      </div>

      {station.vanillaBlock ? (
        <div className="mt-4 rounded-md border border-[color-mix(in_srgb,var(--tfmc-accent)_35%,transparent)] bg-[color-mix(in_srgb,var(--tfmc-accent)_10%,transparent)] p-4">
          <p className="text-sm font-semibold text-[var(--tfmc-accent)]">
            Accessibility: shift+right-click required
          </p>
          <p className="mt-1 text-sm text-[var(--tfmc-mist)]">{station.vanillaBlock.accessNote}</p>
        </div>
      ) : null}

      <h2 className="mt-8 font-[family-name:var(--font-fraunces)] text-xl text-[var(--tfmc-cream)]">
        How to obtain this station
      </h2>
      {station.craftRecipe ? (
        <div className="mt-4 max-w-sm">
          <CraftingGrid recipe={station.craftRecipe} />
        </div>
      ) : station.vanillaBlock ? (
        <p className="mt-1 text-sm text-[var(--tfmc-mist)]">
          No special recipe — place a normal vanilla {station.vanillaBlock.name} and it works as
          the station once shift+right-clicked. Craft it the usual vanilla way.
        </p>
      ) : station.noPlaceableBlock ? (
        <p className="mt-1 text-sm text-[var(--tfmc-mist)]">
          This station has no placeable block — it&apos;s opened directly (NPC or command), not
          crafted or placed in the world.
        </p>
      ) : (
        <p className="mt-1 text-sm text-[var(--tfmc-mist)]">Not documented yet.</p>
      )}

      <h2 className="mt-8 font-[family-name:var(--font-fraunces)] text-xl text-[var(--tfmc-cream)]">
        Recipes crafted here
      </h2>
      {recipes.length ? (
        <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
          {recipes.map((r) => (
            <CraftingGrid key={r.key} recipe={r} />
          ))}
        </div>
      ) : (
        <p className="mt-1 text-sm text-[var(--tfmc-mist)]">No recipes documented yet.</p>
      )}
    </article>
  );
}
