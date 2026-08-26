import Link from "next/link";
import { navItems } from "./data";

const blurbs: Record<string, string> = {
  "/wiki/arcane-trace-detector":
    "Hunt the server's single hidden source of Arcane Radiation with a clicking, glowing detector. A serverwide loot race.",
  "/wiki/musical-instruments":
    "Nine instruments turn your hotbar into a keyboard. Bards craft, equip, and play.",
  "/wiki/mount-whistle":
    "Right-click to reveal every mount within 64 blocks, glowing through walls.",
  "/wiki/materials":
    "The full custom material catalogue — Mythril, Coke, and everything else players craft or find.",
  "/wiki/stations":
    "Every crafting station, with an interactive 3D preview where a model exists.",
};

export default function WikiOverviewPage() {
  return (
    <div className="max-w-2xl">
      <h1 className="font-[family-name:var(--font-fraunces)] text-3xl text-[var(--tfmc-cream)] sm:text-4xl">
        Gameplay Guide
      </h1>
      <p className="mt-2 text-sm text-[var(--tfmc-mist)]">
        TFMC Season 5 — crafting stations, recipes, and mechanics for the custom systems on
        the server. More sections will be added as the season goes on.
      </p>

      <div className="mt-8 flex flex-col gap-3">
        {navItems
          .filter((item) => item.href !== "/wiki")
          .map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="rounded-md border border-[color-mix(in_srgb,var(--tfmc-cream)_12%,transparent)] bg-[color-mix(in_srgb,var(--tfmc-forest)_45%,transparent)] p-4 transition-colors hover:border-[var(--tfmc-accent)]"
            >
              <p className="font-[family-name:var(--font-fraunces)] text-lg text-[var(--tfmc-cream)]">
                {item.label}
              </p>
              <p className="mt-1 text-sm text-[var(--tfmc-mist)]">{blurbs[item.href]}</p>
            </Link>
          ))}
      </div>
    </div>
  );
}
