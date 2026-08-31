import { MapEngineProvider } from "../../../../core/MapEngineContext";
import ChronicleDayViewer from "../../../../components/chronicle/ChronicleDayViewer";
import { ChronicleDayProvider } from "../../../../lib/map/chronicleDayContext";
import { isValidChronicleDay } from "../../../../lib/map/chronicleDayRoute";
import InvalidChronicleDay from "../../../../components/chronicle/InvalidChronicleDay";

// Next.js 16 App Router: `params` is a Promise and must be awaited, matching
// `app/wiki/materials/[slug]/page.tsx`.
export default async function Page({
  params,
}: {
  params: Promise<{ day: string }>;
}) {
  const { day } = await params;

  // The segment comes straight off the URL and ends up in a request path that
  // the backend resolves against a per-day directory, so it is validated
  // before anything else touches it. This is defence in depth, not the only
  // guard: the backend is independently hardened, and `chronicleData.ts`
  // already `encodeURIComponent`s every day it puts in a URL.
  if (!isValidChronicleDay(day)) {
    return <InvalidChronicleDay mapId={"main"} />;
  }

  return (
    <MapEngineProvider>
      <ChronicleDayProvider day={day}>
        {/*
          Keyed by day so a params-only navigation (browser back/forward
          between two day URLs) remounts instead of re-rendering. The banner
          date is derived during render while the data resets happen in
          effects, which run after paint — without this, the first committed
          frame can show the previous day's painted canvases and region
          records under the new day's date.
        */}
        <ChronicleDayViewer key={day} mapId={"main"} day={day} />
      </ChronicleDayProvider>
    </MapEngineProvider>
  );
}
