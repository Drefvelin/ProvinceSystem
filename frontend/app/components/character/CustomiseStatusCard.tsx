"use client";

import type { LoreItemRow } from "../../../lib/characters/api";

function customiseState(item: LoreItemRow): string {
  const fromRow = String(item.state || "").trim().toLowerCase();
  if (fromRow) return fromRow;
  return String(item.draft?.state || "draft").trim().toLowerCase() || "draft";
}

function statusMessage(item: LoreItemRow): string {
  const state = customiseState(item);
  const deny = item.draft?.deny_reason?.trim() || "";
  switch (state) {
    case "pending_skin":
      return (
        "Submitted. It can take up to 5 minutes for your request to enter the system. " +
        "You will get a Discord DM once the kit is ready to claim. " +
        "Your custom skin needs staff approval before the kit is ready."
      );
    case "ready":
      return (
        "Your customise is ready. Claim the kit in-game when it is available " +
        "for this character."
      );
    case "denied":
      return deny
        ? `Denied: ${deny}`
        : "Denied. No reason given. Edit again to submit a different skin.";
    case "applied":
      return "Applied on the server.";
    case "draft":
      return "No customise submitted yet.";
    default:
      return state;
  }
}

type Props = {
  item: LoreItemRow;
};

export default function CustomiseStatusCard({ item }: Props) {
  const state = customiseState(item);
  const previewName =
    item.preview?.display_name?.trim() ||
    item.draft?.display_name?.trim() ||
    item.base_preview?.display_name ||
    item.kit_key;

  return (
    <div className="mt-8 space-y-6">
      <p className="text-lg text-[var(--tfmc-cream)]">{statusMessage(item)}</p>

      <dl className="space-y-3 text-sm">
        <div>
          <dt className="text-[var(--tfmc-stone)]">Status</dt>
          <dd className="font-medium text-[var(--tfmc-cream)]">{state}</dd>
        </div>
        <div>
          <dt className="text-[var(--tfmc-stone)]">Item</dt>
          <dd className="text-[var(--tfmc-cream)]">{previewName}</dd>
        </div>
        <div>
          <dt className="text-[var(--tfmc-stone)]">Kit key</dt>
          <dd className="break-all text-[var(--tfmc-mist)]">{item.kit_key}</dd>
        </div>
        {item.draft?.submission_id ? (
          <div>
            <dt className="text-[var(--tfmc-stone)]">Skin submission</dt>
            <dd className="break-all text-[var(--tfmc-mist)]">
              {item.draft.submission_id}
              {item.draft.submission_status
                ? ` (${item.draft.submission_status})`
                : ""}
            </dd>
          </div>
        ) : null}
      </dl>
    </div>
  );
}
