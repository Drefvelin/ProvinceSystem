"use client";

import { useId } from "react";

type Props = {
  open: boolean;
  summary: string;
  deleting: boolean;
  error: string | null;
  onCancel: () => void;
  onConfirm: () => void;
};

/** Deletion is permanent and has no undo, so it gets the same two-step
 *  confirmation the Discord /case-delete command requires. */
export default function ConfirmDeleteDialog({
  open,
  summary,
  deleting,
  error,
  onCancel,
  onConfirm,
}: Props) {
  const titleId = useId();
  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center bg-[color-mix(in_srgb,var(--tfmc-forest)_72%,black)]/80 p-4 backdrop-blur-[2px] sm:items-center"
      role="presentation"
      onClick={() => {
        if (!deleting) onCancel();
      }}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        className="w-full max-w-sm rounded-sm border border-[color-mix(in_srgb,var(--tfmc-cream)_22%,transparent)] bg-[var(--tfmc-forest)] p-4 shadow-lg"
        onClick={(e) => e.stopPropagation()}
      >
        <h2
          id={titleId}
          className="font-[family-name:var(--font-display)] text-lg text-[var(--tfmc-cream)]"
        >
          Delete this case?
        </h2>
        <p className="mt-2 text-sm text-[var(--tfmc-mist)]">
          This is permanent. It will no longer inform precedent searches.
        </p>
        <p className="mt-2 rounded-sm border border-[color-mix(in_srgb,var(--tfmc-cream)_12%,transparent)] px-3 py-2 text-sm text-[var(--tfmc-stone)]">
          {summary}
        </p>

        {error ? <p className="mt-3 text-xs text-[#e8a0a0]">{error}</p> : null}

        <div className="mt-5 flex items-center justify-end gap-3">
          <button
            type="button"
            disabled={deleting}
            onClick={onCancel}
            className="text-sm text-[var(--tfmc-stone)] underline-offset-2 hover:text-[var(--tfmc-cream)] hover:underline disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            type="button"
            disabled={deleting}
            onClick={onConfirm}
            className="rounded-sm border border-[#e8a0a0] px-4 py-2 text-sm font-semibold text-[#e8a0a0] transition-colors hover:bg-[color-mix(in_srgb,#e8a0a0_12%,transparent)] disabled:opacity-50"
          >
            {deleting ? "Deleting…" : "Delete"}
          </button>
        </div>
      </div>
    </div>
  );
}
