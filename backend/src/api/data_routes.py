from fastapi import APIRouter, Header, Request, Response
from fastapi.responses import FileResponse, JSONResponse
import json, os, time

from .map_access import ensure_map_access
from ..scripts.util.dirs import input_file, defines_file, validate_map
from ..scripts.loader.markers import build_markers_response
from ..scripts.loader.province_metadata import load_province_metadata

data_router = APIRouter()

CACHE_TTL = 300
_province_cache = {}

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
    out = {}

    for pid, m in meta.items():
        p = by_id.get(pid, {})
        trade = p.get("trade") or {}
        shares, dom, ratio = compute_trade_shares(trade)

        out[pid] = {
            **m,
            "province_id": pid,
            "prosperity": p.get("prosperity", 0),
            "trade": trade,
            "trade_total": sum(v.get("trade", 0) for v in trade.values()),
            "trade_shares": shares,
            "dominant_guild": dom,
            "dominance_ratio": ratio,
        }

    return out

@data_router.get("/{map_name}/compiled_data/provinces")
async def get_compiled_provinces(
    map_name: str,
    authorization: str | None = Header(default=None),
):
    ensure_map_access(map_name, authorization)
    now = time.time()
    cached = _province_cache.get(map_name)

    if cached and now - cached["ts"] < CACHE_TTL:
        return JSONResponse(cached["data"])

    data = build_compiled_provinces(map_name)
    _province_cache[map_name] = {"ts": now, "data": data}
    return JSONResponse(data)

@data_router.get("/{map_name}/data/province_label_grid_bin")
async def get_province_label_grid_bin(
    map_name: str,
    authorization: str | None = Header(default=None),
):
    ensure_map_access(map_name, authorization)
    path = defines_file(map_name, "province_label_grid.bin.gz")
    if not os.path.exists(path):
        return JSONResponse({"error": "Data not found"}, 404)
    return FileResponse(
        path,
        media_type="application/gzip",
        filename="province_label_grid.bin.gz",
    )

@data_router.get("/{map_name}/data/markers")
async def get_map_markers(
    map_name: str,
    authorization: str | None = Header(default=None),
):
    ensure_map_access(map_name, authorization)
    return JSONResponse(build_markers_response(map_name))

@data_router.get("/{map_name}/data/{file}")
async def get_map_name_data(
    map_name: str,
    file: str,
    authorization: str | None = Header(default=None),
):
    ensure_map_access(map_name, authorization)
    path = defines_file(map_name, f"{file}.json")
    if not os.path.exists(path):
        return JSONResponse({"error": "Data not found"}, 404)
    with open(path, encoding="utf-8") as f:
        return JSONResponse(json.load(f))

@data_router.post("/{map_name}/data/upload/{mode}")
async def upload_region_data(map_name: str, mode: str, request: Request):
    validate_map(map_name)
    payload = await request.json()

    path = (
        input_file(map_name, f"{mode}.json")
        if mode in {"nation", "guilds", "province_data", "queue", "map_markers"}
        else defines_file(map_name, f"{mode}.json")
    )

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    _province_cache.pop(map_name, None)
    return JSONResponse({"message": f"{mode} data saved for '{map_name}'"})
