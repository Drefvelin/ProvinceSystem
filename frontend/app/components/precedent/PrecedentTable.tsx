"use client";

import type { PrecedentCase } from "@/lib/precedent/api";
import {
  formatCreatedAt,
  punishmentTone,
  rulingTone,
  visibleRuling,
} from "@/lib/precedent/filter";
import {
  dateClass,
  idClass,
  loggedByClass,
  playerChipClass,
  rulePillClass,
  toneClass,
} from "./caseFieldStyles";

type Props = {
  cases: PrecedentCase[];
  /** Total in the DB, for the "showing N of M" line. */
  total: number;
  loading: boolean;
  onEdit: (row: PrecedentCase) => void;
  onDelete: (row: PrecedentCase) => void;
};

const actionClass =
  "text-xs text-[var(--tfmc-stone)] underline-offset-2 hover:text-[var(--tfmc-cream)] hover:underline";

export default function PrecedentTable({
  cases,
  total,
  loading,
  onEdit,
  onDelete,
}: Props) {
  if (loading) {
    return <p className="text-sm text-[var(--tfmc-mist)]">Loading cases…</p>;
  }

  if (cases.length === 0) {
    return (
      <p className="text-sm text-[var(--tfmc-mist)]">
        {total === 0
          ? "No cases logged yet."
          : "No cases match that filter."}
      </p>
    );
  }

  return (
    <div>
      <p className="text-xs text-[var(--tfmc-stone)]">
        Showing {cases.length} of {total}
      </p>
      <ul className="mt-3 space-y-2">
        {cases.map((row) => (
          <li
            key={row.id}
            className="rounded-sm border border-[color-mix(in_srgb,var(--tfmc-cream)_12%,transparent)] px-3 py-2"
          >
            <div className="flex flex-wrap items-baseline justify-between gap-2">
              <p className="font-medium text-[var(--tfmc-cream)]">
                {row.summary}
              </p>
              {/* ml-auto keeps the actions right-aligned even when a long
                  summary pushes them onto their own line. */}
              <div className="ml-auto flex shrink-0 gap-3">
                <button
                  type="button"
                  className={actionClass}
                  onClick={() => onEdit(row)}
                >
                  Edit
                </button>
                <button
                  type="button"
                  className="text-xs text-[#e8a0a0] underline-offset-2 hover:underline"
                  onClick={() => onDelete(row)}
                >
                  Delete
                </button>
              </div>
            </div>

            {/* Each field gets its own shape or colour so the row can be
                scanned without being read: rule is a bordered pill, ruling and
                punishment are tinted by outcome and severity, players are the
                only filled chips. */}
            <div className="mt-1.5 flex flex-wrap items-center gap-x-2 gap-y-1 text-xs">
              {row.rule ? (
                <span className={rulePillClass} title={`Rule ${row.rule}`}>
                  {row.rule}
                </span>
              ) : null}
              {visibleRuling(row.ruling) ? (
                <span
                  className={`font-medium ${toneClass[rulingTone(row.ruling)]}`}
                >
                  {visibleRuling(row.ruling)}
                </span>
              ) : null}
              {row.punishment ? (
                <span
                  className={`font-medium ${
                    toneClass[punishmentTone(row.punishment)]
                  }`}
                >
                  {row.punishment}
                </span>
              ) : null}
              {row.players.map((p) => (
                <span key={p} className={playerChipClass}>
                  {p}
                </span>
              ))}
            </div>

            <p className="mt-1.5 flex flex-wrap items-center gap-x-2 text-xs">
              <span className={loggedByClass}>{row.logged_by}</span>
              <span className={dateClass}>
                {formatCreatedAt(row.created_at)}
              </span>
              <span className={idClass}>{row.id}</span>
            </p>
          </li>
        ))}
      </ul>
    </div>
  );
}
