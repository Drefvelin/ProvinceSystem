import asyncio
import hashlib
import os
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import get_context

from ..compile.nation_compiler import process_nations
from ..compile.trade_compiler import process_trade
from ..mapgen.geometry_cache import MapGeometryCache
from ..mapgen.mapgen import create_map
from ..mapgen.parchmentgen import (
    create_map_preview,
    create_parchment_base,
    map_preview_path,
)
from ..mapgen.infestationgen import create_infestation_map
from ..mapgen.prosperitygen import create_prosperity_map
from ..mapgen.regiongen import generate_regions
from ..mapgen.zocgen import generate_zoc_overlays
from ..map_tools.province_geometry import write_province_geometry
from ..province_id_grid import (
    GRID_FILENAME,
    RUNS_FILENAME,
    build_province_id_map,
    write_province_id_grid_file,
    write_province_id_runs_file,
)
from ..tools.warm_map_webp import (
    cache_path_for,
    warm as warm_map_webp,
    webp_warm_sources,
)
from .mode_worker import run_mode
from .queue import load_queue, compile_queue
from .regen_types import MODES, RegenSpec, parse_regen_type, region_regen_queued
from .dirs import (
    validate_map,
    input_file,
    defines_file
)
from .task_lock import get_map_lock

# Derived artifacts rebuilt only when their sources changed. The stamp records
# the sha256 of every source that fed the last successful build, so a git
# checkout or container rebuild (which moves mtimes but not content) does not
# trigger a needless multi-minute province scan.
DERIVED_STAMP_FILENAME = "derived_sources.json"


class _RegenTimings:
    def __init__(self) -> None:
        self._rows: list[tuple[str, float]] = []

    def record(self, label: str, seconds: float) -> None:
        self._rows.append((label, seconds))

    def timed(self, label: str):
        timings = self

        class _Timer:
            def __enter__(self):
                self._start = time.perf_counter()
                return self

            def __exit__(self, exc_type, exc, tb):
                timings.record(label, time.perf_counter() - self._start)

        return _Timer()

    def sorted_rows(self) -> list[tuple[str, float]]:
        return sorted(self._rows, key=lambda row: row[1], reverse=True)

    def to_dict(self, map_name: str, regen_type: str, total_s: float) -> dict:
        steps = []
        for label, seconds in self.sorted_rows():
            ms = seconds * 1000
            pct = (seconds / total_s * 100) if total_s > 0 else 0.0
            steps.append({
                "label": label,
                "ms": round(ms),
                "pct": round(pct, 1),
            })
        return {
            "map": map_name,
            "regen_type": regen_type,
            "total_ms": round(total_s * 1000),
            "steps": steps,
        }

    def print_summary(self, map_name: str, regen_type: str, total_s: float) -> None:
        print(f"\n⏱️ Regeneration timing summary ({map_name}, {regen_type})")
        if not self._rows:
            print("  (no steps recorded)")
            return

        sorted_rows = self.sorted_rows()
        label_width = max(len(label) for label, _ in sorted_rows)
        for label, seconds in sorted_rows:
            ms = seconds * 1000
            pct = (seconds / total_s * 100) if total_s > 0 else 0.0
            print(f"  {label:<{label_width}}  {ms:>9.0f} ms  {pct:>5.1f}%")
        print(f"  {'TOTAL':<{label_width}}  {total_s * 1000:>9.0f} ms  100.0%")


def merge_worker_timings(timings: _RegenTimings, results: list[dict]) -> None:
    """Merge per-worker step timings into the parent summary."""
    for result in results:
        for label, seconds in result.get("steps", {}).items():
            timings.record(label, seconds)


def parallel_mode_count() -> int:
    """Worker count from REGEN_PARALLEL_MODES; 0 disables parallelism."""
    if os.environ.get("REGEN_SERIAL_MODES"):
        return 0
    raw = os.environ.get("REGEN_PARALLEL_MODES", "0")
    try:
        count = int(raw)
    except ValueError:
        return 0
    return max(0, count)


def should_parallelize_modes(spec: RegenSpec) -> bool:
    return (
        spec.full_regions
        and spec.modes is None
        and parallel_mode_count() > 0
    )


def modes_to_run(map_name: str, spec: RegenSpec) -> list[str]:
    runnable: list[str] = []
    mode_list = spec.modes if spec.modes is not None else MODES
    for mode in mode_list:
        if mode not in MODES:
            raise ValueError(f"Unknown map mode '{mode}'")
        queue = load_queue(map_name, mode)
        if not spec.full_regions and mode != "trade" and not queue:
            print(f"⚠️ Skipping {mode}: Empty queue")
            continue
        runnable.append(mode)
    return runnable


