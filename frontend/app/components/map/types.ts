export type MapId = "main" | "dev";

export type MapMode =
  | "nation"
  | "county"
  | "duchy"
  | "kingdom"
  | "empire"
  | "trade"
  | "prosperity"
  | "terrain"
  | "fertility"
  | "infestation";

export type OverlayBBox = { x: number; y: number; w: number; h: number };

export type RegionInfo = {
  title: string;
  tier: string;
  banner: string;
  size: number;
  subject_size: number;
  overlord: string;
  subjects: string[];
  description: string;
};

export type RegionRecord = Record<
  string,
  {
    name?: string;
    tier?: string;
    banner?: string;
    rgb?: string;
    overlord?: string;
    subjects?: string[];
    size?: number;
    subject_size?: number;
    provinces?: number[];
    occupied_held?: number[];
    overlay?: OverlayBBox;
    overlay_nested?: OverlayBBox;
  }
>;

export type MapObject = {
  id: string;
  visible: boolean;
  path: string;
  overlay?: OverlayBBox;
};

export type HoverOverlay = {
  url: string;
  overlay?: OverlayBBox;
};

export type CursorTooltip = {
  x: number;
  y: number;
  text: string;
  hint?: string;
};

export type SettlementMarkerKind =
  | "faction_capital"
  | "guild_capital"
  | "settlement";

export type SettlementMarkerSize = "small" | "large";

export type SettlementMarker = {
  id: string;
  name: string;
  faction_id?: string;
  province_id?: number;
  kind?: SettlementMarkerKind;
  marker_size?: SettlementMarkerSize;
  population?: number;
  map_x?: number;
  map_y?: number;
};

export type InstallationMarkerKind = "fort" | "port" | "airport";

export type InstallationMarker = {
  id: string;
  name: string;
  kind: InstallationMarkerKind;
  faction_id?: string;
  province_id?: number;
  map_x?: number;
  map_y?: number;
};

export type FortMarker = {
  id: string;
  name?: string;
  province_id?: number;
  faction_id?: string;
  map_x?: number;
  map_y?: number;
  overlay?: OverlayBBox;
  zoc_url?: string;
};

export type WarScheduleSlot = {
  schedule_index: number;
  leg: "invasion" | "counter";
  province_id: number;
  kind: string;
  kind_label: string;
  battle_type?: string;
  required?: boolean;
  status: "fought" | "next" | "upcoming";
  province_name?: string;
  map_x?: number;
  map_y?: number;
  fort_installation_id?: string | null;
  port_installation_id?: string | null;
  display_name?: string;
};

export type WarCapitalCoords = {
  province_id: number;
  center_x?: number;
  center_z?: number;
  map_x?: number;
  map_y?: number;
};

export type WarLinePoint = {
  province_id: number;
  map_x: number;
  map_y: number;
};

export type WarExport = {
  id: string;
  name?: string;
  war_type?: string;
  goal?: string;
  status?: string;
  attacker_leader_id?: string;
  defender_leader_id?: string;
  belligerents?: string[];
  campaign_provinces?: number[];
  cursor_index?: number;
  objective_province_id?: number;
  push_target?: string;
  campaign_schedule_index?: number;
  campaign_counter_schedule_index?: number;
  campaign_battle_schedule?: WarScheduleSlot[];
  campaign_counter_schedule?: WarScheduleSlot[];
  attacker_capital?: WarCapitalCoords;
  defender_capital?: WarCapitalCoords;
  campaign_line_points?: WarLinePoint[];
  occupied_by_attacker?: number[];
  occupied_by_defender?: number[];
};

export type MapMarkersResponse = {
  map_id: string;
  exported_at: string | null;
  settlement_large_population_threshold?: number;
  settlements: SettlementMarker[];
  installations: InstallationMarker[];
  forts: FortMarker[];
  wars?: WarExport[];
};

export const MAP_BOUNDS: Record<MapId, number> = {
  main: 6400,
  dev: 6400,
};

export const MAP_DISPLAY_NAMES: Record<MapId, string> = {
  main: "Adavaar",
  dev: "Adavaar",
};

export function apiBase(): string {
  return process.env.NEXT_PUBLIC_API_URL ?? "";
}

export function mapBaseImageUrl(mapId: MapId): string {
  return `${apiBase()}/${mapId}/map`;
}
