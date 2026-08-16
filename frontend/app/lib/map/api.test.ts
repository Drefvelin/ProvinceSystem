import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  MapAccessError,
  STAFF_MAP_ACCESS_DETAIL,
  STAFF_MAP_PERMISSION_DETAIL,
  fetchAccessibleMaps,
  fetchMapApi,
  fetchMapJson,
  fetchMapMarkers,
  staffMapAccessReason,
} from "@/lib/map/api";

describe("map api", () => {
  beforeEach(() => {
    vi.stubEnv("NEXT_PUBLIC_API_URL", "http://api.test");
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it("fetchMapApi attaches Bearer when session token provided", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ ok: true }), { status: 200 })
    );
    vi.stubGlobal("fetch", fetchMock);

    await fetchMapApi("/dev/data/nation", { sessionToken: "abc-token" });

    expect(fetchMock).toHaveBeenCalledWith(
      "http://api.test/dev/data/nation",
      expect.objectContaining({
        headers: { Authorization: "Bearer abc-token" },
      })
    );
  });

  it("fetchMapMarkers requests markers endpoint with session token", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({ map_id: "main", exported_at: null, settlements: [] }),
        { status: 200 }
      )
    );
    vi.stubGlobal("fetch", fetchMock);

    await fetchMapMarkers("main", "token-1");

    expect(fetchMock).toHaveBeenCalledWith(
      "http://api.test/main/data/markers",
      expect.objectContaining({
        headers: { Authorization: "Bearer token-1" },
      })
    );
  });

  it("fetchMapJson throws MapAccessError with detail on failure", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ detail: STAFF_MAP_PERMISSION_DETAIL }), {
          status: 403,
        })
      )
    );

    await expect(fetchMapJson("/dev/data/nation")).rejects.toMatchObject({
      name: "MapAccessError",
      status: 403,
      detail: STAFF_MAP_PERMISSION_DETAIL,
    } satisfies Partial<MapAccessError>);
  });

  it("fetchAccessibleMaps returns maps payload", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            maps: [{ id: "main", display_name: "Calavorn", public: true }],
          }),
          { status: 200 }
        )
      )
    );

    const data = await fetchAccessibleMaps();
    expect(data.maps).toHaveLength(1);
    expect(data.maps[0].id).toBe("main");
  });

  it("staffMapAccessReason maps backend detail strings", () => {
    expect(
      staffMapAccessReason(
        new MapAccessError(STAFF_MAP_ACCESS_DETAIL, 403, STAFF_MAP_ACCESS_DETAIL)
      )
    ).toBe("login");
    expect(
      staffMapAccessReason(
        new MapAccessError(
          STAFF_MAP_PERMISSION_DETAIL,
          403,
          STAFF_MAP_PERMISSION_DETAIL
        )
      )
    ).toBe("permission");
    expect(
      staffMapAccessReason(new MapAccessError("Other", 404, "Map not found"))
    ).toBe("unknown");
  });
});
