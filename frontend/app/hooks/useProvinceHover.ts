// hooks/mapHover/useProvinceHover.ts
import { useRef } from "react";

import type { MapId } from "../components/map/types";
import { fetchMapJson } from "@/lib/map/api";

export function useProvinceHover({
  mapId,
  mapType,
  setCursorTooltip,
  guildNameCacheRef,
  sessionToken,
}: {
  mapId: MapId;
  mapType: string;
  setCursorTooltip: (v: any) => void;
  guildNameCacheRef: React.MutableRefObject<Record<string, string>> | null;
  sessionToken?: string | null;
}) {
  const provinceCache = useRef<Record<number, any>>({});

  const capitalize = (v: string) => v[0].toUpperCase() + v.slice(1);

  const handleProvinceHover = (
    x: number,
    y: number,
    screenX: number,
    screenY: number
  ): boolean => {
    const active =
      mapType === "terrain" ||
      mapType === "fertility" ||
      mapType === "prosperity" ||
      mapType === "trade";

    if (!active) return false;

    void fetchMapJson<{ province_id?: number }>(
      `/${mapId}/province/${x},${y}/meta`,
      { sessionToken, cache: "no-store" }
    )
      .then((meta) => {
        if (!meta?.province_id) return;

        const render = (data: any) => {
          if (!data || data.terrain === "sea") return;

          const lines = [`x: ${x}  z: ${y}`];

          if (mapType === "terrain")
            lines.push(`Terrain: ${capitalize(data.terrain)}`);
          if (mapType === "fertility")
            lines.push(`Fertility: ${data.fertility}`);
          if (mapType === "prosperity")
            lines.push(`Prosperity: ${data.prosperity ?? 0}`);
          
          if ((mapType === "trade" || mapType === "prosperity") && data.trade_shares) {
            const entries = Object.entries(
                data.trade_shares as Record<string, number>
            ).sort((a, b) => b[1] - a[1]);

            let used = 0;
            const max = Math.min(5, entries.length);

            lines.push("Trade:");

            for (let i = 0; i < max; i++) {
                const [guild, ratio] = entries[i];
                used += ratio;

                const name =
                guildNameCacheRef?.current[guild] ??
                guild.replace(/_/g, " ");

                lines.push(`• ${name}: ${(ratio * 100).toFixed(1)}%`);
            }

            const remaining = 1 - used;
            if (remaining > 0.01) {
                lines.push(`• Other: ${(remaining * 100).toFixed(1)}%`);
            }
          }

          setCursorTooltip({
            x: screenX,
            y: screenY,
            text: lines.join("\n"),
          });
        };

        const pid = meta.province_id;

        if (!provinceCache.current[pid]) {
          void fetchMapJson<Record<number, any>>(
            `/${mapId}/compiled_data/provinces`,
            { sessionToken, cache: "no-store" }
          ).then((all) => {
            provinceCache.current = all;
            render(all[pid]);
          });
        } else {
          render(provinceCache.current[pid]);
        }
      })
      .catch(() => {});

    const consumesHover =
        mapType === "terrain" ||
        mapType === "fertility" ||
        mapType === "prosperity";

    return consumesHover;
  };

  return { handleProvinceHover };
}
