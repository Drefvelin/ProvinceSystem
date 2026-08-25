import { memo } from "react";
import {
  LABEL_INK,
  LABEL_FONT_WEIGHT,
  shouldShowLabelAtScreenSize,
  type NationLabelSpec,
} from "../../lib/mapLabels";
import { HOVER_OVERLAY_EXPAND } from "./overlayStyle";

const LABEL_HOVER_SCALE = 1 + HOVER_OVERLAY_EXPAND;
const LABEL_HOVER_TRANSITION = "transform 150ms ease-out";
const LABEL_VISIBILITY_TRANSITION = "opacity 200ms ease-out";

type LabelLayerProps = {
  labels: NationLabelSpec[];
  mapW: number;
  mapH: number;
  displayScale: number;
  hoveredNationId?: string | null;
};

export default memo(LabelLayer);

function LabelLayer({
  labels,
  mapW,
  mapH,
  displayScale,
  hoveredNationId = null,
}: LabelLayerProps) {
  if (!labels.length || !mapW || !mapH || displayScale <= 0) {
    return null;
  }

  return (
    <svg
      className="pointer-events-none absolute left-0 top-0 z-[15] h-full w-full"
      viewBox={`0 0 ${mapW} ${mapH}`}
      preserveAspectRatio="xMidYMid meet"
      aria-hidden
    >
      {labels.map((label) => {
        const pathId = `map-label-${label.nationId}-${label.componentIndex}`;
        const hovered = hoveredNationId === label.nationId;
        const visible = shouldShowLabelAtScreenSize(
          label.fontSize,
          displayScale
        );
        const hoverTransform = hovered
          ? `translate(${label.cx} ${label.cy}) scale(${LABEL_HOVER_SCALE}) translate(${-label.cx} ${-label.cy})`
          : undefined;

        return (
          <g
            key={`${label.nationId}:${label.componentIndex}`}
            style={{
              pointerEvents: "none",
              opacity: visible ? 1 : 0,
              transform: hoverTransform,
              transformOrigin: `${label.cx}px ${label.cy}px`,
              transition: `${LABEL_VISIBILITY_TRANSITION}, ${LABEL_HOVER_TRANSITION}`,
            }}
          >
            <g
              transform={`translate(${label.pathOffsetX} ${label.pathOffsetY})`}
            >
              <path id={pathId} d={label.pathD} fill="none" />
              <text
                fontSize={label.fontSize}
                fill={LABEL_INK}
                style={{
                  fontFamily: "var(--font-fraunces), serif",
                  fontWeight: LABEL_FONT_WEIGHT,
                }}
              >
                <textPath
                  href={`#${pathId}`}
                  startOffset="50%"
                  textAnchor="middle"
                >
                  {label.text}
                </textPath>
              </text>
            </g>
          </g>
        );
      })}
    </svg>
  );
}
