"use client";

import { useEffect, useState } from "react";
import type { SubmissionPublic } from "../../../lib/skins/api";
import { getReviewSheet, SkinsApiError } from "../../../lib/skins/api";
import { formatLocal } from "../../../lib/skins/formatTime";
import { getSession, isSessionValid } from "../../../lib/skins/session";

function statusMessage(row: SubmissionPublic): string {
  switch (row.status) {
    case "pending":
      return (
        "Submitted. It can take up to 5 minutes for your request to enter the " +
        "review system. You will get a Discord DM when it does. After that, " +
        "staff will review it."
      );
    case "denied":
      return row.deny_reason?.trim()
        ? `Denied: ${row.deny_reason.trim()}`
        : "Denied. No reason given.";
    case "approved":
      return "Approved. Waiting to be applied on the server.";
    case "applied":
      return "Live on the server.";
    case "revoked":
      return "Removed from the server.";
    default:
      return row.status;
  }
}

type Props = {
  row: SubmissionPublic;
};

export default function StatusCard({ row }: Props) {
  const [sheetUrl, setSheetUrl] = useState<string | null>(null);
  const [sheetError, setSheetError] = useState<string | null>(null);
  const [sheetLoading, setSheetLoading] = useState(true);

  useEffect(() => {
    let revoked = false;
    let objectUrl: string | null = null;

    async function loadSheet() {
      setSheetLoading(true);
      setSheetError(null);
      const session = getSession();
      if (!isSessionValid(session) || !session) {
        setSheetError("Session expired. Cannot load preview.");
        setSheetLoading(false);
        return;
      }
      try {
        const url = await getReviewSheet(row.id, session.session_token);
        if (revoked) {
          URL.revokeObjectURL(url);
          return;
        }
        objectUrl = url;
        setSheetUrl(url);
      } catch (err) {
        if (revoked) return;
        setSheetError(
          err instanceof SkinsApiError
            ? err.message
            : err instanceof Error
              ? err.message
              : "Could not load preview"
        );
      } finally {
        if (!revoked) setSheetLoading(false);
      }
    }

    void loadSheet();
    return () => {
      revoked = true;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [row.id]);

  return (
    <div className="mt-8 space-y-6">
      <p className="text-lg text-[var(--tfmc-cream)]">{statusMessage(row)}</p>

      <div className="space-y-2">
        <h2 className="text-sm font-medium text-[var(--tfmc-stone)]">
          Review preview
        </h2>
        {sheetLoading ? (
          <div className="flex items-center gap-3 py-8 text-sm text-[var(--tfmc-mist)]">
            <div
              className="h-6 w-6 animate-spin rounded-full border-2 border-[color-mix(in_srgb,var(--tfmc-cream)_25%,transparent)] border-t-[var(--tfmc-accent)]"
              aria-hidden
            />
            Loading preview…
          </div>
        ) : sheetError ? (
          <p className="text-sm text-[#e8a0a0]" role="alert">
            {sheetError}
          </p>
        ) : sheetUrl ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={sheetUrl}
            alt={`Review sheet for ${row.display_name}`}
            className="max-w-full rounded-sm border border-[color-mix(in_srgb,var(--tfmc-cream)_15%,transparent)]"
            style={{ imageRendering: "pixelated" }}
          />
        ) : null}
      </div>

      <dl className="space-y-3 text-sm">
        <div>
          <dt className="text-[var(--tfmc-stone)]">Status</dt>
          <dd className="font-medium text-[var(--tfmc-cream)]">{row.status}</dd>
        </div>
        <div>
          <dt className="text-[var(--tfmc-stone)]">Kind</dt>
          <dd className="text-[var(--tfmc-cream)]">{row.kind}</dd>
        </div>
        {row.tiers?.length ? (
          <div>
            <dt className="text-[var(--tfmc-stone)]">Armor tiers</dt>
            <dd className="text-[var(--tfmc-cream)]">
              {row.tiers.join(", ")}
            </dd>
          </div>
        ) : row.base_set ? (
          <div>
            <dt className="text-[var(--tfmc-stone)]">Applicable type</dt>
            <dd className="text-[var(--tfmc-cream)]">{row.base_set}</dd>
          </div>
        ) : null}
        <div>
          <dt className="text-[var(--tfmc-stone)]">Item name</dt>
          <dd className="text-[var(--tfmc-cream)]">{row.display_name}</dd>
        </div>
        {row.name_colours?.length || row.name_styles?.length ? (
          <div>
            <dt className="text-[var(--tfmc-stone)]">Name look</dt>
            <dd className="text-[var(--tfmc-cream)]">
              {row.name_colours?.length
                ? `${row.name_colours.length} colour${
                    row.name_colours.length === 1 ? "" : "s"
                  }`
                : "no colours"}
              {row.name_styles?.length
                ? ` · ${row.name_styles.join(", ")}`
                : ""}
            </dd>
          </div>
        ) : null}
        <div>
          <dt className="text-[var(--tfmc-stone)]">Apply name</dt>
          <dd className="text-[var(--tfmc-cream)]">
            {row.add_name ? "Yes" : "No"}
          </dd>
        </div>
        {row.grip_preset ? (
          <div>
            <dt className="text-[var(--tfmc-stone)]">Grip height</dt>
            <dd className="text-[var(--tfmc-cream)]">{row.grip_preset}</dd>
          </div>
        ) : null}
        <div>
          <dt className="text-[var(--tfmc-stone)]">Created</dt>
          <dd className="text-[var(--tfmc-mist)]">{formatLocal(row.created_at)}</dd>
        </div>
        {row.reviewed_at ? (
          <div>
            <dt className="text-[var(--tfmc-stone)]">Reviewed</dt>
            <dd className="text-[var(--tfmc-mist)]">{formatLocal(row.reviewed_at)}</dd>
          </div>
        ) : null}
        {row.applied_at ? (
          <div>
            <dt className="text-[var(--tfmc-stone)]">Applied</dt>
            <dd className="text-[var(--tfmc-mist)]">{formatLocal(row.applied_at)}</dd>
          </div>
        ) : null}
        <div>
          <dt className="text-[var(--tfmc-stone)]">Skin id</dt>
          <dd className="break-all text-[var(--tfmc-mist)]">{row.id}</dd>
        </div>
      </dl>
    </div>
  );
}
