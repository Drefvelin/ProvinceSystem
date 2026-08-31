"use client";

import { useState, useEffect, useRef, useMemo } from "react";
import Link from "next/link";
import { useMapEngine } from "../core/MapEngineContext";
import { useMapHover } from "../hooks/useMapHover";
import type { MapPickViewport } from "../hooks/useMapCoords";
import useMapPaint from "../hooks/useMapPaint";
import { useMapModeData } from "../hooks/useMapModeData";
import { useMapGeometry } from "../hooks/useMapGeometry";
import { useMapMarkers } from "../hooks/useMapMarkers";
import { isMarkerMapMode } from "../lib/mapMarkers";
import type { FitMode } from "../lib/mapViewportMath";
import {
  installationToMapMarker,
} from "../lib/installationMarkers";
import { warBattleMarkersFromWars } from "../lib/warBattleMarkers";
import {
  settlementToMapMarker,
  visibleSettlementKind,
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
import PaintToolbar from "./map/PaintToolbar";
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
import { MAP_BOUNDS, MAP_DISPLAY_NAMES } from "./map/types";
import { useCharacterSessionToken } from "../hooks/useCharacterSessionToken";
import { useCanEditMap } from "../hooks/useCanEditMap";
import {
  MapAccessError,
  fetchMapBlobUrl,
  fetchMapJson,
  mapApiUrl,
  mapRequiresAuth,
  revokeMapBlobUrl,
  staffMapAccessReason,
} from "@/lib/map/api";
import { editorUrl } from "@/lib/map/editorAccess";
import ChronicleOwnershipLayer from "./chronicle/ChronicleOwnershipLayer";
import { fetchProvinceIdGridQ4 } from "@/app/lib/map/chronicleData";
import { directOwnership } from "@/app/lib/map/chronicleOwnership";
import { CHRONICLE_MODE_SOURCE } from "@/app/lib/map/dataSource";
import {
  buildNationColorLut,
  paintChronicleFrameToImageData,
  type ProvinceIdGrid,
} from "@/app/lib/map/chroniclePaint";

const editTitlesLinkClass =
  "rounded-sm border border-[color-mix(in_srgb,var(--tfmc-cream)_25%,transparent)] bg-[color-mix(in_srgb,var(--tfmc-forest)_40%,transparent)] px-3 py-2 text-sm text-[var(--tfmc-cream)] no-underline transition hover:brightness-110 hover:border-[var(--tfmc-accent)]";

const fitModeLabelClass = (active: boolean) =>
  `text-xs transition ${active ? "text-[var(--tfmc-cream)]" : "text-[var(--tfmc-stone)]"}`;

type MapViewerProps = {
  mapId: MapId;
  /**
   * A chronicle day (`YYYY-MM-DD`) to render instead of the live map, or `null`
   * for the live map. Taken as a prop rather than read from
   * `ChronicleDayContext` so the data flow is visible at the call site and this
   * component stays usable without a provider.
   *
   * Non-null switches every day-scoped source over *and* replaces the three
   * server-rendered nation layers with client-side paints — see the pick canvas
   * effect and `ChronicleOwnershipLayer`.
   */
  day?: string | null;
};

const MapViewer = ({ mapId, day = null }: MapViewerProps) => {
  const chronicle = day !== null;
  /**
   * The modes a stored day can honestly answer for, derived from the same
   * constant the data layer switches on so the toolbar and the fetcher can
   * never disagree about which two those are. `undefined` on the live map,
   * which is what makes `MapToolbar` render its full, unchanged list.
   */
  const availableModes = useMemo(
    () =>
      chronicle
        ? new Set(Object.keys(CHRONICLE_MODE_SOURCE) as MapMode[])
        : undefined,
    [chronicle]
  );
  const sessionToken = useCharacterSessionToken();
  const { canEdit, loading: canEditLoading } = useCanEditMap(mapId, sessionToken);
  const authToken = mapRequiresAuth(mapId) ? sessionToken : null;
  const [gateReason, setGateReason] = useState<MapAccessGateReason | null>(
    null
  );
  const [accessChecked, setAccessChecked] = useState(mapId === "main");

  const [mapType, setMapType] = useState<MapMode>("nation");
  const [fitMode, setFitMode] = useState<FitMode>("contain");
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

  const guildNameCacheRef = useGuildCache(mapId, authToken, day);
  const paint = useMapPaint({ mapId, viewportCoordsRef });

  const {
    mapObjects,
    loadData,
    resetDrillVisibility,
    resetMapObjects,
    getHoverRegion,
    drillDownRegion,
  } = useMapEngine();
  const {
    regionData,
    loading,
    accessError,
    notCapturedForDay,
    dayFileMissing,
  } = useMapModeData({
    mapId,
    mapType,
    loadData,
    sessionToken: authToken,
    day,
  });
  const { layers: titleLayers } = useTitleLayerData(
    mapId,
    mapType,
    regionData,
    authToken,
    day
  );
  const {
    neighbors,
    labelNeighbors,
    centroids,
    labelGrid,
    ready: geometryReady,
  } = useMapGeometry(mapId, authToken);
  const markersEnabled = accessChecked && gateReason === null;
  const { settlements, installations, forts, wars } = useMapMarkers(mapId, authToken, markersEnabled, day);

  const mapMarkers = useMemo(() => {
    if (!isMarkerMapMode(mapType)) return [];
    const battleMarkers = warBattleMarkersFromWars(wars);
    return [
      ...settlements.map((settlement) =>
        settlementToMapMarker({
          ...settlement,
          kind: visibleSettlementKind(
            settlement.kind,
            settlement.faction_id,
            mapObjects
          ),
        })
      ),
      ...installations.map(installationToMapMarker),
      ...battleMarkers,
    ];
  }, [settlements, installations, wars, mapType, mapObjects]);

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

  /**
   * The quarter-scale province id grid every chronicle paint reads. Held in
   * state, not a ref, precisely so the paint effects below re-run when it
   * lands: a ref write cannot wake an effect, and the phase 2 version of this
   * left the canvas blank whenever the grid resolved after the data did.
   *
   * Only fetched for a stored day. The live map still gets its borders and its
   * pick image as server-rendered PNGs and must not pay ~95 KB for this.
   */
  const [chronicleGrid, setChronicleGrid] = useState<ProvinceIdGrid | null>(
    null
  );

  useEffect(() => {
    if (day === null) {
      setChronicleGrid(null);
      return;
    }

    const controller = new AbortController();
    let cancelled = false;

    void fetchProvinceIdGridQ4(mapId, authToken, controller.signal)
      .then((grid) => {
        if (!cancelled) setChronicleGrid(grid);
      })
      .catch((err) => {
        if (cancelled || controller.signal.aborted) return;
        console.error("Failed to load chronicle province grid:", err);
      });

    return () => {
      cancelled = true;
      controller.abort();
    };
    // `day` only gates the fetch: the grid is geometry, shared by every day.
  }, [mapId, authToken, day]);

  const mapCanvasMounted =
    !loading && !(mapId === "main" && !geometryReady);

  // Pick pixels are read from the hidden canvas inside MapCanvas. That node
  // does not exist until loading/geometry finish, so this effect must wait
  // for mapCanvasMounted or it draws once into a null ref and never retries.
  useEffect(() => {
    if (!accessChecked || gateReason || !mapCanvasMounted) {
      return;
    }

    let blobUrl: string | null = null;
    let cancelled = false;
    let retryId = 0;
    let retries = 0;

    const drawImage = async () => {
      const canvas = canvasRef.current;
      if (!canvas) {
        if (retries++ > 60) return;
        retryId = requestAnimationFrame(() => {
          if (!cancelled) void drawImage();
        });
        return;
      }
      // getImageData runs per hover frame; keep the backing store CPU-side.
      const ctx = canvas.getContext("2d", { willReadFrequently: true });
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
        // Resizing re-allocates the (6400x6400 => ~164MB) backing store, so
        // only touch the dimensions when the pick image actually changed size.
        if (canvas.width !== img.width || canvas.height !== img.height) {
          canvas.width = img.width;
          canvas.height = img.height;
        }
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
    // `/mapdata/` is regenerated from today's data and has no per-day variant,
    // so a stored day must not download it — the effect below paints the pick
    // canvas from that day's own ownership instead.
    if (day === null) void drawImage();

    return () => {
      cancelled = true;
      cancelAnimationFrame(retryId);
      revokeMapBlobUrl(blobUrl);
    };
  }, [
    mapId,
    mapType,
    accessChecked,
    gateReason,
    authToken,
    mapCanvasMounted,
    day,
  ]);

  /**
   * Chronicle mode's pick canvas.
   *
   * Painted from `directOwnership` — every region in its *own* colour over its
   * *own* provinces — because that is what `/mapdata/{mode}` is: coloured by
   * direct owner, which is why `getHoverRegion` walks up the `overlord` chain
   * to find a visible ancestor. Since `useMapHover`'s `rgbToId` is built from
   * the same day's `regionData`, this makes hover, click, nation details and
   * drill-down day-correct with no change to any hover code.
   *
   * The canvas is 1600x1600 here rather than the live 6400x6400, so a pick can
   * disagree with the drawn border by up to 4 map pixels at the very edge of a
   * nation. That is the same 16x memory trade `ChronicleOwnershipLayer` makes,
   * and the two layers agree with each other because they read the same grid.
   */
  useEffect(() => {
    if (day === null) return;
    if (!accessChecked || gateReason || !mapCanvasMounted) return;
    if (!chronicleGrid || !regionData) return;

    let cancelled = false;
    let retryId = 0;
    let retries = 0;

    const paintPickCanvas = () => {
      const canvas = canvasRef.current;
      if (!canvas) {
        // Same wait as the live path: the node lives inside MapCanvas and is
        // not attached on this effect's first run.
        if (retries++ > 60) return;
        retryId = requestAnimationFrame(() => {
          if (!cancelled) paintPickCanvas();
        });
        return;
      }

      const ctx = canvas.getContext("2d", { willReadFrequently: true });
      if (!ctx) return;

      if (
        canvas.width !== chronicleGrid.width ||
        canvas.height !== chronicleGrid.height
      ) {
        canvas.width = chronicleGrid.width;
        canvas.height = chronicleGrid.height;
      }

      const imageData = ctx.createImageData(
        chronicleGrid.width,
        chronicleGrid.height
      );
      paintChronicleFrameToImageData(
        imageData,
        chronicleGrid,
        buildNationColorLut(directOwnership(regionData))
      );
      ctx.putImageData(imageData, 0, 0);
    };

    paintPickCanvas();

    return () => {
      cancelled = true;
      cancelAnimationFrame(retryId);
    };
  }, [
    day,
    accessChecked,
    gateReason,
    mapCanvasMounted,
    chronicleGrid,
    regionData,
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
    day,
    chronicleGrid,
  });

  // Paint mode owns left-click and pointer tracking; the pick canvas is
  // pointer-events-none while it is on, but guard here too so no stale hover
  // state survives the switch.
  const handleCanvasMouseMove = (event: React.MouseEvent<HTMLCanvasElement>) => {
    if (paint.enabled) return;
    onMouseMove(event);
  };

  useEffect(() => {
    if (!paint.enabled) return;
    onHoverLeave();
    setHoveredMarkerId(null);
    setCursorTooltip(null);
    setHoveredOverlay(null);
    setHoveredFortZoc(null);
    setRegionInfo(null);
    lastProvinceIdRef.current = null;
    // onHoverLeave is stable enough for this one-shot cleanup.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [paint.enabled]);

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
    if (paint.enabled) return;
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

  /**
   * Belt and braces with the filtered toolbar above. The toolbar makes these
   * modes unreachable through the UI; this makes them harmless if one is
   * reached anyway — a bookmarked URL, a future mode nobody remembers to add
   * to `CHRONICLE_MODE_SOURCE`, a state bug. `notCapturedForDay` is only ever
   * set from `MapModeNotCapturedError`, which `mapModeDataSource` only throws
   * for a non-null day, so this branch is unreachable on the live map.
   */
  if (notCapturedForDay) {
    return (
      <div className="flex min-h-[calc(100dvh-var(--tfmc-header-h))] flex-col items-center justify-center gap-3 bg-[var(--tfmc-forest-deep)] px-6 text-center">
        <p className="font-[family-name:var(--font-fraunces)] text-2xl text-[var(--tfmc-cream)]">
          Not recorded for {day}
        </p>
        <p className="max-w-md text-sm leading-snug text-[var(--tfmc-stone)]">
          The daily capture stores nation and trade data only. There is no
          stored answer for this map mode on this day, and showing today&rsquo;s
          would be a lie about the past.
        </p>
        <button
          type="button"
          onClick={() => handleMapTypeChange("nation")}
          className={editTitlesLinkClass}
        >
          Back to the nation map
        </button>
      </div>
    );
  }

  /**
   * The mode *is* captured for chronicle days, but this day's snapshot is
   * missing that source file. Kept separate from `notCapturedForDay` above
   * because the fact differs: nothing was ever recorded there, whereas here
   * the recording exists and lost a piece. Falling through to the map instead
   * would render bare terrain with no nations under a banner asserting a real
   * date — an empty world that reads as a real historical state.
   */
  if (dayFileMissing) {
    return (
      <div className="flex min-h-[calc(100dvh-var(--tfmc-header-h))] flex-col items-center justify-center gap-3 bg-[var(--tfmc-forest-deep)] px-6 text-center">
        <p className="font-[family-name:var(--font-fraunces)] text-2xl text-[var(--tfmc-cream)]">
          Missing from the {day} capture
        </p>
        <p className="max-w-md text-sm leading-snug text-[var(--tfmc-stone)]">
          This day was recorded, but the file behind this map mode is not in
          its snapshot. Nothing is shown rather than an empty world under a
          real date. Another mode, or a nearby day, may still have it.
        </p>
        <button
          type="button"
          onClick={() => handleMapTypeChange("nation")}
          className={editTitlesLinkClass}
        >
          Back to the nation map
        </button>
      </div>
    );
  }

  // Do not render the map until region data is in hand. Mounting MapCanvas
  // early (to start the base-map download sooner) meant the region overlays
  // rendered before regionData settled, and a failed overlay request is made
  // permanent by MapCanvas's onError handler setting display:none — borders
  // then stay invisible until something forces a remount.
  if (!mapCanvasMounted) {
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
        headerAction={
          // The editor writes to the *live* map. Reaching it from a stored day
          // would invite editing today's titles while looking at last year's.
          !chronicle && canEdit && !canEditLoading ? (
            <Link href={editorUrl(mapId)} className={editTitlesLinkClass}>
              Edit titles
            </Link>
          ) : null
        }
        mapModeSelectorMobile={
          <MapToolbar
            mapId={mapId}
            mapType={mapType}
            onMapTypeChange={handleMapTypeChange}
            variant="bar"
            availableModes={availableModes}
          />
        }
        mapModeSelectorDesktop={
          <MapToolbar
            mapId={mapId}
            mapType={mapType}
            onMapTypeChange={handleMapTypeChange}
            variant="sidebar"
            availableModes={availableModes}
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
        fitModeToggle={
          <div className="flex items-center gap-1.5">
            <span className={fitModeLabelClass(fitMode === "cover")}>Width</span>
            <button
              type="button"
              role="switch"
              aria-checked={fitMode === "contain"}
              aria-label="Toggle between filling the width and fitting the height"
              onClick={() =>
                setFitMode((mode) => (mode === "cover" ? "contain" : "cover"))
              }
              className="relative h-4 w-8 shrink-0 rounded-full bg-[color-mix(in_srgb,var(--tfmc-forest)_60%,transparent)] transition-colors"
            >
              <span
                className="absolute top-0.5 left-0.5 h-3 w-3 rounded-full bg-[var(--tfmc-cream)]"
                style={{
                  transform: `translateX(${fitMode === "contain" ? 16 : 0}px)`,
                  transition: "transform 150ms ease",
                }}
              />
            </button>
            <span className={fitModeLabelClass(fitMode === "contain")}>Height</span>
          </div>
        }
        paintPanel={chronicle ? null : <PaintToolbar paint={paint} />}
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
          wars={wars}
          centroids={centroids}
          hoveredMarkerId={hoveredMarkerId}
          hoveredNationId={selectedRegionId}
          onMouseMove={handleCanvasMouseMove}
          onMouseLeave={handleMouseLeave}
          onClick={handleMapClick}
          isHoveringClickable={isHoveringClickable}
          fill
          fitMode={fitMode}
          paint={chronicle ? undefined : paint}
          regionOverlay={
            chronicle ? (
              <ChronicleOwnershipLayer
                grid={chronicleGrid}
                regionData={regionData}
                mapObjects={mapObjects}
                // `selectedRegionId` is the region the pick canvas resolved,
                // but it is not cleared on a miss — `hoveredOverlay` is, and it
                // is set from the same resolution, so it is the honest gate for
                // "is something hovered right now".
                hoveredRegionId={hoveredOverlay ? selectedRegionId : null}
                mapW={MAP_BOUNDS[mapId]}
                mapH={MAP_BOUNDS[mapId]}
              />
            ) : undefined
          }
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
