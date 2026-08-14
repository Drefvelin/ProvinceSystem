import {
  LABEL_AXIS_DEBUG_COLOR,
  LABEL_HALO,
  LABEL_INK,
  LABEL_FONT_WEIGHT,
  type NationLabelSpec,
} from "../../lib/mapLabels";

type LabelLayerProps = {
  labels: NationLabelSpec[];
  mapW: number;
  mapH: number;
  visible: boolean;
};

function strokeWidthForFont(fontSize: number): number {
  return Math.max(2, Math.round(fontSize * 0.14));
}

export default function LabelLayer({
  labels,
  mapW,
  mapH,
  visible,
}: LabelLayerProps) {
  if (!visible || !labels.length || !mapW || !mapH) {
    return null;
  }

  return (
    <svg
      className="pointer-events-none absolute left-0 top-0 h-auto w-full"
      viewBox={`0 0 ${mapW} ${mapH}`}
      preserveAspectRatio="xMidYMid meet"
      aria-hidden
    >
      {labels.map((label) => (
        <g key={`${label.nationId}:${label.componentIndex}`}>
          <line
            x1={label.x1}
            y1={label.y1}
            x2={label.x2}
            y2={label.y2}
            stroke={LABEL_AXIS_DEBUG_COLOR}
            strokeWidth={3}
            strokeLinecap="round"
          />
          <text
            x={label.cx}
            y={label.cy}
            transform={`rotate(${label.angleDeg} ${label.cx} ${label.cy})`}
            textAnchor="middle"
            dominantBaseline="middle"
            fontSize={label.fontSize}
            textLength={label.textLength}
            lengthAdjust="spacingAndGlyphs"
            fill={LABEL_INK}
            stroke={LABEL_HALO}
            strokeWidth={strokeWidthForFont(label.fontSize)}
            paintOrder="stroke"
            strokeLinejoin="round"
            style={{
              fontFamily: "var(--font-fraunces), serif",
              fontWeight: LABEL_FONT_WEIGHT,
            }}
          >
            {label.text}
          </text>
        </g>
      ))}
    </svg>
  );
}
