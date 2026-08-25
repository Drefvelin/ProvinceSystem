export const LABEL_MIN_INSET_PX = 40;
export const LABEL_INSET_PADDING_PX = 8;
export const LABEL_GRID_MAX_CANDIDATES = 150;
export const LABEL_CORRIDOR_SAMPLE_STEP_PX = 6;
export const LABEL_RADIAL_ANGLE_STEPS = 12;
export const LABEL_GLYPH_WIDTH_EM = 0.58;
export const LABEL_ARC_BULGE_RATIO = 0.08;
export const LABEL_TEXT_CENTER_OFFSET_EM = 0.38;

export type ProvinceLabelGridMeta = {
  mapWidth: number;
  mapHeight: number;
  gridWidth: number;
  gridHeight: number;
};

export type ProvinceLabelGrid = ProvinceLabelGridMeta & {
  cells: Uint16Array;
  scaleX: number;
  scaleY: number;
};

export type LabelEndpoints = {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
};

export function parseProvinceLabelGrid(
  meta: ProvinceLabelGridMeta,
  buffer: ArrayBuffer
): ProvinceLabelGrid {
  const expectedBytes = meta.gridWidth * meta.gridHeight * 2;
  if (buffer.byteLength < expectedBytes) {
    throw new Error(
      `Label grid buffer too small: ${buffer.byteLength} < ${expectedBytes}`
    );
  }

  return {
    ...meta,
    cells: new Uint16Array(buffer, 0, meta.gridWidth * meta.gridHeight),
    scaleX: meta.mapWidth / meta.gridWidth,
    scaleY: meta.mapHeight / meta.gridHeight,
  };
}

function segmentPixelLength(
  x1: number,
  y1: number,
  x2: number,
  y2: number
): number {
  return Math.hypot(x2 - x1, y2 - y1);
}

function fontSizeForLabel(segmentPx: number, text: string): number {
  const units = text.trim().length || 1;
  if (segmentPx <= 0) return 1;
  return Math.round(segmentPx / (units * LABEL_GLYPH_WIDTH_EM));
}

export function labelCorridorMargin(
  segmentPx: number,
  fontSize: number
): number {
  const textBand =
    fontSize * LABEL_TEXT_CENTER_OFFSET_EM + segmentPx * LABEL_ARC_BULGE_RATIO;
  return Math.max(LABEL_MIN_INSET_PX, textBand + LABEL_INSET_PADDING_PX);
}

export function buildComponentMask(
  grid: ProvinceLabelGrid,
  provinceIds: number[]
): Uint8Array {
  const allowed = new Set(provinceIds);
  const { cells } = grid;
  const mask = new Uint8Array(grid.gridWidth * grid.gridHeight);

  for (let i = 0; i < cells.length; i += 1) {
    if (allowed.has(cells[i])) {
      mask[i] = 1;
    }
  }

  return mask;
}

/** Multi-source BFS clearance from blob border, in map pixels (conservative). */
export function distanceTransform(
  mask: Uint8Array,
  grid: ProvinceLabelGrid
): Float32Array {
  const { gridWidth, gridHeight, scaleX, scaleY } = grid;
  const cellScale = Math.min(scaleX, scaleY);
  const size = gridWidth * gridHeight;
  const dist = new Float32Array(size);
  dist.fill(-1);

  const queue: number[] = [];
  for (let idx = 0; idx < size; idx += 1) {
    if (mask[idx] === 0) {
      dist[idx] = 0;
      queue.push(idx);
      continue;
    }

    const x = idx % gridWidth;
    const y = (idx / gridWidth) | 0;
    const onGridEdge =
      x === 0 ||
      x === gridWidth - 1 ||
      y === 0 ||
      y === gridHeight - 1;
    if (onGridEdge) {
      dist[idx] = 0;
      queue.push(idx);
    }
  }

  let head = 0;
  while (head < queue.length) {
    const idx = queue[head++];
    const x = idx % gridWidth;
    const y = (idx / gridWidth) | 0;
    const nextDist = dist[idx] + 1;

    if (x > 0) pushNeighbor(idx - 1, nextDist);
    if (x + 1 < gridWidth) pushNeighbor(idx + 1, nextDist);
    if (y > 0) pushNeighbor(idx - gridWidth, nextDist);
    if (y + 1 < gridHeight) pushNeighbor(idx + gridWidth, nextDist);
  }

  function pushNeighbor(neighbor: number, nextDist: number) {
    if (mask[neighbor] === 0 || dist[neighbor] >= 0) return;
    dist[neighbor] = nextDist;
    queue.push(neighbor);
  }

  for (let idx = 0; idx < size; idx += 1) {
    if (mask[idx] === 1 && dist[idx] >= 0) {
      dist[idx] *= cellScale;
    } else {
      dist[idx] = 0;
    }
  }

  return dist;
}