def _run_mode_serial(
    map_name: str,
    mode: str,
    spec: RegenSpec,
    cache: MapGeometryCache,
    timings: _RegenTimings,
) -> None:
    print(f"🛠️ [{map_name}] Processing mode: {mode}")

    if mode == "trade":
        with timings.timed(f"{mode}.prosperity"):
            create_prosperity_map(map_name, "prosperity_map", cache=cache)

    with timings.timed(f"{mode}.map"):
        create_map(map_name, mode, f"{mode}_map", False, cache=cache)
    print(f"🗺️ [{map_name}] Map generated for {mode}")

    with timings.timed(f"{mode}.regions"):
        generate_regions(
            map_name,
            mode,
            borders=mode != "trade",
            queued_regen=region_regen_queued(spec, mode),
            cache=cache,
        )
    print(f"🎨 [{map_name}] Regions generated for {mode}")


def _run_modes_parallel(
    map_name: str,
    spec: RegenSpec,
    modes: list[str],
    timings: _RegenTimings,
) -> None:
    worker_count = min(parallel_mode_count(), 4, len(modes))
    print(f"🚀 Parallel modes: {worker_count} workers")

    ctx = get_context("spawn")
    results: list[dict] = []
    with ProcessPoolExecutor(max_workers=worker_count, mp_context=ctx) as executor:
        futures = {
            executor.submit(run_mode, map_name, mode, spec.full_regions): mode
            for mode in modes
        }
        for future in as_completed(futures):
            mode = futures[future]
            try:
                results.append(future.result())
            except Exception as exc:
                raise RuntimeError(f"Mode '{mode}' failed: {exc}") from exc

    merge_worker_timings(timings, results)


# -------------------------
# Derived-artifact staleness
# -------------------------
def _file_digest(path: str) -> str | None:
    """sha256 of a file, or None when it does not exist."""
    try:
        digest = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
    except OSError:
        return None


def _source_fingerprint(sources: list[str]) -> dict[str, str] | None:
    """Map source path -> sha256. None when any source is missing."""
    fingerprint: dict[str, str] = {}
    for path in sources:
        digest = _file_digest(path)
        if digest is None:
            return None
        fingerprint[os.path.basename(path)] = digest
    return fingerprint


def _stamp_file(map_name: str) -> str:
    return defines_file(map_name, DERIVED_STAMP_FILENAME)


