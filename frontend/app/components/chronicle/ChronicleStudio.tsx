"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { useCharacterSessionToken } from "../../hooks/useCharacterSessionToken";
import { useMapGeometry } from "../../hooks/useMapGeometry";
import { useMapViewport } from "../../hooks/useMapViewport";
import { computeVisibleNationLabels } from "../../lib/mapLabels";
import type { NationLabelSpec } from "../../lib/mapLabels";
import { buildNationColorLut } from "../../lib/map/chroniclePaint";
import {
  computeChronicleBorderMask,
  type ChronicleBorderMask,
} from "../../lib/map/chronicleBorderMask";
import ChronicleBorderCanvas from "./ChronicleBorderCanvas";
import type { ProvinceIdGrid } from "../../lib/map/chroniclePaint";
import {
  CHRONICLE_FETCH_CONCURRENCY,
  DEFAULT_CHRONICLE_RENDER_SIZE,
  EMPTY_CHRONICLE_COST_SAMPLE,
  disposeChronicleFrames,
  estimateChronicleBuild,
  chronicleBuildBlockReason,
  isChronicleBuildCancelled,
  runChronicleBuild,
  selectChronicleRange,
  ChronicleBuildCancelled,
  type ChronicleBuildProgress,
  type ChronicleCostSample,
  type ChronicleDayLoad,
  type ChronicleFrame,
} from "../../lib/map/chronicleBuild";
import {
  fetchChronicleDayFile,
  fetchChronicleDayMarkers,
  fetchChronicleIndex,
  fetchProvinceIdGridQ4,
  isChronicleDayFileMissing,
  type ChronicleIndex,
} from "../../lib/map/chronicleData";
import {
  MapAccessError,
  isAbortError,
  mapRequiresAuth,
  staffMapAccessReason,
} from "@/lib/map/api";
import MapAccessGate, { type MapAccessGateReason } from "../map/MapAccessGate";
import MapAuthImage from "../map/MapAuthImage";
import MapMarkerLayer from "../map/MapMarkerLayer";
import MapViewport from "../map/MapViewport";
import LabelLayer from "../map/LabelLayer";
import WarCampaignLineLayer from "../map/WarCampaignLineLayer";
import {
  MAP_BOUNDS,
  MAP_DISPLAY_NAMES,
  type MapId,
  type MapMarkersResponse,
  type RegionRecord,
} from "../map/types";
import { chronicleDayHref } from "../../lib/map/chronicleDayRoute";
import {
  ChronicleBuildPanel,
  ChroniclePlaybackPanel,
  ChronicleRangePanel,
  ChronicleTogglePanel,
  chroniclePanelClass,
} from "./ChroniclePanels";
import {
  CHRONICLE_TOGGLES_OFF,
  EMPTY_CHRONICLE_LAYERS,
  buildChronicleLayers,
  chronicleLabelMapObjects,
  chronicleRegionData,
  chronicleToggleSignature,
  needsMarkers,
  needsNationFile,
  type ChronicleFrameLayers,
  type ChronicleToggleKey,
  type ChronicleToggles,
} from "./chronicleLayers";
import {
  clearChronicleCanvas,
  createChronicleRenderTarget,
  drawChronicleBitmap,
  renderChronicleFrame,
  type ChronicleRenderTarget,
} from "./chronicleRenderTarget";

/**
 * The timelapse studio: compose the look, pick a range, see what it costs,
 * build every frame in one pass, then play it.
 *
 * The whole design turns on one rule — playback issues no requests. Every day's
 * pixels, labels and markers are fetched and computed during the build pass and
 * held in memory, so scrubbing the slider is a `drawImage` and an array swap.
 */

/** Painted ownership sits under the parchment's texture, not on top of it. */
const CHRONICLE_FILL_OPACITY = 0.88;

/** How many days back the range opens on, when the map has that many. */
const DEFAULT_RANGE_DAYS = 25;

type ChronicleStage = "compose" | "range" | "build" | "play";

type ChronicleDay = ChronicleDayLoad & {
  nation: RegionRecord | null;
  markers: MapMarkersResponse | null;
};

type StudioFrame = ChronicleFrame<ImageBitmap, ChronicleFrameLayers>;

/** Measured once per source so the estimate can re-derive itself per toggle. */
type SourceCost = { bytes: number; ms: number };

