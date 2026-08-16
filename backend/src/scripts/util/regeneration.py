import asyncio
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
from ..mapgen.parchmentgen import create_parchment_base
from ..mapgen.prosperitygen import create_prosperity_map
from ..mapgen.regiongen import generate_regions
from .mode_worker import run_mode
from .queue import load_queue, compile_queue
from .dirs import (
    validate_map,
    input_file,
    defines_file
)
from .task_lock import get_map_lock

MODES = ["nation", "duchy", "kingdom", "county", "empire", "trade"]


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


def should_parallelize_modes(regen_type: str) -> bool:
    return (
        regen_type.lower() == "fullregen"
        and parallel_mode_count() > 0
    )


def modes_to_run(map_name: str, regen_type: str, modes: list[str] | None = None) -> list[str]:
    runnable: list[str] = []
    for mode in modes or MODES:
        queue = load_queue(map_name, mode)
        if regen_type.lower() != "fullregen" and mode != "trade" and not queue:
            print(f"⚠️ Skipping {mode}: Empty queue")
            continue
        runnable.append(mode)
    return runnable


def _run_mode_serial(
    map_name: str,
    mode: str,
    regen_type: str,
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
            queued_regen=(regen_type.lower() != "fullregen" and mode != "trade"),
            cache=cache,
        )
    print(f"🎨 [{map_name}] Regions generated for {mode}")


def _run_modes_parallel(
    map_name: str,
    regen_type: str,
    modes: list[str],
    timings: _RegenTimings,
) -> None:
    worker_count = min(parallel_mode_count(), 4, len(modes))
    print(f"🚀 Parallel modes: {worker_count} workers")

    ctx = get_context("spawn")
    results: list[dict] = []
    with ProcessPoolExecutor(max_workers=worker_count, mp_context=ctx) as executor:
        futures = {
            executor.submit(run_mode, map_name, mode, regen_type): mode
            for mode in modes
        }
        for future in as_completed(futures):
            mode = futures[future]
            try:
                results.append(future.result())
            except Exception as exc:
                raise RuntimeError(f"Mode '{mode}' failed: {exc}") from exc

    merge_worker_timings(timings, results)


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
    print(f"🔁 Regeneration started for map '{map_name}'")

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
    if regen_type.lower() != "textonly":
        with timings.timed("map.parchment"):
            create_parchment_base(map_name)

        runnable_modes = modes_to_run(map_name, regen_type)

        if should_parallelize_modes(regen_type):
            _run_modes_parallel(map_name, regen_type, runnable_modes, timings)
        else:
            cache = None
            with timings.timed("geometry.cache"):
                cache = MapGeometryCache.load(map_name)

            for mode in runnable_modes:
                _run_mode_serial(map_name, mode, regen_type, cache, timings)

    elapsed = time.perf_counter() - start_time

    timings.print_summary(map_name, regen_type, elapsed)
    print(
        f"⏱️ Regeneration for map '{map_name}' "
        f"(type: {regen_type}) took {elapsed:.2f} seconds"
    )
    print(f"✅ Regeneration complete for map '{map_name}'")
    return timings, elapsed


# -------------------------
# Async entry point
# -------------------------
async def run_regeneration(map_name: str, regen_type: str):
    lock = get_map_lock(map_name)

    async with lock:
        # Run blocking work off the event loop
        await asyncio.to_thread(_sync_regeneration, map_name, regen_type)