/** Sea / black gaps in province_label_grid (0 = no land). Labels may cross these. */
export function isLabelCorridorWaterCell(
  grid: ProvinceLabelGrid,
  gridIndex: number
): boolean {
  return grid.cells[gridIndex] === 0;
}

function clearanceAt(
  grid: ProvinceLabelGrid,
  dist: Float32Array,
  mapX: number,
  mapY: number
): number {
  const gx = Math.min(
    grid.gridWidth - 1,
    Math.max(0, Math.floor(mapX / grid.scaleX))
  );
  const gy = Math.min(
    grid.gridHeight - 1,
    Math.max(0, Math.floor(mapY / grid.scaleY))
  );
  const idx = gy * grid.gridWidth + gx;
  if (isLabelCorridorWaterCell(grid, idx)) {
    return Number.POSITIVE_INFINITY;
  }
  return dist[idx];
}

function orientLabelEndpoints(
  x1: number,
  y1: number,
  x2: number,
  y2: number
): { x1: number; y1: number; x2: number; y2: number } {
  const rad = Math.atan2(y2 - y1, x2 - x1);
  const deg = (rad * 180) / Math.PI;
  if (deg <= -90 || deg > 90) {
    return { x1: x2, y1: y2, x2: x1, y2: y1 };
  }
  return { x1, y1, x2, y2 };
}

function quadraticPoint(
  ax: number,
  ay: number,
  cx: number,
  cy: number,
  bx: number,
  by: number,
  t: number
): { x: number; y: number } {
  const u = 1 - t;
  return {
    x: u * u * ax + 2 * u * t * cx + t * t * bx,
    y: u * u * ay + 2 * u * t * cy + t * t * by,
  };
}

function arcControlPoint(
  x1: number,
  y1: number,
  x2: number,
  y2: number
): { cx: number; cy: number } {
  const oriented = orientLabelEndpoints(x1, y1, x2, y2);
  const ax = oriented.x1;
  const ay = oriented.y1;
  const bx = oriented.x2;
  const by = oriented.y2;
  const dx = bx - ax;
  const dy = by - ay;
  const len = Math.hypot(dx, dy);
  if (len === 0) {
    return { cx: ax, cy: ay };
  }
  const mx = (ax + bx) / 2;
  const my = (ay + by) / 2;
  const nx = dy / len;
  const ny = -dx / len;
  const bulge = len * LABEL_ARC_BULGE_RATIO;
  return { cx: mx + nx * bulge, cy: my + ny * bulge };
}

export function corridorClear(
  x1: number,
  y1: number,
  x2: number,
  y2: number,
  margin: number,
  grid: ProvinceLabelGrid,
  dist: Float32Array
): boolean {
  const len = segmentPixelLength(x1, y1, x2, y2);
  if (len === 0) {
    return clearanceAt(grid, dist, x1, y1) >= margin;
  }

  const step = Math.max(
    LABEL_CORRIDOR_SAMPLE_STEP_PX,
    Math.min(grid.scaleX, grid.scaleY) * 0.5
  );
  const steps = Math.max(2, Math.ceil(len / step));
  const { cx, cy } = arcControlPoint(x1, y1, x2, y2);

  for (let i = 0; i <= steps; i += 1) {
    const t = i / steps;
    const chordX = x1 + (x2 - x1) * t;
    const chordY = y1 + (y2 - y1) * t;
    const arc = quadraticPoint(x1, y1, cx, cy, x2, y2, t);

    if (clearanceAt(grid, dist, chordX, chordY) < margin) return false;
    if (clearanceAt(grid, dist, arc.x, arc.y) < margin) return false;
  }

  return true;
}

