"use client";

import Link from "next/link";
import type {
  ProfileDrinkSubmission,
  ProfileSkinSubmission,
} from "../../../lib/profile/api";

function statusClass(status: string): string {
  const s = status.toLowerCase();
  if (s === "denied" || s === "rejected") return "text-[#e8a0a0]";
  if (s === "pending") return "text-[var(--tfmc-mist)]";
  return "text-[var(--tfmc-stone)]";
}

type Props = {
  skins: ProfileSkinSubmission[];
  drinks: ProfileDrinkSubmission[];
};

export default function ProfileSubmissionList({ skins, drinks }: Props) {
  if (skins.length === 0 && drinks.length === 0) {
    return (
      <p className="text-sm text-[var(--tfmc-mist)]">
        No skin or drink submissions yet. Use a skin or drink token on the Skins
        or Drinks pages to upload.
      </p>
    );
  }

  return (
    <div className="flex flex-col gap-8">
      {skins.length > 0 ? (
        <section>
          <h3 className="text-xs font-medium uppercase tracking-widest text-[var(--tfmc-stone)]">
            Skins
          </h3>
          <ul className="mt-3 flex flex-col gap-2">
            {skins.map((row) => (
              <li
                key={row.id}
                className="rounded-sm border border-[color-mix(in_srgb,var(--tfmc-cream)_12%,transparent)] px-3 py-2"
              >
                <div className="flex flex-wrap items-baseline justify-between gap-2">
                  <Link
                    href={`/skins/${encodeURIComponent(row.id)}`}
                    className="font-medium text-[var(--tfmc-cream)] hover:underline"
                  >
                    {row.display_name || row.slug}
                  </Link>
                  <span
                    className={`text-xs font-medium uppercase tracking-wide ${statusClass(row.status)}`}
                  >
                    {row.status}
                  </span>
                </div>
                <p className="mt-1 text-xs text-[var(--tfmc-stone)]">
                  {row.kind} · {row.created_at}
                </p>
                {row.deny_reason ? (
                  <p className="mt-1 text-xs text-[#e8a0a0]">{row.deny_reason}</p>
                ) : null}
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      {drinks.length > 0 ? (
        <section>
          <h3 className="text-xs font-medium uppercase tracking-widest text-[var(--tfmc-stone)]">
            Drinks
          </h3>
          <ul className="mt-3 flex flex-col gap-2">
            {drinks.map((row) => (
              <li
                key={row.id}
                className="rounded-sm border border-[color-mix(in_srgb,var(--tfmc-cream)_12%,transparent)] px-3 py-2"
              >
                <div className="flex flex-wrap items-baseline justify-between gap-2">
                  <Link
                    href={`/drinks/${encodeURIComponent(row.id)}`}
                    className="font-medium text-[var(--tfmc-cream)] hover:underline"
                  >
                    {row.display_name || row.slug}
                  </Link>
                  <span
                    className={`text-xs font-medium uppercase tracking-wide ${statusClass(row.status)}`}
                  >
                    {row.status}
                  </span>
                </div>
                <p className="mt-1 text-xs text-[var(--tfmc-stone)]">
                  {row.created_at}
                </p>
                {row.deny_reason ? (
                  <p className="mt-1 text-xs text-[#e8a0a0]">{row.deny_reason}</p>
                ) : null}
              </li>
            ))}
          </ul>
        </section>
      ) : null}
    </div>
  );
}
