"""Headless 3D preview tiles for staff review sheets.

Fail-soft: missing Node/Chromium or a render error leaves the 2D sheet intact.
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from .storage import (
    BOOK_KIND,
    BOW_KINDS,
    CROSSBOW_KINDS,
    GUN_KIND,
    ITEM_KINDS,
    MODEL_3D_KINDS,
)

log = logging.getLogger("skins.preview_3d")

RENDER_DIR = Path(__file__).resolve().parents[2] / "render"
CLI = RENDER_DIR / "cli.mjs"
TIMEOUT_SEC = 90

PREVIEW_NAMES = {
    "model": "preview_model.png",
    "hat": "preview_hat.png",
    "carry": "preview_carry.png",
    "aim": "preview_aim.png",
    "reload": "preview_reload.png",
    "body": "preview_body.png",
    "book_unsigned": "preview_book_unsigned.png",
    "book_signed": "preview_book_signed.png",
}


def _node_bin() -> str | None:
    env = (os.environ.get("SHEET_RENDER_NODE") or "").strip()
    if env:
        return env
    return shutil.which("node")


def _mtime(path: Path) -> float:
    try:
        return path.stat().st_mtime
    except OSError:
        return 0.0


def _inputs_newer_than_outputs(inputs: list[Path], outputs: list[Path]) -> bool:
    if not outputs or any(not p.is_file() for p in outputs):
        return True
    newest_in = max((_mtime(p) for p in inputs if p.is_file()), default=0)
    oldest_out = min(_mtime(p) for p in outputs)
    return newest_in > oldest_out


def _job_for_kind(kind: str, slug: str, out_dir: Path, tiers: list[str]) -> dict | None:
    files: dict[str, str] = {}
    views: list[str] = []

    if kind == BOOK_KIND:
        unsigned = out_dir / f"{slug}_unsigned.png"
        signed = out_dir / f"{slug}_signed.png"
        if unsigned.is_file():
            files["unsigned"] = str(unsigned)
            views.append("book_unsigned")
        if signed.is_file():
            files["signed"] = str(signed)
            views.append("book_signed")
        if not views:
            return None
        return {"kind": kind, "views": views, "files": files}

    if kind == "armor_set":
        tier = (tiers[0] if tiers else "").strip() or "iron"
        layer1 = out_dir / f"{tier}_layer_1.png"
        layer2 = out_dir / f"{tier}_layer_2.png"
        if not layer1.is_file() and not layer2.is_file():
            return None
        if layer1.is_file():
            files["layer1"] = str(layer1)
        if layer2.is_file():
            files["layer2"] = str(layer2)
        helm_tex = out_dir / f"{tier}_helmet_texture.png"
        helm_model = out_dir / f"{tier}_helmet_model.json"
        if helm_tex.is_file() and helm_model.is_file():
            files["helmet_texture"] = str(helm_tex)
            files["helmet_model"] = str(helm_model)
        return {"kind": kind, "views": ["body"], "files": files}

    tex = out_dir / f"{slug}.png"
    if tex.is_file():
        files["texture"] = str(tex)

    if kind in ITEM_KINDS or kind in BOW_KINDS or kind in CROSSBOW_KINDS:
        if "texture" not in files:
            return None
        return {"kind": kind, "views": ["model"], "files": files}

    if kind in MODEL_3D_KINDS:
        model = out_dir / f"{slug}.json"
        if model.is_file():
            files["model"] = str(model)
        if "texture" not in files:
            return None
        views = ["model"]
        if kind == "helmet_3d":
            views.append("hat")
        return {"kind": kind, "views": views, "files": files}

    if kind == GUN_KIND:
        if "texture" not in files:
            return None
        views = ["model"]
        for stem in ("carry", "reload", "aim"):
            path = out_dir / f"{slug}_{stem}.json"
            if path.is_file():
                files[stem] = str(path)
                views.append(stem)
        return {"kind": kind, "views": views, "files": files}

    return None


def ensure_preview_tiles(
    kind: str,
    slug: str,
    out_dir: Path,
    tiers: list[str] | None = None,
) -> list[tuple[str, Path]]:
    """Render missing 3D tiles. Returns (label, path) for files that exist."""
    job = _job_for_kind(kind, slug, out_dir, tiers or [])
    if job is None:
        return []

    wanted = [
        (view, out_dir / PREVIEW_NAMES[view])
        for view in job["views"]
        if view in PREVIEW_NAMES
    ]
    outputs = [path for _, path in wanted]
    inputs = [Path(p) for p in job["files"].values()]
    if not _inputs_newer_than_outputs(inputs, outputs):
        return [(view, path) for view, path in wanted if path.is_file()]

    if os.environ.get("SHEET_RENDER_DISABLE", "").strip() in ("1", "true", "yes"):
        return [(view, path) for view, path in wanted if path.is_file()]

    node = _node_bin()
    if not node or not CLI.is_file():
        log.warning("3D sheet renderer unavailable (node or backend/render/cli.mjs)")
        return [(view, path) for view, path in wanted if path.is_file()]

    payload = {
        "kind": job["kind"],
        "views": job["views"],
        "files": job["files"],
        "outDir": str(out_dir),
    }
    try:
        with tempfile.NamedTemporaryFile(
            "w", suffix=".json", delete=False, encoding="utf-8"
        ) as tmp:
            json.dump(payload, tmp)
            tmp_path = tmp.name
        try:
            result = subprocess.run(
                [node, str(CLI), tmp_path],
                capture_output=True,
                text=True,
                timeout=TIMEOUT_SEC,
                cwd=str(RENDER_DIR),
            )
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
        if result.returncode != 0:
            err = (result.stderr or result.stdout or "").strip()
            log.warning("3D sheet renderer failed: %s", err[:500] or result.returncode)
    except (OSError, subprocess.TimeoutExpired) as e:
        log.warning("3D sheet renderer error: %s", e)

    return [(view, path) for view, path in wanted if path.is_file()]
