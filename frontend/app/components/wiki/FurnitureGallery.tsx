"use client";

import { useEffect, useState } from "react";

import StationModelViewer from "./StationModelViewer";

type FurniturePreview = { name: string; id: string };

const textureById: Record<string, string> = {
  frying_pan: "frying_pan",
  saucepan: "frying_pan",
  pot: "pot",
  bowl: "plate",
  cutting_board: "cutting_board",
  butter_churn: "butter_churn",
  butter_plate: "plate",
  plate: "plate",
  bucket: "bucket",
  fire_pit: "fire_pit",
  meat_hook: "meat_hook",
  mixing_bowl: "plate",
  milling_stone: "milling_stone",
  oven_bottom: "oven",
  bread_tray: "tray",
  oven_top: "oven",
  liquid_container: "liquid_container",
  sausage_maker: "sausage_maker",
  tool_shelf: "tool_shelf",
  pedestal: "pedestal",
  artifact_display: "artifact_display",
  lure: "lure",
};

export default function FurnitureGallery({ pieces }: { pieces: FurniturePreview[] }) {
  const [selectedId, setSelectedId] = useState(pieces[0]?.id ?? "");

  useEffect(() => {
    const selectFromUrl = () => {
      const requested = new URL(window.location.href).searchParams.get("piece");
      const match = pieces.find((piece) => (piece.id.split(":").at(-1) ?? piece.id) === requested);
      setSelectedId(match?.id ?? pieces[0]?.id ?? "");
    };

    selectFromUrl();
    window.addEventListener("popstate", selectFromUrl);
    window.addEventListener("hashchange", selectFromUrl);
    return () => {
      window.removeEventListener("popstate", selectFromUrl);
      window.removeEventListener("hashchange", selectFromUrl);
    };
  }, [pieces]);

  const selected = pieces.find((piece) => piece.id === selectedId) ?? pieces[0];
  if (!selected) return null;

  const assetId = selected.id.split(":").at(-1) ?? selected.id;
  const textureId = textureById[assetId];

  return (
    <div className="mt-4 grid gap-4 lg:grid-cols-[minmax(0,1fr)_minmax(18rem,24rem)]">
      <ul className="grid grid-cols-2 gap-2 sm:grid-cols-3">
        {pieces.map((piece) => (
          <li key={piece.id}>
            <button
              type="button"
              aria-pressed={piece.id === selected.id}
              onClick={() => {
                setSelectedId(piece.id);
                const url = new URL(window.location.href);
                url.searchParams.set("piece", piece.id.split(":").at(-1) ?? piece.id);
                url.hash = "catalogue";
                window.history.pushState({}, "", url);
              }}
              className={`h-full w-full rounded border px-3 py-2 text-left text-sm transition-colors ${
                piece.id === selected.id
                  ? "border-[var(--tfmc-accent)] bg-[color-mix(in_srgb,var(--tfmc-accent)_12%,transparent)] text-[var(--tfmc-cream)]"
                  : "border-[color-mix(in_srgb,var(--tfmc-cream)_14%,transparent)] bg-[color-mix(in_srgb,var(--tfmc-forest-deep)_45%,transparent)] text-[var(--tfmc-mist)] hover:border-[color-mix(in_srgb,var(--tfmc-accent)_55%,transparent)] hover:text-[var(--tfmc-cream)]"
              }`}
            >
              {piece.name}
            </button>
          </li>
        ))}
      </ul>
      <div>
        <p className="mb-2 text-sm font-semibold text-[var(--tfmc-cream)]">{selected.name}</p>
        <StationModelViewer
          key={selected.id}
          modelUrl={`/wiki/models/furniture/${assetId}.json`}
          textureUrl={`/wiki/textures/furniture/${textureId}.png`}
        />
      </div>
    </div>
  );
}
