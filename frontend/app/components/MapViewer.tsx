"use client";

import { useState, useEffect, useRef } from "react";
import { useMapEngine } from "../core/MapEngineContext";
import { useMapHover } from "../hooks/useMapHover";
import { useMapModeData } from "../hooks/useMapModeData";
import { useGuildCache } from "../hooks/useGuildCache";
import {
  applyDrillStack,
  drillStackNames,
  getAncestryChain,
  getNextDrillTarget,
  type DrillLayer,
} from "./map/drillUtils";
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
import { MAP_DISPLAY_NAMES, apiBase } from "./map/types";

type MapViewerProps = {
  mapId: MapId;
};

const MapViewer = ({ mapId }: MapViewerProps) => {
  const [mapType, setMapType] = useState<MapMode>("nation");
  const [hoveredOverlay, setHoveredOverlay] = useState<HoverOverlay | null>(
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

  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const lastProvinceIdRef = useRef<number | null>(null);

  const guildNameCacheRef = mapId === "dev" ? useGuildCache(mapId) : null;

  const mapDisplayName = MAP_DISPLAY_NAMES[mapId];

  const {
    mapObjects,
    loadData,
    resetMapObjects,
    getHoverRegion,
    drillDownRegion,
  } = useMapEngine();
  const { regionData, loading } = useMapModeData({
    mapId,
    mapType,
    loadData,
  });

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
    if (loading) return;

    const drawImage = async () => {
      const canvas = canvasRef.current;
      if (!canvas) return;
      const ctx = canvas.getContext("2d");
      if (!ctx) return;

      const img = new Image();
      img.crossOrigin = "anonymous";
      img.src = `${apiBase()}/${mapId}/mapdata/${mapType}`;
      img.onload = () => {
        canvas.width = img.width;
        canvas.height = img.height;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0);
      };
    };

    setCursorTooltip(null);
    setDrillStack([]);
    setHoveredOverlay(null);
    setRegionInfo(null);
    setModalOpen(false);
    setModalRegionInfo(null);
    drawImage();
  }, [mapId, mapType, loading]);

  const { onMouseMove } = useMapHover({
    mapId,
    mapType,
    loading,
    regionData,
    canvasRef,
    guildNameCacheRef,
    setCursorTooltip,
    setHoveredOverlay,
    setRegionInfo,
    setSelectedRegionId,
    getHoverRegion,
    mapDisplayName,
    mapObjects,
  });

  function handleMapTypeChange(mode: MapMode) {
    resetMapObjects();
    setMapType(mode);
  }

  function handleResetDrill() {
    setDrillStack([]);
    if (regionData) loadData(regionData);
  }

  function handleDrillToLayer(index: number) {
    if (!regionData || index < 0 || index >= drillStack.length) return;

    const nextStack = drillStack.slice(0, index + 1);
    applyDrillStack(nextStack, regionData, loadData, drillDownRegion);
    setDrillStack(nextStack);
    setHoveredOverlay(null);
    setRegionInfo(null);
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
      loadData(regionData);
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

  const handleMapClick = (event: React.MouseEvent<HTMLDivElement>) => {
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
    setCursorTooltip(null);
    setHoveredOverlay(null);
    setRegionInfo(null);
    lastProvinceIdRef.current = null;
  };

  if (loading) {
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
          />
        }
      >
        <MapCanvas
          mapId={mapId}
          mapType={mapType}
          canvasRef={canvasRef}
          mapObjects={mapObjects}
          hoveredOverlay={hoveredOverlay}
          cursorTooltip={cursorTooltip}
          onMouseMove={onMouseMove}
          onMouseLeave={handleMouseLeave}
          onClick={handleMapClick}
        />
      </MapPageLayout>

      <NationDetailModal
        open={modalOpen}
        mapId={mapId}
        mapType={mapType}
        regionInfo={modalRegionInfo}
        regionData={regionData}
        onClose={() => setModalOpen(false)}
      />
    </>
  );
};

export default MapViewer;
