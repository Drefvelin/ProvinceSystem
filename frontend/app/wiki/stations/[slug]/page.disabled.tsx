// TEMPORARILY DISABLED: Stations section - re-enable by renaming this file back to
// `page.tsx`. Next.js only creates a route for a file literally named `page.tsx`, so
// renaming (rather than commenting out the component, which would leave the route
// file without a default export and break the build) is what takes the route off the
// site, out of the sidebar/overview, and out of the built search index.
import Link from "next/link";
import { notFound } from "next/navigation";
import CraftingGrid from "../../../components/wiki/CraftingGrid";
import StationModelViewer from "../../../components/wiki/StationModelViewer";
import SimpleCubeViewer from "../../../components/wiki/SimpleCubeViewer";
import { getStationBySlug, stations } from "../../data";

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
          <StationModelViewer modelUrl={station.model.url} textureUrl={station.model.texture} textureUrls={station.model.textures} textureAnimationUrl={station.model.textureAnimationUrl} />
        ): station.cubeFaces ? (
          <SimpleCubeViewer faces={station.cubeFaces} />
        ): (
          <div className="flex h-40 flex-col items-center justify-center gap-2 rounded-md border border-[color-mix(in_srgb,var(--tfmc-cream)_12%,transparent)] bg-[color-mix(in_srgb,var(--tfmc-forest-deep)_60%,transparent)]">
            {station.fallbackTexture ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={station.fallbackTexture}
                alt={station.name}
                className="h-12 w-12 [image-rendering:pixelated]"
              />
            ): null}
            <p className="text-xs text-[var(--tfmc-mist)]">
              {station.vanillaBlock
                ? `This is a vanilla ${station.vanillaBlock.name}: no custom model.`
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
      ): null}

      <h2 id="obtaining" className="mt-8 font-[family-name:var(--font-fraunces)] text-xl text-[var(--tfmc-cream)]">
        How to obtain this station
      </h2>
      {station.craftRecipe ? (
        <div className="mt-4 max-w-sm">
          <CraftingGrid recipe={station.craftRecipe} />
        </div>
      ): station.vanillaBlock ? (
        <p className="mt-1 text-sm text-[var(--tfmc-mist)]">
          No special recipe: place a normal vanilla {station.vanillaBlock.name} and it works as
          the station once shift+right-clicked. Craft it the usual vanilla way.
        </p>
      ): station.noPlaceableBlock ? (
        <p className="mt-1 text-sm text-[var(--tfmc-mist)]">
          This station has no placeable block. It&apos;s opened directly (NPC or command), not
          crafted or placed in the world.
        </p>
      ): (
        <p className="mt-1 text-sm text-[var(--tfmc-mist)]">Not documented yet.</p>
      )}
    </article>
  );
}
