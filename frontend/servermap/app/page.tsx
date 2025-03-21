import { MapEngineProvider } from "./core/MapEngineContext";
import MapViewer from "./MapViewer";

export default function Page() {
  return (
    <MapEngineProvider>
      <MapViewer />
    </MapEngineProvider>
  );
}
