// TEMPORARILY DISABLED: Stations section - re-enable by renaming this file back to
// `page.tsx`. Next.js only creates a route for a file literally named `page.tsx`, so
// renaming (rather than commenting out the component, which would leave the route
// file without a default export and break the build) is what takes the route off the
// site, out of the sidebar/overview, and out of the built search index.
import { stations } from "../data";
import StationGallery from "./StationGallery";

export default function StationsPage() {
  return (
    <article className="max-w-4xl">
      <h1 className="font-[family-name:var(--font-fraunces)] text-3xl text-[var(--tfmc-cream)] sm:text-4xl">
        Crafting Stations
      </h1>
      <p className="mt-2 text-sm text-[var(--tfmc-mist)]">
        Every station used by the recipes on this guide. Stations with a real in-world model show
        an interactive 3D preview: drag to rotate.
      </p>

      <h2 id="catalogue" className="sr-only">Station catalogue</h2>
      <StationGallery stations={stations} />
    </article>
  );
}
