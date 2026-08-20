"use client";

import { useState, useEffect, useRef, useMemo } from "react";
import { useMapEngine } from "../core/MapEngineContext";
import { useMapHover } from "../hooks/useMapHover";
import type { MapPickViewport } from "../hooks/useMapCoords";
import { useMapModeData } from "../hooks/useMapModeData";
import { useMapGeometry } from "../hooks/useMapGeometry";
import { useMapMarkers } from "../hooks/useMapMarkers";
import { isMarkerMapMode } from "../lib/mapMarkers";
import {
  installationToMapMarker,
} from "../lib/installationMarkers";
import {
  settlementToMapMarker,
} from "../lib/settlementMarkers";
import { useGuildCache } from "../hooks/useGuildCache";
import { useTitleLayerData } from "../hooks/useTitleLayerData";
import {
  computeRegionLabelGeometry,
  filterRegionLabelsForMapObjects,
  LABEL_MAP_MODES,
} from "../lib/mapLabels";
import {
  applyDrillStack,
  drillStackNames,
  getAncestryChain,
  getNextDrillTarget,
  type DrillLayer,
} from "./map/drillUtils";
import MapAccessGate, {
  type MapAccessGateReason,
} from "./map/MapAccessGate";
import MapCanvas from "./map/MapCanvas";
import MapPageLayout from "./map/MapPageLayout";
import MapToolbar from "./map/MapToolbar";
import {
  MapDesktopSidePanel,
  MapDrillStackBar,
} from "./map/MapSidePanel";
import NationDetailModal from "./map/NationDetailModal";
import { buildRegionInfo } from "./map/regionInfo";
import type {
  CursorTooltip,
  HoverOverlay,
  MapId,
  MapMode,
  RegionInfo,
} from "./map/types";
import { MAP_DISPLAY_NAMES } from "./map/types";
import { getSession, isSessionValid } from "@/lib/characters/session";
import {
  MapAccessError,
  fetchMapBlobUrl,
  fetchMapJson,
  mapApiUrl,
  mapRequiresAuth,
  revokeMapBlobUrl,
  staffMapAccessReason,
} from "@/lib/map/api";

type MapViewerProps = {
  mapId: MapId;
};

function useCharacterSessionToken(): string | null {
  const [sessionToken, setSessionToken] = useState<string | null>(null);

  useEffect(() => {
    const syncSession = () => {
      const session = getSession();
      setSessionToken(
        isSessionValid(session) ? session?.session_token ?? null : null
      );
    };

    syncSession();
    window.addEventListener("storage", syncSession);
    return () => window.removeEventListener("storage", syncSession);
  }, []);

  return sessionToken;
}

