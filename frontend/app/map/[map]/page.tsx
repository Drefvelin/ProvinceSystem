import { notFound } from "next/navigation";

import { MapEngineProvider } from "../../core/MapEngineContext";
import MapViewer from "../../components/MapViewer";
import { parseMapRouteSegment } from "../../lib/map/chronicleDayRoute";

export default async function Page({
  params,
}: {
  params: Promise<{ map: string }>;
}) {
  const mapId = parseMapRouteSegment((await params).map);
  if (!mapId) notFound();

  return (
    <MapEngineProvider>
      <MapViewer mapId={mapId} />
    </MapEngineProvider>
  );
}
