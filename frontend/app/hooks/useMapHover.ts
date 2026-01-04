// hooks/mapHover/useMapHover.ts
import { getMapCoords } from "./useMapCoords";
import { useProvinceHover } from "./useProvinceHover";
import { useRegionHover } from "./useRegionHover";

export function useMapHover(props: any) {
  const {
    canvasRef,
    mapId,
    mapType,
    loading,
    setCursorTooltip,
    guildNameCacheRef,
  } = props;

  const { handleProvinceHover } = useProvinceHover({
    mapId,
    mapType,
    setCursorTooltip,
    guildNameCacheRef,
  });

  const { handleRegionHover } = useRegionHover(props);

  const onMouseMove = (event: React.MouseEvent<HTMLDivElement>) => {
    if (loading) return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const coords = getMapCoords(event, canvas, mapId);
    if (!coords) {
      setCursorTooltip(null);
      return;
    }

    setCursorTooltip({
      x: coords.screenX,
      y: coords.screenY,
      text: `x: ${coords.x}  z: ${coords.y}`,
    });

    if (
      handleProvinceHover(
        coords.x,
        coords.y,
        coords.screenX,
        coords.screenY
      )
    ) {
      return;
    }

    handleRegionHover(
      ctx,
      coords.x,
      coords.y,
      coords.screenX,
      coords.screenY,
      setCursorTooltip
    );
  };

  return { onMouseMove };
}