const MapViewer = ({ mapId }: MapViewerProps) => {
  const sessionToken = useCharacterSessionToken();
  const authToken = mapRequiresAuth(mapId) ? sessionToken : null;
  const [gateReason, setGateReason] = useState<MapAccessGateReason | null>(
    null
  );
  const [accessChecked, setAccessChecked] = useState(mapId === "main");

  const [mapType, setMapType] = useState<MapMode>("nation");
  const [hoveredOverlay, setHoveredOverlay] = useState<HoverOverlay | null>(
    null
  );
  const [hoveredFortZoc, setHoveredFortZoc] = useState<HoverOverlay | null>(
    null
  );
  const [selectedRegionId, setSelectedRegionId] = useState<string | null>(null);
  const [regionInfo, setRegionInfo] = useState<RegionInfo | null>(null);
  const [modalRegionInfo, setModalRegionInfo] = useState<RegionInfo | null>(
    null
  );
  const [modalOpen, setModalOpen] = useState(false);
  const [drillStack, setDrillStack] = useState<DrillLayer[]>([]);
  const [pendingDrillId, setPendingDrillId] = useState<string | null>(null);
  const [cursorTooltip, setCursorTooltip] = useState<CursorTooltip | null>(
    null
  );
  const [hoveredMarkerId, setHoveredMarkerId] = useState<string | null>(null);

  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const viewportCoordsRef = useRef<MapPickViewport | null>(null);
  const lastProvinceIdRef = useRef<number | null>(null);

  const mapDisplayName = MAP_DISPLAY_NAMES[mapId];

  useEffect(() => {
    if (mapId !== "dev") {
      setGateReason(null);
      setAccessChecked(true);
      return;
    }

    let cancelled = false;
    setAccessChecked(false);
    setGateReason(null);

    void fetchMapJson(`/${mapId}/data/nation`, { sessionToken: authToken })
      .then(() => {
        if (!cancelled) setGateReason(null);
      })
      .catch((err) => {
        if (cancelled) return;
        if (err instanceof MapAccessError && err.status === 403) {
          setGateReason(staffMapAccessReason(err));
        }
      })
      .finally(() => {
        if (!cancelled) setAccessChecked(true);
      });

    return () => {
      cancelled = true;
    };
  }, [mapId, authToken]);

  const guildNameCacheRef = useGuildCache(mapId, authToken);

  const {
    mapObjects,
    loadData,
    resetDrillVisibility,
    resetMapObjects,
    getHoverRegion,
    drillDownRegion,
  } = useMapEngine();
  const { regionData, loading, accessError } = useMapModeData({
    mapId,
    mapType,
    loadData,
    sessionToken: authToken,
  });
  const { layers: titleLayers } = useTitleLayerData(
    mapId,
    mapType,
    regionData,
    authToken
  );
  const {
    neighbors,
    labelNeighbors,
    centroids,
    labelGrid,
    ready: geometryReady,
  } = useMapGeometry(mapId, authToken);
  const markersEnabled = accessChecked && gateReason === null;
  const { settlements, installations, forts } = useMapMarkers(mapId, authToken, markersEnabled);

  const mapMarkers = useMemo(() => {
    if (!isMarkerMapMode(mapType)) return [];
    return [
      ...settlements.map(settlementToMapMarker),
      ...installations.map(installationToMapMarker),
    ];
  }, [settlements, installations, mapType]);

  const labelGeometry = useMemo(() => {
    if (mapId !== "main" || !LABEL_MAP_MODES.has(mapType)) return null;
    if (!regionData || !neighbors || !centroids) return null;
    const needsTitleLayers =
      mapType === "duchy" ||
      mapType === "kingdom" ||
      mapType === "empire" ||
      mapType === "trade";
    if (needsTitleLayers && !titleLayers) {
      return null;
    }
    return computeRegionLabelGeometry(
      mapType,
      regionData,
      titleLayers,
      neighbors,
      centroids,
      {
        grid: labelGrid ?? undefined,
        labelNeighbors: labelNeighbors ?? neighbors,
      }
    );
  }, [
    mapId,
    mapType,
    regionData,
    titleLayers,
    neighbors,
    labelNeighbors,
    centroids,
    labelGrid,
  ]);

  const regionLabels = useMemo(
    () => filterRegionLabelsForMapObjects(labelGeometry, mapType, mapObjects),
    [labelGeometry, mapType, mapObjects]
  );

  useEffect(() => {
    if (!pendingDrillId || !regionData) return;

    drillDownRegion(pendingDrillId, regionData);

    const region = regionData[pendingDrillId];
    const name = region?.name || pendingDrillId;

    setDrillStack([
      {
        regionId: pendingDrillId,
        name,
        rgb: region?.rgb ?? "128,128,128",
      },
    ]);
    setPendingDrillId(null);
  }, [pendingDrillId, regionData, drillDownRegion]);

  useEffect(() => {
    if (!accessChecked || gateReason || loading || (mapId === "main" && !geometryReady)) {
      return;
    }

    let blobUrl: string | null = null;
    let cancelled = false;

    const drawImage = async () => {
      const canvas = canvasRef.current;
      if (!canvas) return;
      const ctx = canvas.getContext("2d");
      if (!ctx) return;

      const path = `/${mapId}/mapdata/${mapType}`;
      let src = mapApiUrl(path);
      if (mapRequiresAuth(mapId) && authToken) {
        try {
          src = await fetchMapBlobUrl(path, authToken);
          blobUrl = src;
        } catch (err) {
          console.error("Failed to load pick map image:", err);
          return;
        }
      }

      if (cancelled) {
        revokeMapBlobUrl(blobUrl);
        return;
      }

      const img = new Image();
      img.crossOrigin = "anonymous";
      img.src = src;
      img.onload = () => {
        if (cancelled) return;
        canvas.width = img.width;
        canvas.height = img.height;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0);
      };
      img.onerror = () => {
        console.error("Failed to load pick map image:", src);
      };
    };

    setCursorTooltip(null);
    setDrillStack([]);
    setHoveredOverlay(null);
    setHoveredFortZoc(null);
    setRegionInfo(null);
    setModalOpen(false);
    setModalRegionInfo(null);
    void drawImage();

    return () => {
      cancelled = true;
      revokeMapBlobUrl(blobUrl);
    };
  }, [
    mapId,
    mapType,
    loading,
    geometryReady,
    accessChecked,
    gateReason,
    authToken,
  ]);

  const { onMouseMove, onMouseLeave: onHoverLeave, isHoveringClickable } = useMapHover({
    mapId,
    mapType,
    loading,
    regionData,
    canvasRef,
    viewportCoordsRef,
    guildNameCacheRef,
    sessionToken: authToken,
    setCursorTooltip,
    setHoveredOverlay,
    setHoveredFortZoc,
    setRegionInfo,
    setSelectedRegionId,
    getHoverRegion,
    mapDisplayName,
    mapObjects,
    markers: mapMarkers,
    forts,
    setHoveredMarkerId,
  });

  function handleMapTypeChange(mode: MapMode) {
    resetMapObjects();
    setMapType(mode);
  }

  function handleResetDrill() {
    setDrillStack([]);
    if (regionData) resetDrillVisibility(regionData);
  }

  function handleDrillToLayer(index: number) {
    if (!regionData || index < 0 || index >= drillStack.length) return;

    const nextStack = drillStack.slice(0, index + 1);
    applyDrillStack(
      nextStack,
      regionData,
      resetDrillVisibility,
      drillDownRegion
    );
    setDrillStack(nextStack);
  }

  const handleDrill = () => {
    if (!selectedRegionId || !regionData) return;

    const nextTargetId = getNextDrillTarget(
      selectedRegionId,
      regionData,
      drillStack
    );
    if (!nextTargetId) return;

    const region = regionData[nextTargetId];
    if (!region?.subjects?.length) return;

    const ancestry = getAncestryChain(selectedRegionId, regionData);
    const stackNames = drillStackNames(drillStack);
    const isInsideStack = ancestry.some((id) =>
      stackNames.includes(regionData[id]?.name ?? "")
    );

    if (!isInsideStack) {
      setDrillStack([]);
      resetDrillVisibility(regionData);
      setPendingDrillId(nextTargetId);
      return;
    }

    drillDownRegion(nextTargetId, regionData);

    const layer: DrillLayer = {
      regionId: nextTargetId,
      name: region.name || nextTargetId,
      rgb: region.rgb ?? "128,128,128",
    };
    setDrillStack((prev) =>
      prev.some((entry) => entry.regionId === layer.regionId)
        ? prev
        : [...prev, layer]
    );
  };

  const handleMapClick = (event: React.MouseEvent<HTMLCanvasElement>) => {
    if (event.button !== 0) return;
    if (!selectedRegionId || !regionData) return;

    if (event.ctrlKey || event.metaKey) {
      handleDrill();
      return;
    }

    const region = regionData[selectedRegionId];
    if (!region) return;

    setModalRegionInfo(
      buildRegionInfo(
        selectedRegionId,
        region,
        mapType,
        mapDisplayName,
        regionData
      )
    );
    setModalOpen(true);
  };

  const handleMouseLeave = () => {
    onHoverLeave();
    setHoveredMarkerId(null);
    setCursorTooltip(null);
    setHoveredOverlay(null);
    setHoveredFortZoc(null);
    setRegionInfo(null);
    lastProvinceIdRef.current = null;
  };

  if (!accessChecked) {
    return (
      <div className="flex min-h-[calc(100dvh-var(--tfmc-header-h))] items-center justify-center bg-[var(--tfmc-forest-deep)]">
        <p className="text-lg font-medium text-[var(--tfmc-cream)]">
          Loading map…
        </p>
      </div>
    );
  }

  if (gateReason || accessError) {
    return (
      <MapAccessGate
        reason={gateReason ?? accessError ?? "unknown"}
        mapDisplayName={mapDisplayName}
      />
    );
  }

  if (loading || (mapId === "main" && !geometryReady)) {
    return (
      <div className="flex min-h-[calc(100dvh-var(--tfmc-header-h))] items-center justify-center bg-[var(--tfmc-forest-deep)]">
        <p className="text-lg font-medium text-[var(--tfmc-cream)]">
          Loading map…
        </p>
      </div>
    );
  }

  return (
    <>
      <MapPageLayout
        mapDisplayName={mapDisplayName}
        mapModeSelector={
          <MapToolbar
            mapId={mapId}
            mapType={mapType}
            onMapTypeChange={handleMapTypeChange}
            variant="bar"
          />
        }
        drillStackBar={
          <MapDrillStackBar
            drillStack={drillStack}
            onSelectLayer={handleDrillToLayer}
            onResetDrill={handleResetDrill}
          />
        }
        desktopSidePanel={
          <MapDesktopSidePanel
            mapId={mapId}
            mapType={mapType}
            regionInfo={regionInfo}
            regionData={regionData}
            sessionToken={authToken}
          />
        }
      >
        <MapCanvas
          mapId={mapId}
          mapType={mapType}
          sessionToken={authToken}
          canvasRef={canvasRef}
          viewportCoordsRef={viewportCoordsRef}
          mapObjects={mapObjects}
          hoveredOverlay={hoveredOverlay}
          hoveredFortZoc={hoveredFortZoc}
          cursorTooltip={cursorTooltip}
          labels={regionLabels}
          markers={mapMarkers}
          hoveredMarkerId={hoveredMarkerId}
          hoveredNationId={selectedRegionId}
          onMouseMove={onMouseMove}
          onMouseLeave={handleMouseLeave}
          onClick={handleMapClick}
          isHoveringClickable={isHoveringClickable}
        />
      </MapPageLayout>

      <NationDetailModal
        open={modalOpen}
        mapId={mapId}
        mapType={mapType}
        regionInfo={modalRegionInfo}
        regionData={regionData}
        sessionToken={authToken}
        onClose={() => setModalOpen(false)}
      />
    </>
  );
};

export default MapViewer;
