"use client";

import Link from "next/link";
import type { CharacterListItem } from "../../../lib/characters/api";

type Props = {
  characters: CharacterListItem[];
  aliveCount: number;
  maxSlots: number;
  onLogout: () => void;
  loggingOut?: boolean;
};

function Row({ item }: { item: CharacterListItem }) {
  const status = String(item.status || "").toUpperCase();
  return (
    <li className="char-row flex flex-col gap-1 border-b border-[color-mix(in_srgb,var(--tfmc-cream)_12%,transparent)] py-4 last:border-b-0 sm:flex-row sm:items-baseline sm:justify-between sm:gap-4">
      <div>
        <p className="font-[family-name:var(--font-fraunces)] text-lg text-[var(--tfmc-cream)]">
          {item.name || "Unnamed"}
        </p>
        <p className="mt-1 text-sm text-[var(--tfmc-mist)]">
          {[item.race, item.class].filter(Boolean).join(" · ") || "—"}
        </p>
      </div>
      <span className="text-xs font-medium uppercase tracking-wide text-[var(--tfmc-stone)]">
        {status}
      </span>
    </li>
  );
}

function Section({
  title,
  items,
  empty,
}: {
  title: string;
  items: CharacterListItem[];
  empty?: string;
}) {
  if (items.length === 0 && !empty) return null;
  return (
    <section className="mt-10">
      <h2 className="font-[family-name:var(--font-fraunces)] text-xl text-[var(--tfmc-cream)]">
        {title}
      </h2>
      {items.length === 0 ? (
        <p className="mt-3 text-sm text-[var(--tfmc-mist)]">{empty}</p>
      ) : (
        <ul className="mt-2">{items.map((c) => <Row key={c.id} item={c} />)}</ul>
      )}
    </section>
  );
}

export default function CharacterList({
  characters,
  aliveCount,
  maxSlots,
  onLogout,
  loggingOut = false,
}: Props) {
  const alive = characters.filter(
    (c) => String(c.status).toUpperCase() === "ALIVE"
  );
  const pending = characters.filter(
    (c) => String(c.status).toLowerCase() === "pending"
  );
  const dead = characters.filter((c) => {
    const s = String(c.status).toUpperCase();
    return s === "DEAD" || s === "MISSING";
  });

  const atLimit = aliveCount >= maxSlots;
  const hasAny = characters.length > 0;

  return (
    <div className="char-rise mt-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <p className="text-sm text-[var(--tfmc-stone)]">
          Alive slots {aliveCount} / {maxSlots}
        </p>
        <div className="flex flex-wrap items-center gap-3">
          {atLimit ? (
            <span className="text-sm text-[var(--tfmc-mist)]">
              No free slot
            </span>
          ) : (
            <Link
              href="/character/create"
              className="inline-flex items-center justify-center rounded-sm bg-[var(--tfmc-accent)] px-4 py-2 text-sm font-semibold text-[var(--tfmc-forest-deep)] transition-opacity hover:opacity-90"
            >
              Create
            </Link>
          )}
          <button
            type="button"
            onClick={onLogout}
            disabled={loggingOut}
            className="text-sm text-[var(--tfmc-stone)] underline-offset-2 hover:text-[var(--tfmc-cream)] hover:underline disabled:opacity-50"
          >
            {loggingOut ? "Logging out…" : "Log out"}
          </button>
        </div>
      </div>

      {!hasAny ? (
        <div className="mt-12 text-center">
          <p className="text-[var(--tfmc-mist)]">No characters yet.</p>
          {!atLimit ? (
            <Link
              href="/character/create"
              className="mt-6 inline-flex items-center justify-center rounded-sm bg-[var(--tfmc-accent)] px-5 py-2.5 text-sm font-semibold text-[var(--tfmc-forest-deep)] transition-opacity hover:opacity-90"
            >
              Create a character
            </Link>
          ) : null}
        </div>
      ) : (
        <>
          <Section title="Alive" items={alive} empty="No alive characters." />
          <Section title="Pending" items={pending} />
          <Section title="Dead" items={dead} />
        </>
      )}
    </div>
  );
}