type CandidatePoint = { x: number; y: number };

function collectCandidates(
  grid: ProvinceLabelGrid,
  mask: Uint8Array,
  dist: Float32Array,
  minClearance: number
): CandidatePoint[] {
  const { gridWidth, gridHeight, scaleX, scaleY } = grid;
  const points: CandidatePoint[] = [];

  for (let gy = 0; gy < gridHeight; gy += 1) {
    for (let gx = 0; gx < gridWidth; gx += 1) {
      const idx = gy * gridWidth + gx;
      if (mask[idx] === 0) continue;
      if (dist[idx] < minClearance) continue;
      points.push({
        x: (gx + 0.5) * scaleX,
        y: (gy + 0.5) * scaleY,
      });
    }
  }

  if (points.length <= LABEL_GRID_MAX_CANDIDATES) {
    return points;
  }

  const stride = Math.ceil(points.length / LABEL_GRID_MAX_CANDIDATES);
  return points.filter((_, index) => index % stride === 0);
}

function tryFindSegment(
  candidates: CandidatePoint[],
  text: string,
  grid: ProvinceLabelGrid,
  dist: Float32Array,
  marginScale: number
): LabelEndpoints | null {
  const pairs: Array<{ a: CandidatePoint; b: CandidatePoint; len: number }> =
    [];

  for (let i = 0; i < candidates.length; i += 1) {
    for (let j = i + 1; j < candidates.length; j += 1) {
      const a = candidates[i];
      const b = candidates[j];
      pairs.push({
        a,
        b,
        len: segmentPixelLength(a.x, a.y, b.x, b.y),
      });
    }
  }

  pairs.sort((left, right) => right.len - left.len);

  for (const pair of pairs) {
    const fontSize = fontSizeForLabel(pair.len, text);
    const margin = labelCorridorMargin(pair.len, fontSize) * marginScale;
    if (
      corridorClear(pair.a.x, pair.a.y, pair.b.x, pair.b.y, margin, grid, dist)
    ) {
      return { x1: pair.a.x, y1: pair.a.y, x2: pair.b.x, y2: pair.b.y };
    }
  }

  return null;
}

export function findLabelAnchor(
  mask: Uint8Array,
  dist: Float32Array,
  grid: ProvinceLabelGrid
): { x: number; y: number } | null {
  let bestIdx = -1;
  let bestClearance = -1;

  for (let idx = 0; idx < mask.length; idx += 1) {
    if (mask[idx] === 0) continue;
    const clearance = dist[idx];
    if (clearance > bestClearance) {
      bestClearance = clearance;
      bestIdx = idx;
    }
  }

  if (bestIdx < 0) return null;

  const gx = bestIdx % grid.gridWidth;
  const gy = (bestIdx / grid.gridWidth) | 0;
  return {
    x: (gx + 0.5) * grid.scaleX,
    y: (gy + 0.5) * grid.scaleY,
  };
}

export function raycastHalfExtent(
  anchorX: number,
  anchorY: number,
  angle: number,
  margin: number,
  grid: ProvinceLabelGrid,
  dist: Float32Array,
  mask: Uint8Array
): number {
  const ux = Math.cos(angle);
  const uy = Math.sin(angle);
  const step = Math.max(
    LABEL_CORRIDOR_SAMPLE_STEP_PX,
    Math.min(grid.scaleX, grid.scaleY) * 0.5
  );
  const maxDist = Math.max(grid.mapWidth, grid.mapHeight) * 2;
  let distance = 0;

  while (distance + step <= maxDist) {
    const nextDist = distance + step;
    const x = anchorX + ux * nextDist;
    const y = anchorY + uy * nextDist;

    if (x < 0 || y < 0 || x > grid.mapWidth || y > grid.mapHeight) {
      break;
    }

    const gx = Math.floor(x / grid.scaleX);
    const gy = Math.floor(y / grid.scaleY);
    if (gx < 0 || gy < 0 || gx >= grid.gridWidth || gy >= grid.gridHeight) {
      break;
    }

    const idx = gy * grid.gridWidth + gx;
    if (!isLabelCorridorWaterCell(grid, idx) && mask[idx] === 0) {
      break;
    }

    if (clearanceAt(grid, dist, x, y) < margin) {
      break;
    }

    distance = nextDist;
  }

  return distance;
}