export default function ChronicleStudio({ mapId }: { mapId: MapId }) {
  const sessionToken = useCharacterSessionToken();
  const authToken = mapRequiresAuth(mapId) ? sessionToken : null;
  const mapDisplayName = MAP_DISPLAY_NAMES[mapId];

  const [index, setIndex] = useState<ChronicleIndex | null>(null);
  const [indexError, setIndexError] = useState<string | null>(null);
  const [gateReason, setGateReason] = useState<MapAccessGateReason | null>(null);
  const [indexLoading, setIndexLoading] = useState(true);

  const [stage, setStage] = useState<ChronicleStage>("compose");
  const [toggles, setToggles] = useState<ChronicleToggles>(CHRONICLE_TOGGLES_OFF);
  const [notice, setNotice] = useState<string | null>(null);
  const [layerError, setLayerError] = useState<string | null>(null);
  const [layersLoading, setLayersLoading] = useState(false);

  const [previewNation, setPreviewNation] = useState<RegionRecord | null>(null);
  const [previewMarkers, setPreviewMarkers] =
    useState<MapMarkersResponse | null>(null);

  const [rangeStart, setRangeStart] = useState<string | null>(null);
  const [rangeEnd, setRangeEnd] = useState<string | null>(null);
  const [renderSize, setRenderSize] = useState(DEFAULT_CHRONICLE_RENDER_SIZE);

  const [buildProgress, setBuildProgress] =
    useState<ChronicleBuildProgress | null>(null);
  const [buildError, setBuildError] = useState<string | null>(null);
  const [skippedDays, setSkippedDays] = useState<string[]>([]);

  const [playIndex, setPlayIndex] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [speed, setSpeed] = useState(4);
  const [loop, setLoop] = useState(true);

  const [mapSize, setMapSize] = useState({
    w: MAP_BOUNDS[mapId],
    h: MAP_BOUNDS[mapId],
  });
  // The three halves of a day's CPU cost, each measured on the compose preview
  // and each only required when the toggle that pays for it is on.
  const [frameMs, setFrameMs] = useState<number | null>(null);
  const [labelMs, setLabelMs] = useState<number | null>(null);
  const [borderMs, setBorderMs] = useState<number | null>(null);
  const [layerMs, setLayerMs] = useState<number | null>(null);
  const [nationCost, setNationCost] = useState<SourceCost | null>(null);
  const [markersCost, setMarkersCost] = useState<SourceCost | null>(null);

  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const gridRef = useRef<ProvinceIdGrid | null>(null);
  const gridPromiseRef = useRef<Promise<ProvinceIdGrid> | null>(null);
  const previewTargetRef = useRef<{
    target: ChronicleRenderTarget;
    size: number;
  } | null>(null);
  // The grid lives in a ref because the paint path wants it synchronously, but a
  // ref write cannot wake an effect. This counter is the render-visible half:
  // without it, whether the preview ever painted came down to which promise
  // resolved last - the grid arriving after the day's nation data left the
  // canvas blank with no error anywhere.
  const [gridVersion, setGridVersion] = useState(0);
  const framesRef = useRef<StudioFrame[]>([]);
  const abortRef = useRef<AbortController | null>(null);
  /**
   * `abortRef` alone is not enough to stop a second build. The build panel's
   * Back button cancels and returns to the range step, which re-enables Build —
   * but a build parked on a fetch keeps running until that fetch resolves, and
   * a second click would overwrite `abortRef` and leave the first build both
   * unreferenced and uncancellable. One flag, cleared only by the build that
   * set it, keeps exactly one build alive at a time.
   */
  const buildingRef = useRef(false);
  // The ref is the guard (two clicks can land in one tick, before any re-render);
  // this is the same fact in a form the panels can render a reason from.
  const [building, setBuilding] = useState(false);
  // Preview fetches are cancelled on unmount only: aborting them whenever this
  // component re-renders would race the once-per-source `attemptedRef` guard and
  // leave a source neither fetched nor retried.
  const previewAbortRef = useRef<AbortController | null>(null);
  const previewAbortSignal = useCallback((): AbortSignal => {
    if (!previewAbortRef.current) previewAbortRef.current = new AbortController();
    return previewAbortRef.current.signal;
  }, []);
  // Bumped whenever `framesRef` is replaced, so the render reads the new array.
  const [framesVersion, setFramesVersion] = useState(0);

  const viewport = useMapViewport({ mapSize, fitMode: "contain" });
  const geometry = useMapGeometry(mapId, authToken);
  // `useMapGeometry` only serves the main map, so nation names cannot be drawn
  // anywhere else. The toggle says so rather than rendering an empty layer.
  const namesSupported = mapId === "main";

  const days = useMemo(() => index?.days ?? [], [index]);
  const incompleteSet = useMemo(
    () => new Set((index?.incomplete_days ?? []).map((entry) => entry.day)),
    [index]
  );
  const previewDay = index?.last ?? null;

  useEffect(() => {
    let cancelled = false;
    setIndexLoading(true);
    setIndexError(null);
    setGateReason(null);

    fetchChronicleIndex(mapId, authToken)
      .then((loaded) => {
        if (cancelled) return;
        setIndex(loaded);
        const last = loaded.last;
        const first =
          loaded.days.length > DEFAULT_RANGE_DAYS
            ? loaded.days[loaded.days.length - DEFAULT_RANGE_DAYS]!
            : loaded.first;
        setRangeStart(first ?? null);
        setRangeEnd(last ?? null);
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        if (err instanceof MapAccessError && err.status === 403) {
          setGateReason(staffMapAccessReason(err));
          return;
        }
        setIndexError(
          err instanceof Error ? err.message : "Failed to load the chronicle."
        );
      })
      .finally(() => {
        if (!cancelled) setIndexLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [mapId, authToken]);

  // The grid is fetched under one session's credentials. After a login or a
  // logout in another tab `authToken` changes underneath us, and a cached grid
  // from the old session would keep being served to every later frame. Drop it
  // — and any fetch still in flight for it — whenever the identity changes.
  useEffect(() => {
    gridRef.current = null;
    gridPromiseRef.current = null;
    previewTargetRef.current = null;
    setGridVersion((version) => version + 1);
  }, [mapId, authToken]);

  const ensureGrid = useCallback(
    async (signal?: AbortSignal): Promise<ProvinceIdGrid> => {
      if (gridRef.current) return gridRef.current;
      // Share one in-flight fetch: compose and build can both ask for the grid
      // before either has it, and the artifact is the same 95 KB either way.
      if (!gridPromiseRef.current) {
        gridPromiseRef.current = fetchProvinceIdGridQ4(mapId, authToken, signal)
          .then((grid) => {
            gridRef.current = grid;
            setGridVersion((version) => version + 1);
            return grid;
          })
          .catch((err) => {
            gridPromiseRef.current = null;
            throw err;
          });
      }
      return gridPromiseRef.current;
    },
    [mapId, authToken]
  );

  /**
   * One render target for the whole session: the compose preview and the build
   * paint through the same scratch canvas, so the timing the preview reports is
   * the timing the build will pay, and the 1600x1600 scratch buffer is only
   * ever allocated once.
   */
  const ensureRenderTarget = useCallback(
    (grid: ProvinceIdGrid): ChronicleRenderTarget => {
      const existing = previewTargetRef.current;
      if (
        existing &&
        existing.size === renderSize &&
        existing.target.grid === grid
      ) {
        return existing.target;
      }
      const target = createChronicleRenderTarget(grid, renderSize, renderSize);
      previewTargetRef.current = { target, size: renderSize };
      return target;
    },
    [renderSize]
  );

  /**
   * Each source times itself as it arrives: the build estimate is measured from
   * the bytes and milliseconds already spent rather than guessed at.
   */
  const loadNationFile = useCallback(
    async (day: string, signal?: AbortSignal) => {
      const startedAt = performance.now();
      const file = await fetchChronicleDayFile<RegionRecord>(
        mapId,
        day,
        "nation",
        authToken,
        signal
      );
      // Only the first fetch is recorded: one sample is all the estimate needs,
      // and re-recording would queue a render behind every day of a build.
      const cost = {
        bytes: file.byteLength,
        ms: Math.max(1, performance.now() - startedAt),
      };
      setNationCost((current) => current ?? cost);
      return file;
    },
    [mapId, authToken]
  );

  const loadMarkersFile = useCallback(
    async (day: string, signal?: AbortSignal) => {
      const startedAt = performance.now();
      try {
        const file = await fetchChronicleDayMarkers(mapId, day, authToken, signal);
        const cost = {
          bytes: file.byteLength,
          ms: Math.max(1, performance.now() - startedAt),
        };
        setMarkersCost((current) => current ?? cost);
        return file;
      } catch (err) {
        // A day with no stored markers still has a map worth painting.
        if (isChronicleDayFileMissing(err)) return null;
        throw err;
      }
    },
    [mapId, authToken]
  );

  const loadDay = useCallback(
    async (
      day: string,
      wantNation: boolean,
      wantMarkers: boolean,
      signal?: AbortSignal
    ): Promise<ChronicleDay | null> => {
      let nation: RegionRecord | null = null;
      let markers: MapMarkersResponse | null = null;
      let byteLength = 0;
      let fingerprint: string | null = null;

      if (wantNation) {
        const file = await loadNationFile(day, signal);
        nation = file.value;
        fingerprint = file.fingerprint;
        byteLength += file.byteLength;
      }
      if (wantMarkers) {
        const file = await loadMarkersFile(day, signal);
        if (file) {
          markers = file.value;
          byteLength += file.byteLength;
        }
      }

      return {
        nation,
        markers,
        nationFingerprint: fingerprint,
        byteLength,
        incomplete: incompleteSet.has(day),
      };
    },
    [loadNationFile, loadMarkersFile, incompleteSet]
  );

  const wantNation = needsNationFile(toggles);
  const wantMarkers = needsMarkers(toggles);
  // One attempt per source: stops two quick toggles from starting the same
  // fetch twice, and stops a day that genuinely has no markers from being asked
  // for again every time another layer is switched. Cleared on failure so a
  // later toggle can retry.
  const attemptedRef = useRef({ nation: false, markers: false });

  // Compose preview: pull a source only when a toggle that needs it turns on,
  // and only once. Switching a layer back off keeps what was fetched — the
  // layer components and the paint pass gate on the toggles themselves, so
  // re-enabling one costs nothing.
  useEffect(() => {
    if (!previewDay) return;
    const fetchNation =
      wantNation && !previewNation && !attemptedRef.current.nation;
    const fetchMarkers =
      wantMarkers && !previewMarkers && !attemptedRef.current.markers;
    if (!fetchNation && !fetchMarkers) return;

    let cancelled = false;
    const signal = previewAbortSignal();
    setLayersLoading(true);
    setLayerError(null);

    const load = async () => {
      try {
        if (fetchNation) {
          attemptedRef.current.nation = true;
          // No signal on the grid: it is shared with the build, and one panel
          // re-render must not tear down a fetch the build is waiting on.
          await ensureGrid();
          const file = await loadNationFile(previewDay, signal);
          if (!cancelled) setPreviewNation(file.value);
        }
        if (fetchMarkers) {
          attemptedRef.current.markers = true;
          const file = await loadMarkersFile(previewDay, signal);
          if (!cancelled) setPreviewMarkers(file?.value ?? null);
        }
      } catch (err) {
        // Our own abort, or a grid fetch some other caller cancelled — neither
        // is something to put in front of the user.
        if (cancelled || isAbortError(err)) return;
        attemptedRef.current = { nation: false, markers: false };
        setLayerError(
          err instanceof Error
            ? err.message
            : `Failed to load ${previewDay}'s layers.`
        );
      } finally {
        if (!cancelled) setLayersLoading(false);
      }
    };

    void load();
    return () => {
      cancelled = true;
    };
  }, [
    previewDay,
    wantNation,
    wantMarkers,
    previewNation,
    previewMarkers,
    ensureGrid,
    loadNationFile,
    loadMarkersFile,
  ]);

  const previewRegionData = useMemo(
    () => chronicleRegionData(previewNation),
    [previewNation]
  );
  const previewLabelObjects = useMemo(
    () => chronicleLabelMapObjects(previewRegionData, previewNation),
    [previewRegionData, previewNation]
  );

  const computeLabels = useCallback(
    (
      regionData: ReturnType<typeof chronicleRegionData>,
      labelObjects: ReturnType<typeof chronicleLabelMapObjects>
    ): NationLabelSpec[] | null => {
      const { neighbors, labelNeighbors, centroids, labelGrid } = geometry;
      // Null, not []. An empty array is a legitimate answer for a day with no
      // realms; "the geometry has not landed" is not an answer at all, and
      // returning [] for it let the estimate time the empty path and let the
      // build write unlabelled frames while the names toggle was on.
      if (!namesSupported || !geometry.ready || !neighbors || !centroids) {
        return null;
      }
      if (!Object.keys(regionData).length) return [];
      return computeVisibleNationLabels(
        regionData,
        neighbors,
        centroids,
        labelObjects,
        {
          grid: labelGrid ?? undefined,
          labelNeighbors: labelNeighbors ?? neighbors,
        }
      );
    },
    [geometry, namesSupported]
  );

  // The label pass is the most expensive thing a chronicle day does — connected
  // components across every province of every realm — so it is timed here on a
  // real day rather than assumed. `ms` stays null when there was no realm to
  // label, which would otherwise record a suspiciously free measurement.
  const previewLabels = useMemo(() => {
    if (!toggles.nationNames || !Object.keys(previewRegionData).length) {
      return { labels: [] as NationLabelSpec[], ms: null as number | null };
    }
    const startedAt = performance.now();
    const labels = computeLabels(previewRegionData, previewLabelObjects);
    // No geometry yet, so nothing was measured. Reporting `ms: 0.02` here made
    // the panel promise "about 0.95 s" for a build that really costs ~63 s.
    if (labels == null) {
      return { labels: [] as NationLabelSpec[], ms: null as number | null };
    }
    return { labels, ms: performance.now() - startedAt };
  }, [
    toggles.nationNames,
    computeLabels,
    previewRegionData,
    previewLabelObjects,
  ]);

  // Computed on the preview day so the estimate quotes a measured border pass,
  // exactly as it does for the label pass. `gridVersion` is the dependency
  // rather than the ref, which React cannot see change.
  const previewBorders = useMemo(() => {
    const grid = gridRef.current;
    if (!toggles.nationBorders || !grid || !previewNation) {
      return {
        mask: null as ChronicleBorderMask | null,
        ms: null as number | null,
      };
    }
    const startedAt = performance.now();
    const mask = computeChronicleBorderMask(grid, previewNation);
    return { mask, ms: performance.now() - startedAt };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [toggles.nationBorders, previewNation, gridVersion]);

  useEffect(() => {
    if (previewBorders.ms != null) setBorderMs(previewBorders.ms);
  }, [previewBorders]);

  const previewLayers = useMemo(() => {
    const startedAt = performance.now();
    const layers = buildChronicleLayers({
      toggles,
      markers: previewMarkers,
      labels: previewLabels.labels,
      labelObjects: previewLabelObjects,
      borders: previewBorders.mask,
    });
    return {
      layers,
      // Marker layout is only worth timing when there were markers to lay out.
      ms: previewMarkers ? performance.now() - startedAt : null,
    };
  }, [
    toggles,
    previewMarkers,
    previewLabels.labels,
    previewLabelObjects,
    previewBorders.mask,
  ]);

  useEffect(() => {
    if (previewLabels.ms != null) setLabelMs(previewLabels.ms);
  }, [previewLabels]);

  useEffect(() => {
    if (previewLayers.ms != null) setLayerMs(previewLayers.ms);
  }, [previewLayers]);

  // The compose preview *is* a build frame: same render target, same downscale,
  // same `transferToImageBitmap`. Two things fall out of that — what the user
  // composes is exactly what playback will show, and the time this takes is the
  // per-frame time the build will pay rather than a fraction of it.
  useEffect(() => {
    // Compose only. The build paints through this same render target, and on the
    // `createImageBitmap` fallback path the two interleave and tear each other's
    // frames; `stage === "play"` alone let the preview run right through a build.
    if (stage !== "compose") return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const grid = gridRef.current;
    if (!toggles.nationFill || !previewNation || !grid) {
      clearChronicleCanvas(canvas);
      setFrameMs(null);
      return;
    }

    let cancelled = false;
    const paint = async () => {
      const target = ensureRenderTarget(grid);
      const startedAt = performance.now();
      const { bitmap } = await renderChronicleFrame(
        target,
        buildNationColorLut(previewNation)
      );
      const ms = performance.now() - startedAt;
      if (cancelled) {
        bitmap.close();
        return;
      }
      drawChronicleBitmap(canvas, bitmap);
      // `drawImage` copies synchronously and no frame array holds this one.
      bitmap.close();
      setFrameMs(ms);
    };

    void paint();
    return () => {
      cancelled = true;
    };
  }, [
    stage,
    toggles.nationFill,
    previewNation,
    gridVersion,
    ensureRenderTarget,
  ]);

  const toggleSignature = useMemo(
    () => chronicleToggleSignature(toggles),
    [toggles]
  );

  /**
   * A sample is only offered once every layer that is switched on has been
   * measured on the preview day. Anything short of that returns the empty
   * sample, whose null signature makes the estimate admit it is guessing.
   */
  const costSample: ChronicleCostSample = useMemo(() => {
    const wantNation = needsNationFile(toggles);
    const wantMarkers = needsMarkers(toggles);
    const sources: SourceCost[] = [];

    if (wantNation) {
      if (!nationCost) return EMPTY_CHRONICLE_COST_SAMPLE;
      sources.push(nationCost);
    }
    if (wantMarkers) {
      if (!markersCost) return EMPTY_CHRONICLE_COST_SAMPLE;
      sources.push(markersCost);
    }
    if (!sources.length) return EMPTY_CHRONICLE_COST_SAMPLE;

    if (toggles.nationFill && frameMs == null) {
      return EMPTY_CHRONICLE_COST_SAMPLE;
    }
    if (toggles.nationBorders && borderMs == null) {
      return EMPTY_CHRONICLE_COST_SAMPLE;
    }
    if (toggles.nationNames && labelMs == null) {
      return EMPTY_CHRONICLE_COST_SAMPLE;
    }
    if (wantMarkers && layerMs == null) return EMPTY_CHRONICLE_COST_SAMPLE;

    const bytes = sources.reduce((sum, cost) => sum + cost.bytes, 0);
    const ms = sources.reduce((sum, cost) => sum + cost.ms, 0);

    return {
      signature: toggleSignature,
      bytesPerDay: bytes,
      bytesPerMs: ms > 0 ? bytes / ms : null,
      // Only the layers that are on contribute: a build with no names never
      // runs the label pass, so its cost must not be carried into the estimate.
      cpuMsPerDay:
        (toggles.nationFill ? frameMs! : 0) +
        (toggles.nationBorders ? borderMs! : 0) +
        (toggles.nationNames ? labelMs! : 0) +
        (wantMarkers ? layerMs! : 0),
    };
  }, [
    toggles,
    toggleSignature,
    nationCost,
    markersCost,
    frameMs,
    borderMs,
    labelMs,
    layerMs,
  ]);

  const selection = useMemo(
    () =>
      selectChronicleRange(
        { days, incomplete_days: index?.incomplete_days ?? [] },
        rangeStart,
        rangeEnd
      ),
    [days, index, rangeStart, rangeEnd]
  );

  const estimate = useMemo(
    () =>
      estimateChronicleBuild({
        dayCount: selection.days.length,
        sample: costSample,
        signature: toggleSignature,
        renderWidth: renderSize,
        renderHeight: renderSize,
      }),
    [selection.days.length, costSample, toggleSignature, renderSize]
  );

  /**
   * The label pass needs `useMapGeometry`'s five fetches to have landed. Until
   * they do it returns nothing in microseconds, which is both an unmeasurable
   * estimate and an unlabelled build — so names being on makes the geometry a
   * hard prerequisite rather than a nice-to-have.
   */
  const geometryReady = Boolean(
    geometry.ready && geometry.neighbors && geometry.centroids
  );

  const buildBlockReason = useMemo(
    () =>
      chronicleBuildBlockReason({
        selectionError: selection.error,
        dayCount: selection.days.length,
        building,
        nationNames: toggles.nationNames,
        namesSupported,
        geometryReady,
        overCeiling: estimate.overCeiling,
      }),
    [
      selection,
      building,
      toggles.nationNames,
      namesSupported,
      geometryReady,
      estimate.overCeiling,
    ]
  );

  /** Step 1 only cares about the geometry; the range is not picked yet. */
  const composeBlockReason =
    toggles.nationNames && namesSupported && !geometryReady
      ? "Still loading label geometry — nation names cannot be measured or drawn yet."
      : null;

  const discardFrames = useCallback(() => {
    if (!framesRef.current.length) return;
    disposeChronicleFrames(framesRef.current, (bitmap) => bitmap.close());
    framesRef.current = [];
    setFramesVersion((version) => version + 1);
    setPlayIndex(0);
    setPlaying(false);
  }, []);

  // Frames are painted from one set of toggles; changing them makes every one
  // of them a lie. Say so and go back to compose instead of silently rebuilding.
  useEffect(() => {
    if (!framesRef.current.length) return;
    discardFrames();
    setStage("compose");
    setNotice(
      "Layers changed, so the built frames were discarded. Build again when the look is right."
    );
  }, [toggles, discardFrames]);

  useEffect(() => {
    if (!framesRef.current.length) return;
    discardFrames();
    setStage("range");
    setNotice("The range changed, so the built frames were discarded.");
  }, [rangeStart, rangeEnd, renderSize, discardFrames]);

  useEffect(() => {
    return () => {
      abortRef.current?.abort();
      previewAbortRef.current?.abort();
      disposeChronicleFrames(framesRef.current, (bitmap) => bitmap.close());
      framesRef.current = [];
    };
  }, []);

  const startBuild = useCallback(async () => {
    // The disabled button is a hint; this is the guard. A second click while the
    // first build is parked on a fetch must not start a build that nothing holds
    // a reference to, and `estimate.overCeiling` must be re-checked here rather
    // than trusted from a button that a stage change already re-enabled.
    if (buildingRef.current || buildBlockReason) return;

    buildingRef.current = true;
    setBuilding(true);
    const controller = new AbortController();
    abortRef.current = controller;
    // Every write below is guarded on this: only the build that still owns
    // `abortRef` may touch the stage, the frames or the progress bar. A build
    // that lost the ref is a ghost and must land silently.
    const owns = () => abortRef.current === controller;
    discardFrames();
    setStage("build");
    setBuildError(null);
    setBuildProgress({
      completed: 0,
      total: selection.days.length,
      day: selection.days[0]!,
      painted: 0,
      reused: 0,
      skipped: 0,
    });

    setSkippedDays([]);
    // One measurement per build is enough, and it keeps the paint pass from
    // queueing a React update between every pair of frames.
    let measuredPaint = false;

    try {
      const grid = wantNation ? await ensureGrid(controller.signal) : null;
      // The same target the compose preview painted through: one
      // grid-resolution scratch buffer and one small output canvas, reused for
      // every day of the build.
      const target =
        grid && toggles.nationFill ? ensureRenderTarget(grid) : null;

      // Labels are a pure function of the nation file, so a day whose
      // fingerprint matches the one before it reuses them exactly as it reuses
      // the frame. On a quiet stretch that skips the single most expensive step
      // in the pass.
      let lastLabels: {
        fingerprint: string | null;
        labels: NationLabelSpec[];
      } | null = null;
      // Borders are a pure function of the nation file too, so an unchanged day
      // shares the previous day's mask object rather than walking 2.5M grid
      // cells again — a reused day costs zero extra bytes, not even a copy.
      let lastBorders: {
        fingerprint: string | null;
        mask: ChronicleBorderMask | null;
      } | null = null;

      const result = await runChronicleBuild<
        ChronicleDay,
        ImageBitmap,
        ChronicleFrameLayers
      >({
        days: selection.days,
        concurrency: CHRONICLE_FETCH_CONCURRENCY,
        signal: controller.signal,
        onProgress: (progress) => {
          if (owns()) setBuildProgress(progress);
        },
        effects: {
          loadDay: async (day, signal) => {
            try {
              return await loadDay(day, wantNation, wantMarkers, signal);
            } catch (err) {
              if (signal?.aborted) throw new ChronicleBuildCancelled();
              // A day missing its sources is a hole in the history, not a
              // failure: the build reports it and carries on.
              if (isChronicleDayFileMissing(err)) return null;
              throw err;
            }
          },
          renderDay: async (_day, load) => {
            if (!target || !load.nation) return null;
            const startedAt = performance.now();
            const { bitmap } = await renderChronicleFrame(
              target,
              buildNationColorLut(load.nation)
            );
            // The first real build frame is a better sample than the preview's,
            // and it costs one state update rather than one per day.
            if (!measuredPaint && owns()) {
              measuredPaint = true;
              setFrameMs(performance.now() - startedAt);
            }
            return bitmap;
          },
          buildLayers: (_day, load) => {
            const regionData = chronicleRegionData(load.nation);
            const labelObjects = chronicleLabelMapObjects(
              regionData,
              load.nation
            );

            let labels: NationLabelSpec[] = [];
            if (toggles.nationNames) {
              const reusable =
                lastLabels != null &&
                load.nationFingerprint != null &&
                lastLabels.fingerprint === load.nationFingerprint;
              labels = reusable
                ? lastLabels!.labels
                : (computeLabels(regionData, labelObjects) ?? []);
              lastLabels = { fingerprint: load.nationFingerprint, labels };
            }

            let borders: ChronicleBorderMask | null = null;
            if (toggles.nationBorders && grid && load.nation) {
              const reusable =
                lastBorders != null &&
                load.nationFingerprint != null &&
                lastBorders.fingerprint === load.nationFingerprint;
              borders = reusable
                ? lastBorders!.mask
                : computeChronicleBorderMask(grid, load.nation);
              lastBorders = {
                fingerprint: load.nationFingerprint,
                mask: borders,
              };
            }

            return buildChronicleLayers({
              toggles,
              markers: load.markers,
              labels,
              labelObjects,
              borders,
            });
          },
          disposeImage: (bitmap) => bitmap.close(),
        },
      });

      if (!owns()) {
        // Cancelled and superseded while this build was still in flight. Its
        // frames belong to nobody: hand them back to the GC rather than
        // overwriting the live build's array and leaking it.
        disposeChronicleFrames(result.frames, (bitmap) => bitmap.close());
        return;
      }

      framesRef.current = result.frames;
      setSkippedDays(result.skippedDays);
      setFramesVersion((version) => version + 1);
      setPlayIndex(0);
      setStage(result.frames.length ? "play" : "range");
      if (!result.frames.length) {
        setBuildError("No day in that range had anything to draw.");
      }
    } catch (err) {
      if (!owns()) return;
      if (isChronicleBuildCancelled(err) || isAbortError(err)) {
        setBuildProgress(null);
        setStage("range");
        return;
      }
      setBuildError(
        err instanceof Error ? err.message : "The build failed part-way."
      );
    } finally {
      buildingRef.current = false;
      setBuilding(false);
      // Identity check: a superseded build must not clear the ref belonging to
      // the build that replaced it, which is what made Cancel and Back no-ops.
      if (abortRef.current === controller) abortRef.current = null;
    }
  }, [
    buildBlockReason,
    selection,
    toggles,
    ensureGrid,
    ensureRenderTarget,
    loadDay,
    computeLabels,
    discardFrames,
  ]);

  const cancelBuild = useCallback(() => {
    abortRef.current?.abort();
  }, []);

  const frames = framesRef.current;
  const activeFrame: StudioFrame | null =
    stage === "play" ? (frames[playIndex] ?? null) : null;
  const activeLayers = activeFrame?.layers ?? EMPTY_CHRONICLE_LAYERS;
  const layers = stage === "play" ? activeLayers : previewLayers.layers;

  // Playback and scrubbing are the same two operations: draw the day's bitmap,
  // swap in its precomputed overlays. Nothing here touches the network.
  useEffect(() => {
    if (stage !== "play") return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    drawChronicleBitmap(canvas, framesRef.current[playIndex]?.image ?? null);
  }, [stage, playIndex, framesVersion]);

  // Advancing from a ref rather than from `playIndex` keeps the loop off the
  // effect's dependency list, so a running playback is never torn down and
  // restarted between two frames.
  const playIndexRef = useRef(0);
  useEffect(() => {
    playIndexRef.current = playIndex;
  }, [playIndex]);

  useEffect(() => {
    if (stage !== "play" || !playing) return;
    const total = framesRef.current.length;
    if (total < 2) return;

    let raf = 0;
    let last = performance.now();
    const step = (time: number) => {
      raf = requestAnimationFrame(step);
      const frameIntervalMs = 1000 / speed;
      const elapsed = time - last;
      if (elapsed < frameIntervalMs) return;
      last = time - (elapsed % frameIntervalMs);

      const next = playIndexRef.current + 1;
      if (next < total) {
        playIndexRef.current = next;
        setPlayIndex(next);
      } else if (loop) {
        playIndexRef.current = 0;
        setPlayIndex(0);
      } else {
        setPlaying(false);
      }
    };

    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, [stage, playing, speed, loop, framesVersion]);

  const toggleLayer = useCallback((key: ChronicleToggleKey) => {
    setNotice(null);
    setToggles((current) => ({ ...current, [key]: !current[key] }));
  }, []);

  if (gateReason) {
    return <MapAccessGate reason={gateReason} mapDisplayName={mapDisplayName} />;
  }

  const disabledReasons: Partial<Record<ChronicleToggleKey, string>> =
    namesSupported
      ? {}
      : { nationNames: "Unavailable — label geometry only exists for the live map." };

  const emptyChronicle = !indexLoading && !indexError && days.length === 0;

  return (
    <div className="flex min-h-[calc(100dvh-var(--tfmc-header-h))] flex-col bg-[var(--tfmc-forest-deep)] text-[var(--tfmc-cream)] md:h-[calc(100dvh-var(--tfmc-header-h))] md:overflow-hidden">
      <div className="relative aspect-square w-full min-h-0 md:aspect-auto md:w-auto md:flex-1">
        <div className="relative h-full w-full overflow-hidden">
          <MapViewport
            mapSize={mapSize}
            viewportRef={viewport.viewportRef}
            transformStyle={viewport.transformStyle}
            transformTransition={viewport.transformTransition}
            cursorClassName={viewport.isPanning ? "cursor-grabbing" : "cursor-grab"}
            isPanning={viewport.isPanning}
            fill
          >
            <MapAuthImage
              mapId={mapId}
              path={`/${mapId}/map`}
              sessionToken={authToken}
              alt={`${mapDisplayName} base map`}
              className="pointer-events-none block h-full w-full"
              onLoad={(event) => {
                const img = event.currentTarget;
                if (img.naturalWidth > 0 && img.naturalHeight > 0) {
                  setMapSize((current) =>
                    current.w === img.naturalWidth &&
                    current.h === img.naturalHeight
                      ? current
                      : { w: img.naturalWidth, h: img.naturalHeight }
                  );
                }
              }}
            />
            <canvas
              ref={canvasRef}
              className="pointer-events-none absolute inset-0 z-[12] h-full w-full"
              style={{ opacity: CHRONICLE_FILL_OPACITY }}
            />
            <ChronicleBorderCanvas mask={layers.borders} />
            {layers.wars.length ? (
              <WarCampaignLineLayer
                wars={layers.wars}
                centroids={geometry.centroids}
                mapW={mapSize.w}
                mapH={mapSize.h}
              />
            ) : null}
            {/*
              `alwaysVisible` on both: every layer here is one the user ticked
              on in Compose, so the live map's zoom-size gate would hide the
              thing they asked for. Crowding is theirs to judge — the toggle
              that switched the layer on switches it back off.
            */}
            <MapMarkerLayer
              markers={layers.markers}
              mapW={mapSize.w}
              mapH={mapSize.h}
              mapType="nation"
              displayScale={viewport.displayScale}
              layer="base"
              alwaysVisible
            />
            <LabelLayer
              labels={layers.labels}
              mapW={mapSize.w}
              mapH={mapSize.h}
              displayScale={viewport.displayScale}
              alwaysVisible
            />
          </MapViewport>
        </div>

        <div className="pointer-events-none absolute inset-0 z-10 p-4">
          <div className="pointer-events-auto absolute left-4 top-4 w-72 max-h-[calc(100%-2rem)] space-y-3 overflow-y-auto">
            <div className={`${chroniclePanelClass} p-3`}>
              <p className="text-xs font-medium uppercase tracking-widest text-[var(--tfmc-mist)]">
                Map chronicle
              </p>
              <h1 className="font-[family-name:var(--font-fraunces)] text-xl font-medium tracking-tight text-[var(--tfmc-cream)]">
                {mapDisplayName} timelapse
              </h1>
              <Link
                href={mapId === "main" ? "/map/main" : "/map/r3b1rth"}
                className="mt-2 inline-flex text-xs text-[var(--tfmc-stone)] underline-offset-2 hover:text-[var(--tfmc-cream)]"
              >
                Back to the live map
              </Link>
              {indexLoading ? (
                <p className="mt-2 text-xs text-[var(--tfmc-stone)]">
                  Loading the chronicle index…
                </p>
              ) : null}
              {indexError ? (
                <p className="mt-2 text-xs text-[var(--tfmc-accent)]">
                  {indexError}
                </p>
              ) : null}
              {emptyChronicle ? (
                <p className="mt-2 text-xs text-[var(--tfmc-stone)]">
                  No days have been captured for this map yet. The timelapse
                  starts once the first daily snapshot lands.
                </p>
              ) : null}
              {index && index.incomplete_day_count > 0 ? (
                <p className="mt-2 text-xs text-[var(--tfmc-accent)]">
                  {index.incomplete_day_count} stored day
                  {index.incomplete_day_count === 1 ? "" : "s"} were captured
                  with missing sources.
                </p>
              ) : null}
              {layerError ? (
                <p className="mt-2 text-xs text-[var(--tfmc-accent)]">
                  {layerError}
                </p>
              ) : null}
            </div>

            {!emptyChronicle && stage === "compose" ? (
              <ChronicleTogglePanel
                toggles={toggles}
                onToggle={toggleLayer}
                disabledReasons={disabledReasons}
                busy={layersLoading || indexLoading}
                blockReason={composeBlockReason}
                notice={notice}
                onNext={() => setStage("range")}
              />
            ) : null}

            {stage === "range" ? (
              <ChronicleRangePanel
                days={days}
                incompleteDays={incompleteSet}
                start={rangeStart}
                end={rangeEnd}
                onStartChange={setRangeStart}
                onEndChange={setRangeEnd}
                selection={selection}
                estimate={estimate}
                renderSize={renderSize}
                onRenderSizeChange={setRenderSize}
                blockReason={buildBlockReason}
                onBack={() => setStage("compose")}
                onBuild={() => void startBuild()}
              />
            ) : null}

            {stage === "build" ? (
              <ChronicleBuildPanel
                progress={buildProgress}
                error={buildError}
                onCancel={cancelBuild}
                onBack={() => {
                  cancelBuild();
                  setStage("range");
                }}
              />
            ) : null}

            {stage === "play" ? (
              <ChroniclePlaybackPanel
                days={frames.map((frame) => frame.day)}
                activeIndex={playIndex}
                onScrub={(next) => {
                  setPlaying(false);
                  setPlayIndex(next);
                }}
                playing={playing}
                onTogglePlay={() => setPlaying((current) => !current)}
                speed={speed}
                onSpeedChange={setSpeed}
                loop={loop}
                onLoopChange={setLoop}
                incomplete={Boolean(activeFrame?.incomplete)}
                exploreHref={
                  activeFrame ? chronicleDayHref(mapId, activeFrame.day) : null
                }
                skippedDays={skippedDays}
                onDiscard={() => {
                  discardFrames();
                  setStage("compose");
                  setNotice(null);
                }}
              />
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
}
