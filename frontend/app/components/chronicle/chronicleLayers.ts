import type {
  MapMarkersResponse,
  RegionRecord,
  WarExport,
} from "../map/types";
import { filterPlacedInstallations, installationToMapMarker } from "../../lib/installationMarkers";
import {
  filterPlacedSettlements,
  settlementToMapMarker,
  visibleSettlementKind,
} from "../../lib/settlementMarkers";
import { warBattleMarkersFromWars } from "../../lib/warBattleMarkers";
import type { MapMarker } from "../../lib/mapMarkers";
import type { ChronicleBorderMask } from "../../lib/map/chronicleBorderMask";
import type {
  LabelMapObject,
  NationLabelSpec,
  NationRegionInput,
} from "../../lib/mapLabels";

/**
 * Turning one stored day's raw payloads into the exact arrays the live map's
 * layer components already take. Pure, so the studio's compose preview and its
 * build pass go through the same code and cannot drift apart.
 */

export type ChronicleToggleKey =
  | "nationFill"
  | "nationBorders"
  | "nationNames"
  | "settlements"
  | "markerNames"
  | "forts"
  | "wars";

export type ChronicleToggles = Record<ChronicleToggleKey, boolean>;

/** The map opens bare: every layer off, parchment only. */
export const CHRONICLE_TOGGLES_OFF: ChronicleToggles = {
  nationFill: false,
  nationBorders: false,
  nationNames: false,
  settlements: false,
  markerNames: false,
  forts: false,
  wars: false,
};

export const CHRONICLE_TOGGLE_ORDER: {
  key: ChronicleToggleKey;
  label: string;
  detail: string;
}[] = [
  { key: "nationFill", label: "Nation fill", detail: "Painted territory" },
  {
    key: "nationBorders",
    label: "Nation borders",
    detail: "Outlines only, no fill",
  },
  { key: "nationNames", label: "Nation names", detail: "Realm labels" },
  {
    key: "settlements",
    label: "Settlements & installations",
    detail: "Towns, ports, airports",
  },
  {
    key: "markerNames",
    label: "Marker names",
    detail: "Name chips under pins",
  },
  { key: "forts", label: "Forts", detail: "Fort pins" },
  { key: "wars", label: "Wars", detail: "Campaign lines and battles" },
];

/** Every nation layer reads the same `nation` day file. */
export function needsNationFile(toggles: ChronicleToggles): boolean {
  return toggles.nationFill || toggles.nationBorders || toggles.nationNames;
}

/**
 * Settlements, forts and wars all come out of the one markers payload.
 *
 * `markerNames` is deliberately absent: it fetches nothing of its own and only
 * restyles pins the three layers above already produced.
 */
export function needsMarkers(toggles: ChronicleToggles): boolean {
  return toggles.settlements || toggles.forts || toggles.wars;
}

/**
 * Whether anything would actually be drawn. Gates the "Pick a date range"
 * button, so `markerNames` must not count — on its own it draws nothing, and
 * letting it through would offer to build a range of empty frames.
 */
export function anyChronicleToggleOn(toggles: ChronicleToggles): boolean {
  return CHRONICLE_TOGGLE_ORDER.some(
    ({ key }) => key !== "markerNames" && toggles[key]
  );
}

/**
 * Identifies a layer set for the build estimate. What a day costs depends
 * entirely on which layers are on — the label pass alone dwarfs the pixel pass —
 * so a timing measured under one set must never be quoted for another. Built
 * from a fixed order so the same set always produces the same string.
 */
export function chronicleToggleSignature(toggles: ChronicleToggles): string {
  const on = CHRONICLE_TOGGLE_ORDER.filter(({ key }) => toggles[key]).map(
    ({ key }) => key
  );
  return on.length ? on.join("+") : "none";
}

/**
 * Same filter the live map applies in `useMapModeData`: a nation with no colour
 * or no land has nothing to paint and no place to hang a label, and letting it
 * through only produces empty label components.
 */
export function chronicleRegionData(
  nationFile: RegionRecord | null
): Record<string, NationRegionInput> {
  // Null-prototype on purpose. Realm ids come from a parsed day file, and
  // `JSON.parse` makes `__proto__` a real own property, so a plain `{}` here
  // turns `out[id] = region` into a call to `Object.prototype.__proto__`'s
  // setter: that realm vanishes from the label layer while `buildNationColorLut`
  // still paints its provinces, and the object then answers truthily for keys it
  // does not have. With no prototype there is no setter and no inherited key.
  const out: Record<string, NationRegionInput> = Object.create(null);
  if (!nationFile) return out;
  for (const [id, region] of Object.entries(nationFile)) {
    if (typeof region?.rgb !== "string") continue;
    if (!Array.isArray(region.provinces) || region.provinces.length === 0) {
      continue;
    }
    out[id] = region;
  }
  return out;
}

