// hooks/mapHover/useRegionHover.ts
export function useRegionHover({
  mapId,
  mapType,
  regionData,
  getHoverRegion,
  setHoveredColor,
  setRegionInfo,
  setSelectedRegionId,
  mapDisplayName,
}: any) {
  const capitalize = (v: string) => v[0].toUpperCase() + v.slice(1);

  const handleRegionHover = (
    ctx: CanvasRenderingContext2D,
    x: number,
    y: number,
    screenX: number,
    screenY: number,
    setCursorTooltip: Function
  ) => {
    if (!regionData) return;

    const pixel = ctx.getImageData(x, y, 1, 1).data;
    const rgb = `${pixel[0]},${pixel[1]},${pixel[2]}`;

    const id = Object.keys(regionData).find(
      k => regionData[k].rgb === rgb
    );

    if (!id) {
      setHoveredColor(null);
      setRegionInfo(null);
      return;
    }

    setSelectedRegionId(id);

    const { imagePath, region } = getHoverRegion(
      mapType,
      mapId,
      id,
      regionData
    );

    setHoveredColor(imagePath);

    if (region) {
      setRegionInfo({
        title: region.name,
        tier: region.tier ?? capitalize(mapType),
        banner: region.banner,
        description:
            mapType === "trade"
            ? `The area of ${mapDisplayName} where ${region.name} dominates trade`
            : `A ${mapType === "nation" ? "Nation" : region.tier ?? capitalize(mapType)} in ${mapDisplayName}`,
      });
    }

    setCursorTooltip({
      x: screenX,
      y: screenY,
      text: `x: ${x}  z: ${y}`,
    });
  };

  return { handleRegionHover };
}
