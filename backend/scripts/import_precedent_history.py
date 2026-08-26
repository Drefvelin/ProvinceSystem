"""One-off import: seed precedent_cases from a legacy ban-log config.yml.

Usage:
    python scripts/import_precedent_history.py "C:/path/to/config.yml" [--dry-run]

Reads the LiteBans-style `player: [{head, bans}, {violations: {...}}]` structure,
extracts a rule number from each violation's `reason` text when present, and
inserts each usable violation directly into Supabase via src.precedent.db —
skipping entries where the yaml fields are clearly swapped/corrupted (e.g.
`length` holding a name). Embeddings are requested from Voyage in one batched
call (not one request per row) to stay well under free-tier rate limits.

Run from backend/ so `src` is importable and `.env` loads via python-dotenv.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

_RULE_RE = re.compile(r"\((\d+\.\d+)\)")
_KNOWN_LENGTH_RE = re.compile(r"^(\d+[a-zA-Z]+|perma.*|permanent.*)$", re.IGNORECASE)
_BATCH_SIZE = 64


def _extract_rule(reason: str) -> str:
    m = _RULE_RE.search(reason)
    return m.group(1) if m else ""


def _ruling_for_status(status: str) -> str:
    status = (status or "").strip().lower()
    if status == "pardoned":
        return "Pardoned after review"
    if status == "helper":
        return "Decided by helper-tier staff"
    if status in ("active", "permanent"):
        return "Upheld"
    return status or "Unknown"


def _looks_valid(entry: dict) -> bool:
    """Reject entries where fields are obviously swapped (garbled source data)."""
    reason = str(entry.get("reason") or "").strip()
    length = str(entry.get("length") or "").strip()
    banned_by = str(entry.get("bannedBy") or "").strip()
    if not reason or reason == ".":
        return False
    if not banned_by or not length:
        return False
    if not _KNOWN_LENGTH_RE.match(length):
        return False
    if _KNOWN_LENGTH_RE.match(banned_by):
        return False
    return True


def iter_violations(data: dict):
    players = (data or {}).get("player") or {}
    for username, entries in players.items():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            violations = entry.get("violations")
            if not isinstance(violations, dict):
                continue
            for _, v in violations.items():
                if not isinstance(v, list):
                    continue
                flat = {}
                for item in v:
                    if isinstance(item, str) and "=" in item:
                        k, _, val = item.partition("=")
                        flat[k.strip()] = val.strip()
                if flat:
                    yield username, flat


def _case_text(body: dict) -> str:
    return (
        f"Summary: {body['summary']}\n"
        f"Rule: {body['rule']}\n"
        f"Ruling: {body['ruling']}\n"
        f"Punishment: {body['punishment']}"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("config_path")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    from src.precedent.db import insert_case, migrate
    from src.precedent.embeddings import embed_batch

    raw = Path(args.config_path).read_text(encoding="utf-8")
    data = yaml.safe_load(raw)

    bodies: list[dict] = []
    skipped = 0
    for username, flat in iter_violations(data):
        if not _looks_valid(flat):
            skipped += 1
            print(f"SKIP  {username}: corrupted entry {flat}", file=sys.stderr)
            continue
        reason = flat["reason"]
        bodies.append(
            {
                "logged_by": flat["bannedBy"],
                "players": [username],
                "summary": reason,
                "rule": _extract_rule(reason),
                "ruling": _ruling_for_status(flat.get("status", "")),
                "punishment": flat["length"],
            }
        )

    print(f"Parsed {len(bodies)} usable violations, {skipped} skipped.\n")

    if args.dry_run:
        for b in bodies:
            print(f"DRY   {b['players'][0]}: {b}")
        print(f"\nDone. imported=0 (dry-run) parsed={len(bodies)} skipped={skipped}")
        return 0

    migrate()
    ok = 0
    for start in range(0, len(bodies), _BATCH_SIZE):
        chunk = bodies[start : start + _BATCH_SIZE]
        texts = [_case_text(b) for b in chunk]
        vectors = embed_batch(texts, input_type="document")
        for body, vector in zip(chunk, vectors):
            insert_case(
                logged_by=body["logged_by"],
                players=body["players"],
                summary=body["summary"],
                rule=body["rule"],
                ruling=body["ruling"],
                punishment=body["punishment"],
                embedding=vector,
            )
            ok += 1
            print(f"OK    {body['players'][0]}: {body['summary'][:60]}")

    print(f"\nDone. imported={ok} skipped={skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
