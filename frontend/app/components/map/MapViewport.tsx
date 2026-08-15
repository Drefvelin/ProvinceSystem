import type { CSSProperties, ReactNode, RefObject } from "react";

import type { Size } from "../../lib/mapViewportMath";

export type MapViewportProps = {
  mapSize: Size;
  viewportRef: RefObject<HTMLDivElement | null>;
  transformStyle: string;
  transformTransition?: string;
  cursorClassName: string;
  isPanning: boolean;
  children: ReactNode;
};

export default function MapViewport({
  mapSize,
  viewportRef,
  transformStyle,
  transformTransition,
  cursorClassName,
  isPanning,
  children,
}: MapViewportProps) {
  const { w: mapW, h: mapH } = mapSize;

  const outerStyle: CSSProperties | undefined =
    mapW > 0 && mapH > 0 ? { aspectRatio: `${mapW} / ${mapH}` } : undefined;

  const innerStyle: CSSProperties = {
    width: mapW,
    height: mapH,
    transform: transformStyle,
    transformOrigin: "0 0",
    transition: transformTransition,
  };

  return (
    <div
      ref={viewportRef}
      className={`relative w-full overflow-hidden ${cursorClassName}${
        isPanning ? " select-none" : ""
      }`}
      style={outerStyle}
    >
      <div className="relative" style={innerStyle}>
        {children}
      </div>
    </div>
  );
}