export function tryRadialSegment(
  mask: Uint8Array,
  dist: Float32Array,
  grid: ProvinceLabelGrid,
  text: string,
  marginScale: number,
  anchor?: { x: number; y: number }
): LabelEndpoints | null {
  const center = anchor ?? findLabelAnchor(mask, dist, grid);
  if (!center) return null;

  const anchorClearance = clearanceAt(grid, dist, center.x, center.y);
  if (anchorClearance <= 0) return null;

  let best: { endpoints: LabelEndpoints; len: number } | null = null;

  for (let i = 0; i < LABEL_RADIAL_ANGLE_STEPS; i += 1) {
    const angle = (i / LABEL_RADIAL_ANGLE_STEPS) * Math.PI;
    const probeMargin = 1;
    let forward = raycastHalfExtent(
      center.x,
      center.y,
      angle,
      probeMargin,
      grid,
      dist,
      mask
    );
    let backward = raycastHalfExtent(
      center.x,
      center.y,
      angle + Math.PI,
      probeMargin,
      grid,
      dist,
      mask
    );
    let totalLen = forward + backward;
    if (totalLen <= 0) continue;

    const fontSize = fontSizeForLabel(totalLen, text);
    const desiredMargin =
      labelCorridorMargin(totalLen, fontSize) * marginScale;
    const effectiveMargin = Math.min(desiredMargin, anchorClearance);

    forward = raycastHalfExtent(
      center.x,
      center.y,
      angle,
      effectiveMargin,
      grid,
      dist,
      mask
    );
    backward = raycastHalfExtent(
      center.x,
      center.y,
      angle + Math.PI,
      effectiveMargin,
      grid,
      dist,
      mask
    );
    totalLen = forward + backward;
    if (totalLen <= 0) continue;

    const ux = Math.cos(angle);
    const uy = Math.sin(angle);
    const x1 = center.x - backward * ux;
    const y1 = center.y - backward * uy;
    const x2 = center.x + forward * ux;
    const y2 = center.y + forward * uy;

    if (!corridorClear(x1, y1, x2, y2, effectiveMargin, grid, dist)) {
      continue;
    }

    if (!best || totalLen > best.len) {
      best = {
        endpoints: { x1, y1, x2, y2 },
        len: totalLen,
      };
    }
  }

  return best?.endpoints ?? null;
}

export function insetLabelEndpoints(
  componentIds: number[],
  text: string,
  grid: ProvinceLabelGrid,
  seed: LabelEndpoints
): LabelEndpoints | null {
  const mask = buildComponentMask(grid, componentIds);
  const dist = distanceTransform(mask, grid);
  const cellScale = Math.min(grid.scaleX, grid.scaleY);
  const candidates = collectCandidates(
    grid,
    mask,
    dist,
    Math.min(LABEL_MIN_INSET_PX, cellScale)
  );
  candidates.push(
    { x: seed.x1, y: seed.y1 },
    { x: seed.x2, y: seed.y2 }
  );

  if (candidates.length) {
    for (const marginScale of [1, 0.75, 0.5]) {
      const found = tryFindSegment(candidates, text, grid, dist, marginScale);
      if (found) {
        return found;
      }
    }
  }

  for (const marginScale of [1, 0.75, 0.5]) {
    const radial = tryRadialSegment(mask, dist, grid, text, marginScale);
    if (radial) {
      return radial;
    }
  }

  return null;
}

export async function decompressGzipBuffer(
  compressed: ArrayBuffer
): Promise<ArrayBuffer> {
  if (typeof DecompressionStream === "undefined") {
    throw new Error("DecompressionStream is not available in this environment");
  }

  const stream = new Blob([compressed])
    .stream()
    .pipeThrough(new DecompressionStream("gzip"));
  return new Response(stream).arrayBuffer();
}
