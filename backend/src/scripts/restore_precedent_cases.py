"""Restore precedent cases deleted through the API, from the audit trail.

Every delete writes a `precedent_audit` row holding a full snapshot of the case,
including its original id and created_at, so a deletion -- including a mass one
-- is reversible as long as the audit table is intact.

Cases whose id already exists are skipped, never overwritten, so this is safe to
re-run and safe to run while the corpus is partly intact.

    # See what could be restored, without touching anything
    cd backend && python -m src.scripts.restore_precedent_cases --dry-run

    # Restore everything deleted in the last day
    cd backend && python -m src.scripts.restore_precedent_cases --since "2026-08-29"

    # Restore one case
    cd backend && python -m src.scripts.restore_precedent_cases --case-id <uuid>
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_BACKEND_SRC = _BACKEND_ROOT / "src"
for _p in (str(_BACKEND_ROOT), str(_BACKEND_SRC)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from dotenv import load_dotenv

load_dotenv(_BACKEND_ROOT / ".env")

from src.precedent.db import AuditActor, list_deleted_cases, restore_case
from src.precedent.embeddings import EmbeddingError, embed_batch

BATCH = 100
RETRIES = 5
RETRY_SLEEP_SEC = 30.0


def _embed_with_retry(texts: list[str]) -> list[list[float]]:
    for attempt in range(RETRIES):
        try:
            return embed_batch(texts)
        except EmbeddingError as e:
            if attempt == RETRIES - 1:
                raise
            print(f"    embedding failed ({e}); retrying in {RETRY_SLEEP_SEC:.0f}s")
            time.sleep(RETRY_SLEEP_SEC)
    raise AssertionError("unreachable")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Report only; write nothing.")
    parser.add_argument("--since", help="Only deletions at or after this timestamp.")
    parser.add_argument("--case-id", help="Restore just this case id.")
    parser.add_argument(
        "--actor", default="restore-script", help="Name recorded in the audit trail."
    )
    args = parser.parse_args()

    rows = list_deleted_cases(since=args.since)
    if args.case_id:
        rows = [r for r in rows if str(r["case_id"]) == args.case_id]

    # A case can be deleted, restored and deleted again; keep only the most
    # recent deletion per id (list_deleted_cases returns newest first).
    seen: set[str] = set()
    unique = []
    for r in rows:
        cid = str(r["case_id"])
        if cid in seen:
            continue
        seen.add(cid)
        unique.append(r)

    if not unique:
        print("Nothing to restore.")
        return

    print(f"{len(unique)} deleted case(s) available to restore:")
    for r in unique:
        summary = (r["before"] or {}).get("summary", "")
        print(
            f"  {r['case_id']}  deleted {r['deleted_at']:%Y-%m-%d %H:%M} "
            f"by {r['actor']!r} ({r['source']})"
        )
        print(f"      {summary[:70]}")

    if args.dry_run:
        print("\nDry run: nothing written.")
        return

    restored = skipped = 0
    for start in range(0, len(unique), BATCH):
        chunk = unique[start : start + BATCH]
        vectors = _embed_with_retry(
            [(r["before"] or {}).get("summary", "") for r in chunk]
        )
        for r, vec in zip(chunk, vectors):
            ok = restore_case(
                str(r["case_id"]),
                snapshot=r["before"] or {},
                embedding=vec,
                actor=AuditActor(source="script", actor=args.actor),
            )
            if ok:
                restored += 1
            else:
                skipped += 1
                print(f"  skipped {r['case_id']} (a case with that id already exists)")
        print(f"  {restored + skipped}/{len(unique)}")

    print(f"\nrestored {restored}, skipped {skipped}")


if __name__ == "__main__":
    main()
