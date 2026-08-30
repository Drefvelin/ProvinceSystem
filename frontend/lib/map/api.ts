import type { MapId, MapMarkersResponse } from "@/app/components/map/types";

export const STAFF_MAP_ACCESS_DETAIL = "Staff map access required";
export const STAFF_MAP_PERMISSION_DETAIL = "Staff map permission required";

export const STAFF_MAP_PAGE_ROUTES: Partial<Record<MapId, string>> = {
  dev: "/map/r3b1rth",
};

export type AccessibleMapEntry = {
  id: string;
  display_name: string;
  public: boolean;
};

export type AccessibleMapsResponse = {
  maps: AccessibleMapEntry[];
};

export class MapAccessError extends Error {
  status: number;
  detail: string;

  constructor(message: string, status: number, detail: string) {
    super(message);
    this.name = "MapAccessError";
    this.status = status;
    this.detail = detail;
  }
}

export function getApiBase(): string {
  const base = (process.env.NEXT_PUBLIC_API_URL || "").trim().replace(/\/$/, "");
  if (!base) {
    throw new Error("NEXT_PUBLIC_API_URL is not set");
  }
  return base;
}

function detailMessage(data: unknown, fallback: string): string {
  if (data && typeof data === "object" && "detail" in data) {
    const detail = (data as { detail: unknown }).detail;
    if (typeof detail === "string") return detail;
  }
  return fallback;
}

function authHeaders(sessionToken?: string | null): HeadersInit | undefined {
  const token = (sessionToken || "").trim();
  if (!token) return undefined;
  return { Authorization: `Bearer ${token}` };
}

export type FetchMapApiOptions = {
  sessionToken?: string | null;
  method?: string;
  cache?: RequestCache;
  body?: string;
  headers?: HeadersInit;
};

export type EditorTier = "county" | "duchy" | "kingdom" | "empire";

export type EditorProvinceRow = {
  id: number;
  rgb: string;
  terrain?: string;
  fertility?: number;
};

export type EditorProvincesResponse = {
  provinces: EditorProvinceRow[];
};

export type EditorTitlesResponse = {
  ok: true;
  tier: string;
  count: number;
};

export type EditorRegenResponse = {
  ok: true;
  regen_type: string;
  message: string;
};

export type EditorTitleDraft = Record<
  string,
  {
    name: string;
    rgb: string;
    provinces?: number[];
    titles?: string[];
  }
>;

function mergeHeaders(
  sessionToken?: string | null,
  extra?: HeadersInit
): HeadersInit | undefined {
  const auth = authHeaders(sessionToken);
  if (!auth && !extra) return undefined;
  return { ...extra, ...auth };
}

export async function fetchMapApi(
  path: string,
  options: FetchMapApiOptions = {}
): Promise<Response> {
  const normalized = path.startsWith("/") ? path : `/${path}`;
  const headers = mergeHeaders(options.sessionToken, options.headers);
  try {
    return await fetch(`${getApiBase()}${normalized}`, {
      method: options.method ?? "GET",
      headers,
      body: options.body,
      // "no-cache" revalidates on every request but reuses the stored body on a
      // 304, so an unchanged 34 MB base map costs a header round-trip instead of
      // a full re-download. "no-store" would refetch the bytes every time.
      cache: options.cache ?? "no-cache",
    });
  } catch {
    throw new MapAccessError("Request failed. Please try again.", 0, "");
  }
}

export async function fetchMapJson<T>(
  path: string,
  options: FetchMapApiOptions = {}
): Promise<T> {
  const res = await fetchMapApi(path, options);
  if (res.ok) {
    return (await res.json()) as T;
  }

  let data: unknown = null;
  try {
    data = await res.json();
  } catch {
    data = null;
  }

  const detail = detailMessage(data, res.statusText || "Request failed");
  throw new MapAccessError(detail, res.status, detail);
}

