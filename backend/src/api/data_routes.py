from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Request, Response
from fastapi.responses import JSONResponse
import json, os, time

from .http_headers import (
    add_no_cache,
    conditional_file_response,
    conditional_json_response,
    make_etag,
)
from .internal_access import require_localhost
from .map_access import ensure_map_access
from .editor_validation import TITLE_TIERS, TitleValidationError, validate_title_tier
from ..scripts.util.dirs import input_file, defines_file, validate_map
from ..scripts.loader.markers import build_markers_response
from ..scripts.mapgen.infestationgen import create_infestation_map, load_infestation_by_id
from ..scripts.loader.province_metadata import load_province_metadata
from ..scripts.mapgen.zocgen import generate_zoc_overlays

data_router = APIRouter()

CACHE_TTL = 300
_province_cache = {}

def clear_province_cache(map_name: str) -> None:
    _province_cache.pop(map_name, None)

def add_cors(response: Response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    return response;

def compute_trade_shares(trade: dict):
    total = sum(v.get("trade", 0) for v in trade.values())
    if total <= 0:
        return {}, None, 0.0

    shares, dominant, best = {}, None, 0.0
    for g, d in trade.items():
        v = d.get("trade", 0)
        r = v / total
        shares[g] = r
        if v > best:
            best, dominant = v, g
    return shares, dominant, best / total

def build_compiled_provinces(map_name: str):
    meta = load_province_metadata(map_name)

    with open(input_file(map_name, "province_data.json"), encoding="utf-8") as f:
        pdata = json.load(f)

    by_id = {p["id"]: p for p in pdata}
    infest = load_infestation_by_id(map_name)
    out = {}

    for pid, m in meta.items():
        p = by_id.get(pid, {})
        if not p:
            try:
                p = by_id.get(int(pid), {})
            except (TypeError, ValueError):
                p = {}
        trade = p.get("trade") or {}
        shares, dom, ratio = compute_trade_shares(trade)
        inf = infest.get(pid)
        if inf is None:
            try:
                inf = infest.get(int(pid))
            except (TypeError, ValueError):
                inf = None

        out[pid] = {
            **m,
            "province_id": pid,
            "prosperity": p.get("prosperity", 0),
            "trade": trade,
            "trade_total": sum(v.get("trade", 0) for v in trade.values()),
            "trade_shares": shares,
            "dominant_guild": dom,
            "dominance_ratio": ratio,
            "infestation_severity": inf.get("severity") if inf else None,
            "infestation_group": inf.get("group") if inf else None,
            "infestation_display": (inf.get("display") or inf.get("group")) if inf else None,
        }

    return out

@data_router.get("/{map_name}/compiled_data/provinces")
async def get_compiled_provinces(
    map_name: str,
    authorization: str | None = Header(default=None),
    if_none_match: str | None = Header(default=None),
):
    ensure_map_access(map_name, authorization)
    now = time.time()
    cached = _province_cache.get(map_name)

    if not cached or now - cached["ts"] >= CACHE_TTL:
        data = build_compiled_provinces(map_name)
        # Serialize once per rebuild and keep the bytes: the ETag is a hash of
        # the body, so a TTL rollover that produces identical data keeps the
        # same tag and the client revalidates into a 304 instead of
        # re-downloading ~185KB it already has.
        cached = {
            "ts": now,
            "data": data,
            "body": json.dumps(data, sort_keys=True, ensure_ascii=False),
        }
        _province_cache[map_name] = cached

    return conditional_json_response(
        body=cached["body"],
        if_none_match=if_none_match,
    )

@data_router.get("/{map_name}/data/province_label_grid_bin")
async def get_province_label_grid_bin(
    map_name: str,
    authorization: str | None = Header(default=None),
    if_none_match: str | None = Header(default=None),
    if_modified_since: str | None = Header(default=None),
):
    ensure_map_access(map_name, authorization)
    path = defines_file(map_name, "province_label_grid.bin.gz")
    if not os.path.exists(path):
        return add_no_cache(JSONResponse({"error": "Data not found"}, 404))
    return conditional_file_response(
        path,
        media_type="application/gzip",
        if_none_match=if_none_match,
        if_modified_since=if_modified_since,
    )

@data_router.get("/{map_name}/data/markers")
async def get_map_markers(
    map_name: str,
    authorization: str | None = Header(default=None),
    if_none_match: str | None = Header(default=None),
):
    ensure_map_access(map_name, authorization)
    # Markers are assembled from several files (map_markers.json, centroids, zoc
    # overlays), so there is no single file to stat and no cache entry to key
    # on. Hash the built payload instead: still cheap next to the JSON encode,
    # and the tag changes the instant any input does, so a marker upload is
    # picked up as immediately as it was under no-store.
    payload = build_markers_response(map_name)
    return conditional_json_response(
        body=json.dumps(payload, sort_keys=True, ensure_ascii=False),
        if_none_match=if_none_match,
    )

@data_router.get("/{map_name}/data/{file}")
async def get_map_name_data(
    map_name: str,
    file: str,
    authorization: str | None = Header(default=None),
    if_none_match: str | None = Header(default=None),
    if_modified_since: str | None = Header(default=None),
):
    ensure_map_access(map_name, authorization)
    path = defines_file(map_name, f"{file}.json")
    if not os.path.exists(path):
        return add_no_cache(JSONResponse({"error": "Data not found"}, 404))
    # The response body was always the file verbatim; parsing and re-encoding it
    # only cost CPU. Streaming the file lets the shared ETag/Last-Modified
    # helper turn an unchanged geometry blob into a 304.
    return conditional_file_response(
        path,
        media_type="application/json",
        if_none_match=if_none_match,
        if_modified_since=if_modified_since,
    )

@data_router.post("/{map_name}/data/upload/{mode}")
async def upload_region_data(
    map_name: str,
    mode: str,
    request: Request,
    background_tasks: BackgroundTasks,
):
    require_localhost(request)
    validate_map(map_name)
    payload = await request.json()

    mode_norm = (mode or "").strip().lower()
    if mode_norm in TITLE_TIERS:
        if not isinstance(payload, dict):
            raise HTTPException(status_code=400, detail="Title data must be a JSON object")
        if not payload:
            return JSONResponse({"message": f"{mode} upload skipped (empty) for '{map_name}'"})
        try:
            payload = validate_title_tier(mode_norm, payload, map_name)
        except TitleValidationError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    path = (
        input_file(map_name, f"{mode}.json")
        if mode in {"nation", "guilds", "province_data", "queue", "map_markers", "infestation_data"}
        else defines_file(map_name, f"{mode}.json")
    )

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    _province_cache.pop(map_name, None)

    if mode_norm == "map_markers":
        background_tasks.add_task(generate_zoc_overlays, map_name)
    if mode_norm == "infestation_data":
        background_tasks.add_task(create_infestation_map, map_name)

    return JSONResponse({"message": f"{mode} data saved for '{map_name}'"})