/**
 * The label pass asks which realms are on screen through `mapObjects`, which on
 * the live map comes from the drill-down engine. The chronicle has no drill
 * down, so it stands in the engine's own starting answer: a realm is drawn
 * unless it has an overlord, whose suzerain's label already covers its land.
 */
export function chronicleLabelMapObjects(
  regionData: Record<string, NationRegionInput>,
  nationFile: RegionRecord | null
): LabelMapObject[] {
  // `nested`/`baseId` are stated rather than left to be inferred from the id.
  // These are all real region ids — the studio has no drill state and so no
  // synthetic `_nested` entries — and a realm legitimately named `Foo_nested`
  // would otherwise be read as one.
  return Object.keys(regionData).map((id) => ({
    id,
    visible: !nationFile?.[id]?.overlord,
    nested: false,
    baseId: id,
  }));
}

/**
 * Every array below comes off the wire. `?? []` only covers null and undefined,
 * so a day whose `settlements` is an object (or a string, or a number) used to
 * reach `.filter` inside a `useMemo` and take the whole page down mid-render.
 * A malformed source is a hole in one day, not a dead studio.
 */
function asArray<T>(value: T[] | undefined | null | unknown): T[] {
  return Array.isArray(value) ? (value as T[]) : [];
}

export function chronicleSettlementMarkers(
  markers: MapMarkersResponse | null,
  labelObjects: LabelMapObject[]
): MapMarker[] {
  if (!markers) return [];
  return [
    ...filterPlacedSettlements(asArray(markers.settlements)).map((settlement) =>
      settlementToMapMarker({
        ...settlement,
        kind: visibleSettlementKind(
          settlement.kind,
          settlement.faction_id,
          labelObjects
        ),
      })
    ),
    ...filterPlacedInstallations(asArray(markers.installations))
      .filter((installation) => installation.kind !== "fort")
      .map(installationToMapMarker),
  ];
}

export function chronicleFortMarkers(
  markers: MapMarkersResponse | null
): MapMarker[] {
  if (!markers) return [];
  return filterPlacedInstallations(asArray(markers.installations))
    .filter((installation) => installation.kind === "fort")
    .map(installationToMapMarker);
}

export function chronicleWars(
  markers: MapMarkersResponse | null
): WarExport[] {
  return asArray<WarExport>(markers?.wars);
}

export type ChronicleFrameLayers = {
  labels: NationLabelSpec[];
  /** Packed border bitmask for the day, or null when borders are off. */
  borders: ChronicleBorderMask | null;
  markers: MapMarker[];
  wars: WarExport[];
};

export const EMPTY_CHRONICLE_LAYERS: ChronicleFrameLayers = {
  labels: [],
  borders: null,
  markers: [],
  wars: [],
};

/**
 * Assembles one day's overlay arrays from whatever the enabled toggles pulled.
 * `labels` arrive pre-computed because the label pass needs session geometry
 * the caller owns; everything else is derived here.
 */
export function buildChronicleLayers(options: {
  toggles: ChronicleToggles;
  markers: MapMarkersResponse | null;
  labels: NationLabelSpec[];
  labelObjects: LabelMapObject[];
  /**
   * Pre-computed like `labels`, and for the same reason: the border pass needs
   * the province grid, which the caller owns for the whole session rather than
   * per day.
   */
  borders?: ChronicleBorderMask | null;
}): ChronicleFrameLayers {
  const { toggles, markers, labels, labelObjects, borders = null } = options;
  const pins: MapMarker[] = [];
  // Name chips are decided here rather than in `MapMarkerLayer` because the
  // per-kind default is baked into the markers themselves: installations, forts
  // and battles ship `showLabelOnlyOnHover: true`, and a built timelapse is
  // never hovered, so those pins would be permanently nameless. One stamp over
  // every pin makes the toggle mean the same thing for all of them.
  const nameChips = toggles.markerNames;

  if (toggles.settlements) {
    pins.push(...chronicleSettlementMarkers(markers, labelObjects));
  }
  if (toggles.forts) {
    pins.push(...chronicleFortMarkers(markers));
  }
  if (toggles.wars) {
    pins.push(...warBattleMarkersFromWars(chronicleWars(markers)));
  }

  return {
    labels: toggles.nationNames ? labels : [],
    borders: toggles.nationBorders ? borders : null,
    markers: pins.map((pin) => ({
      ...pin,
      showLabelOnlyOnHover: !nameChips,
    })),
    wars: toggles.wars ? chronicleWars(markers) : [],
  };
}
