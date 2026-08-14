import type { CSSProperties } from "react";
import type { OverlayBBox } from "./types";

export function overlayStyle(
  bbox: OverlayBBox | undefined,
  mapW: number,
  mapH: number
): CSSProperties {
  if (!bbox?.w || !bbox?.h || !mapW || !mapH) {
    return {
      left: 0,
      top: 0,
      width: 0,
      height: 0,
      visibility: "hidden",
    };
  }

  return {
    left: `${(bbox.x / mapW) * 100}%`,
    top: `${(bbox.y / mapH) * 100}%`,
    width: `${(bbox.w / mapW) * 100}%`,
    height: `${(bbox.h / mapH) * 100}%`,
  };
}
