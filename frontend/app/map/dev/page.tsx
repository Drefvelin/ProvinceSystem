import { MapEngineProvider } from "../.././core/MapEngineContext";
import MapViewer from "../../components/MapViewer";

export default function Page() {
  return (
    <MapEngineProvider>
      <MapViewer mapId={"dev"} />
    </MapEngineProvider>
  );
}
