import Link from "next/link";
import StationModelViewer from "./StationModelViewer";
import { catalogNames, slugify, stations, type Slot as SlotData, type Recipe } from "../../wiki/data";

function Slot({ name, qty, texture, model }: { name?: string; qty?: number } & Pick<SlotData, "texture" | "model">) {
  const isMaterial = !!name && catalogNames.has(name);

  const box = (
    <div
      className={
        isMaterial
          ? "group relative z-0 flex h-12 w-12 shrink-0 items-center justify-center overflow-visible border border-[color-mix(in_srgb,var(--tfmc-accent)_45%,transparent)] bg-[color-mix(in_srgb,var(--tfmc-forest)_75%,transparent)] transition-colors duration-150 hover:z-10 hover:border-[var(--tfmc-accent)] sm:h-14 sm:w-14"
         : model
           ? "group relative z-0 flex h-12 w-12 shrink-0 items-center justify-center overflow-visible border border-[color-mix(in_srgb,var(--tfmc-cream)_18%,transparent)] bg-[color-mix(in_srgb,var(--tfmc-forest)_70%,transparent)] outline-none hover:z-20 focus:z-20 focus:border-[var(--tfmc-accent)] sm:h-14 sm:w-14"
           : "relative flex h-12 w-12 shrink-0 items-center justify-center border border-[color-mix(in_srgb,var(--tfmc-cream)_18%,transparent)] bg-[color-mix(in_srgb,var(--tfmc-forest)_70%,transparent)] sm:h-14 sm:w-14"
      }
      title={name}
      tabIndex={model ? 0 : undefined}
      aria-label={model && name ? `3D preview of ${name}. Hover or focus to enlarge.` : undefined}
    >
      {model ? (
        <StationModelViewer
          modelUrl={model.url}
          textureUrl={model.texture}
          textureUrls={model.textures}
          textureAnimationUrl={model.textureAnimationUrl}
          variant="thumb"
        />
      ): texture ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={texture}
          alt={name ?? ""}
          className={
            isMaterial
              ? "h-8 w-8 [image-rendering:pixelated] transition-transform duration-150 will-change-transform group-hover:scale-150 group-hover:drop-shadow-[0_4px_6px_rgba(0,0,0,0.5)] sm:h-10 sm:w-10"
             : "h-8 w-8 [image-rendering:pixelated] sm:h-10 sm:w-10"
          }
        />
      ): name ? (
        <span className="px-1 text-center text-[9px] leading-tight text-[var(--tfmc-stone)]">
          {name}
        </span>
      ): null}
      {name && qty && qty > 1 ? (
        <span
          className="absolute bottom-0 right-0.5 text-[10px] font-semibold text-[var(--tfmc-cream)]"
          style={{ textShadow: "1px 1px 0 #000" }}
        >
          {qty}
        </span>
      ): null}
    </div>
  );

  if (isMaterial) {
    return (
      <Link href={`/wiki/materials/${slugify(name!)}`} className="outline-none">
        {box}
      </Link>
    );
  }
  return box;
}

export default function CraftingGrid({ recipe }: { recipe: Recipe }) {
  const slots = Array.from({ length: 9 }, (_, i) => recipe.ingredients[i]);
  const station = stations.find((s) => s.name === recipe.station);
  // TEMPORARILY DISABLED: Stations section - re-enable by setting this back to
  // `true`. `/wiki/stations/*` no longer exists, so the station chip must render as
  // plain text instead of a link into a 404.
  const stationsLinkEnabled = false;

  return (
    <div className="rounded-md border border-[color-mix(in_srgb,var(--tfmc-cream)_12%,transparent)] bg-[color-mix(in_srgb,var(--tfmc-forest-deep)_55%,transparent)] p-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h3 className="font-[family-name:var(--font-fraunces)] text-lg text-[var(--tfmc-cream)]">
          {recipe.title}
        </h3>
        {stationsLinkEnabled && station ? (
          <Link
            href={`/wiki/stations/${station.slug}`}
            className="group flex items-center gap-1.5 rounded border border-transparent py-0.5 pl-1 pr-1.5 text-xs text-[var(--tfmc-mist)] transition-colors hover:border-[color-mix(in_srgb,var(--tfmc-accent)_35%,transparent)] hover:bg-[color-mix(in_srgb,var(--tfmc-accent)_10%,transparent)] hover:text-[var(--tfmc-accent)]"
          >
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={station.icon}
              alt=""
              className="h-4 w-4 [image-rendering:pixelated] transition-transform duration-150 group-hover:scale-125"
            />
            <span className="underline-offset-2 group-hover:underline">{recipe.station}</span>
          </Link>
        ): (
          <span className="text-xs text-[var(--tfmc-mist)]">{recipe.station}</span>
        )}
      </div>
      {recipe.requirement ? (
        <p className="mt-1 text-xs text-[var(--tfmc-accent)]">Requires: {recipe.requirement}</p>
      ): null}

      <div className="mt-3 flex flex-wrap items-center gap-4">
        <div className="grid grid-cols-3 gap-1">
          {slots.map((slot, i) => (
            <Slot key={i} name={slot?.name} qty={slot?.qty} texture={slot?.texture} model={slot?.model} />
          ))}
        </div>

        <span className="text-xl text-[var(--tfmc-mist)]">&rarr;</span>

        <Slot
          name={recipe.output.name}
          qty={recipe.output.qty}
          texture={recipe.output.texture}
          model={recipe.output.model}
        />
      </div>

      {recipe.note ? <p className="mt-3 text-xs text-[var(--tfmc-mist)]">{recipe.note}</p>: null}
    </div>
  );
}
