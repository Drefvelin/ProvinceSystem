// hooks/mapHover/useMapCoords.ts
const MAP_BOUNDS: Record<string, number> = {
  main: 4096,
  dev: 6400,
};

export function getMapCoords(
  event: React.MouseEvent,
  canvas: HTMLCanvasElement,
  mapId: "main" | "dev"
) {
  const rect = canvas.getBoundingClientRect();
  const mapSize = MAP_BOUNDS[mapId] ?? 6400;

  const mouseX = event.clientX - rect.left;
  const mouseY = event.clientY - rect.top;

  if (
    mouseX < 0 ||
    mouseY < 0 ||
    mouseX >= rect.width ||
    mouseY >= rect.height
  ) {
    return null;
  }

  return {
    x: Math.floor((mouseX / rect.width) * mapSize),
    y: Math.floor((mouseY / rect.height) * mapSize),
    screenX: event.clientX,
    screenY: event.clientY,
  };
}
