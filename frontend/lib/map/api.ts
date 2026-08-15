import type { MapId } from "@/app/components/map/types";

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
};

export async function fetchMapApi(
  path: string,
  options: FetchMapApiOptions = {}
): Promise<Response> {
  const normalized = path.startsWith("/") ? path : `/${path}`;
  const headers = authHeaders(options.sessionToken);
  try {
    return await fetch(`${getApiBase()}${normalized}`, {
      method: options.method ?? "GET",
      headers,
      cache: options.cache,
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
  const res = await fetchMapApi(path, { sessionToken });
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

export function staffMapAccessReason(
  error: MapAccessError
): "login" | "permission" | "unknown" {
  if (error.status !== 403) return "unknown";
  if (error.detail === STAFF_MAP_ACCESS_DETAIL) return "login";
  if (error.detail === STAFF_MAP_PERMISSION_DETAIL) return "permission";
  return "unknown";
}
