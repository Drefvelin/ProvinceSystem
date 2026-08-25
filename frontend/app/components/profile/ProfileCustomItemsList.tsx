"use client";

import Link from "next/link";
import type { ProfileCustomItem } from "../../../lib/profile/api";

function statusLabel(item: ProfileCustomItem): string {
  const state = String(item.state || "").trim().toLowerCase();
  const sub = String(item.submission_status || "").trim().toLowerCase();
  if (state === "pending_skin") {
    if (sub === "approved") return "Pending pack";
    return "Awaiting approval";
  }
  switch (state) {
    case "ready":
      return "Ready";
    case "denied":
      return "Denied";
    case "applied":
      return "Applied";
    case "draft":
      return "Draft";
    default:
      return state || "Unknown";
  }
}

type Props = {
  items: ProfileCustomItem[];
};

export default function ProfileCustomItemsList({ items }: Props) {
  if (items.length === 0) {
    return (
      <p className="text-sm text-[var(--tfmc-mist)]">
        No kit custom items in progress.
      </p>
    );
  }

  return (
    <ul className="flex flex-col gap-2">
      {items.map((item) => {
        const href = `/character/${encodeURIComponent(item.character_id)}/kits`;
        return (
          <li
            key={`${item.character_id}:${item.kit_key}`}
            className="rounded-sm border border-[color-mix(in_srgb,var(--tfmc-cream)_12%,transparent)] px-3 py-2"
          >
            <div className="flex flex-wrap items-baseline justify-between gap-2">
              <Link
                href={href}
                className="font-medium text-[var(--tfmc-cream)] hover:underline"
              >
                {item.display_name || item.kit_key}
              </Link>
              <span className="text-xs font-medium uppercase tracking-wide text-[var(--tfmc-stone)]">
                {statusLabel(item)}
              </span>
            </div>
            <p className="mt-1 text-xs text-[var(--tfmc-stone)]">
              {item.character_name} · {item.kit_key}
            </p>
            {item.deny_reason ? (
              <p className="mt-1 text-xs text-[#e8a0a0]">{item.deny_reason}</p>
            ) : null}
          </li>
        );
      })}
    </ul>
  );
}