def _load_stamps(map_name: str) -> dict:
    try:
        with open(_stamp_file(map_name), "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def _save_stamp(map_name: str, key: str, fingerprint: dict[str, str]) -> None:
    stamps = _load_stamps(map_name)
    stamps[key] = fingerprint
    path = _stamp_file(map_name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(stamps, f, indent=2, sort_keys=True)
        f.write("\n")


def derived_is_current(
    map_name: str,
    key: str,
    fingerprint: dict[str, str],
    outputs: list[str],
) -> bool:
    """True when every output exists and was built from exactly these sources."""
    if any(not os.path.exists(path) for path in outputs):
        return False
    return _load_stamps(map_name).get(key) == fingerprint


def _rebuild_derived(
    map_name: str,
    key: str,
    label: str,
    sources: list[str],
    outputs: list[str],
    build,
    timings: _RegenTimings,
) -> None:
    """Run `build` only when `sources` changed since the last successful build.

    Never fatal: these artifacts are consumed by the editor and the plugin, not
    by the map render, so a failure here must not sink an otherwise good regen.
    """
    fingerprint = _source_fingerprint(sources)
    if fingerprint is None:
        missing = [os.path.basename(p) for p in sources if not os.path.exists(p)]
        print(f"⏭️ Skipping {label}: missing {', '.join(missing)}")
        return

    if derived_is_current(map_name, key, fingerprint, outputs):
        print(f"⏭️ {label} up to date (sources unchanged)")
        return

    print(f"🔧 Rebuilding {label} (sources changed)")
    try:
        with timings.timed(f"derived.{key}"):
            build()
    except Exception as exc:
        print(f"⚠️ {label} failed: {exc}")
        return

    _save_stamp(map_name, key, fingerprint)


def _province_sources(map_name: str) -> list[str]:
    return [
        input_file(map_name, "provinces.png"),
        defines_file(map_name, "provinces.txt"),
    ]


def _geometry_outputs(map_name: str) -> list[str]:
    return [
        defines_file(map_name, name)
        for name in (
            "province_neighbors.json",
            "province_label_neighbors.json",
            "province_centroids.json",
            "province_label_grid.bin.gz",
            "province_label_grid.json",
        )
    ]


def run_derived_artifacts(map_name: str, timings: _RegenTimings) -> None:
    """Rebuild province/preview derivatives whose sources changed."""
    province_sources = _province_sources(map_name)

    # The runs artifact is a re-encoding of the grid, so both are produced by one
    # entry under one stamp. Split across two entries they could rebuild
    # independently and leave the editor decoding runs that disagree with the
    # grid — a mismatch nothing downstream can detect.
    def _build_province_id_artifacts() -> None:
        # Both artifacts encode the same array, so decode provinces.png once.
        source = build_province_id_map(map_name)
        write_province_id_grid_file(map_name, source=source)
        write_province_id_runs_file(map_name, source=source)

    _rebuild_derived(
        map_name,
        "province_id_grid",
        "province id grid + runs",
        province_sources,
        [
            defines_file(map_name, GRID_FILENAME),
            defines_file(map_name, RUNS_FILENAME),
        ],
        _build_province_id_artifacts,
        timings,
    )

    if os.environ.get("REGEN_SKIP_PROVINCE_GEOMETRY"):
        print("⏭️ Skipping province geometry (REGEN_SKIP_PROVINCE_GEOMETRY)")
    else:
        _rebuild_derived(
            map_name,
            "province_geometry",
            "province geometry",
            province_sources,
            _geometry_outputs(map_name),
            lambda: write_province_geometry(map_name),
            timings,
        )

    _rebuild_derived(
        map_name,
        "map_preview",
        "map preview",
        [input_file(map_name, "map.png")],
        [map_preview_path(map_name)],
        lambda: create_map_preview(map_name),
        timings,
    )


def warm_webp_cache(map_name: str, timings: _RegenTimings) -> None:
    """Pre-encode the WebP copies so the first visitor after a regen is not
    served the full-size PNG while the background encode runs.

    Gated on the same content stamp as the other derived artifacts rather than
    on webp_cache's own mtime check. create_parchment_base rewrites
    parchment_base.png every regen, so mtime freshness is always false and this
    would otherwise spend ~26s per image re-encoding byte-identical input,
    synchronously, while holding the map lock.
    """
    sources = webp_warm_sources(map_name)
    if not sources:
        return

    _rebuild_derived(
        map_name,
        "webp_cache",
        "WebP cache",
        sources,
        [str(cache_path_for(source)) for source in sources],
        lambda: warm_map_webp([map_name]),
        timings,
    )


def print_queues(map_name: str):
    raw_path = input_file(map_name, "queue.json")
    compiled_path = defines_file(map_name, "queue.json")

    print(f"📥 RAW QUEUE ({raw_path}):")
    if os.path.exists(raw_path):
        with open(raw_path, "r", encoding="utf-8") as f:
            print(json.dumps(json.load(f), indent=2))
    else:
        print("❌ No raw queue file found.")

    print(f"\n📦 COMPILED QUEUE ({compiled_path}):")
    if os.path.exists(compiled_path):
        with open(compiled_path, "r", encoding="utf-8") as f:
            print(json.dumps(json.load(f), indent=2))
    else:
        print("❌ No compiled queue file found.")


# -------------------------
# Sync regeneration logic
# -------------------------
def _sync_regeneration(map_name: str, regen_type: str):
    # Windows consoles often default to cp1252; regen logs use UTF-8 symbols.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    start_time = time.perf_counter()
    timings = _RegenTimings()

    validate_map(map_name)
    spec = parse_regen_type(regen_type)
    print(f"🔁 Regeneration started for map '{map_name}' ({spec.label})")

    # 1. Compile nation data
    with timings.timed("compile.nation"):
        process_nations(map_name)
    if os.path.exists(input_file(map_name, "guilds.json")):
        with timings.timed("compile.trade"):
            process_trade(map_name)

    # 2. Compile queue
    with timings.timed("compile.queue"):
        compile_queue(map_name)
    print("✅ Queue compiled")
    print_queues(map_name)

    # 3. Generate maps + regions
    if not spec.is_textonly:
        with timings.timed("map.parchment"):
            create_parchment_base(map_name)

        runnable_modes = modes_to_run(map_name, spec)

        if should_parallelize_modes(spec):
            _run_modes_parallel(map_name, spec, runnable_modes, timings)
            with timings.timed("geometry.cache"):
                cache = MapGeometryCache.load(map_name)
        else:
            cache = None
            with timings.timed("geometry.cache"):
                cache = MapGeometryCache.load(map_name)

            for mode in runnable_modes:
                _run_mode_serial(map_name, mode, spec, cache, timings)

        with timings.timed("zocgen"):
            generate_zoc_overlays(map_name, cache=cache)

        with timings.timed("map.infestation"):
            create_infestation_map(map_name, "infestation_map", cache=cache)

    run_derived_artifacts(map_name, timings)

    elapsed = time.perf_counter() - start_time

    timings.print_summary(map_name, regen_type, elapsed)
    print(
        f"⏱️ Regeneration for map '{map_name}' "
        f"(type: {regen_type}) took {elapsed:.2f} seconds"
    )
    print(f"✅ Regeneration complete for map '{map_name}'")

    # After the summary so it never hides the real regen cost, but still inside
    # the map lock so a request cannot race a half-written cache entry.
    warm_webp_cache(map_name, timings)
    return timings, elapsed


# -------------------------
# Async entry point
# -------------------------
async def run_regeneration(map_name: str, regen_type: str):
    lock = get_map_lock(map_name)

    async with lock:
        # Run blocking work off the event loop
        await asyncio.to_thread(_sync_regeneration, map_name, regen_type)