export async function fetchMapBlobUrl(
  path: string,
  sessionToken: string
): Promise<string> {
  const res = await fetchMapApi(path, {
    sessionToken,
    // `fetch` defaults to `Accept: */*`, which the API reads as "cannot display
    // WebP" and answers with the full-size PNG. Public maps render through a
    // plain <img> and get this from the browser; authenticated maps come through
    // here, so they have to ask for it explicitly.
    headers: { Accept: "image/webp,image/png,*/*" },
  });
  if (!res.ok) {
    let data: unknown = null;
    try {
      data = await res.json();
    } catch {
      data = null;
    }
    const detail = detailMessage(data, res.statusText || "Request failed");
    throw new MapAccessError(detail, res.status, detail);
  }

  const blob = await res.blob();
  return URL.createObjectURL(blob);
}

export function revokeMapBlobUrl(url: string | null | undefined): void {
  if (url && url.startsWith("blob:")) {
    URL.revokeObjectURL(url);
  }
}

export function mapApiUrl(path: string): string {
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return `${getApiBase()}${normalized}`;
}

export function mapApiPathFromUrl(urlOrPath: string): string {
  if (urlOrPath.startsWith("/")) return urlOrPath;
  const base = getApiBase();
  if (urlOrPath.startsWith(`${base}/`)) {
    return urlOrPath.slice(base.length);
  }
  return urlOrPath;
}

export function mapRequiresAuth(mapId: MapId): boolean {
  return mapId !== "main";
}

export async function fetchAccessibleMaps(
  sessionToken?: string | null
): Promise<AccessibleMapsResponse> {
  return fetchMapJson<AccessibleMapsResponse>("/maps/accessible", {
    sessionToken,
  });
}

export async function fetchMapMarkers(
  mapId: MapId,
  sessionToken?: string | null
): Promise<MapMarkersResponse> {
  return fetchMapJson<MapMarkersResponse>(`/${mapId}/data/markers`, {
    sessionToken,
  });
}

export function staffMapAccessReason(
  error: MapAccessError
): "login" | "permission" | "unknown" {
  if (error.status !== 403) return "unknown";
  if (error.detail === STAFF_MAP_ACCESS_DETAIL) return "login";
  if (error.detail === STAFF_MAP_PERMISSION_DETAIL) return "permission";
  return "unknown";
}

export async function fetchEditorProvinces(
  mapId: MapId,
  sessionToken: string
): Promise<EditorProvincesResponse> {
  return fetchMapJson<EditorProvincesResponse>(`/${mapId}/editor/provinces`, {
    sessionToken,
  });
}

export function editorProvincePickPath(mapId: MapId): string {
  return `/${mapId}/editor/pick/provinces`;
}

export function editorProvinceIndexPath(mapId: MapId): string {
  return `/${mapId}/editor/province-index`;
}

export async function fetchEditorProvinceIndex(
  mapId: MapId,
  sessionToken: string
): Promise<ArrayBuffer> {
  const res = await fetchMapApi(editorProvinceIndexPath(mapId), {
    sessionToken,
  });
  if (!res.ok) {
    const data = await res.json().catch(() => null);
    const detail = detailMessage(data, res.statusText);
    throw new MapAccessError(
      `Editor province index failed: ${detail}`,
      res.status,
      detail
    );
  }
  return await res.arrayBuffer();
}

export async function postEditorTitles(
  mapId: MapId,
  tier: EditorTier,
  body: EditorTitleDraft,
  sessionToken: string
): Promise<EditorTitlesResponse> {
  return fetchMapJson<EditorTitlesResponse>(`/${mapId}/editor/titles/${tier}`, {
    method: "POST",
    sessionToken,
    body: JSON.stringify(body),
    headers: { "Content-Type": "application/json" },
  });
}

export async function postEditorRegen(
  mapId: MapId,
  regenType: string,
  sessionToken: string
): Promise<EditorRegenResponse> {
  return fetchMapJson<EditorRegenResponse>(
    `/${mapId}/editor/regen/${encodeURIComponent(regenType)}`,
    {
      method: "POST",
      sessionToken,
    }
  );
}
