import {
  buildAreaPath,
  buildLinePath,
  buildStepPath,
  diffConsecutive,
  formatMoney,
  formatSignedMoney,
  ledgerCursorReadout,
  niceTicks,
  stackBreakdown,
  wealthShare,
  type StackedBreakdown,
} from "../../lib/map/ledgerSeries";
import type { LedgerFactionOption, MergedLedgerFaction } from "../../lib/map/ledgerSeries";
import type { LedgerSeries } from "../../lib/map/ledgerData";
import { chroniclePanelClass, selectClass } from "./ChroniclePanels";
import { factionForKey, type LedgerChartsResult } from "./useLedgerSeries";

/**
 * The play-stage economy panel: wealth, prestige and income for one focused
 * faction. Three charts only — a territory/population panel was proposed and
 * declined, so this file does not grow a fourth.
 *
 * All chart *geometry* — path building, stacking, tick spacing, money
 * formatting — comes from `ledgerSeries.ts`. Vitest is node-env and only
 * covers `app/**\/*.test.ts`, so anything computed in this component ships
 * with zero test coverage; the only math done here is the linear x/y scale
 * every `ledgerSeries.ts` builder takes as a callback, which has nowhere else
 * to live because it depends on this panel's own pixel dimensions.
 *
 * NEVER wire this panel into the GIF export or the frame layers:
 *  (a) no chart key belongs in `ChronicleToggleKey` / `CHRONICLE_TOGGLE_ORDER`
 *      (`chronicleLayers.ts`) — those feed the compose stage and the build's
 *      `imageFingerprint`, so a chart toggle would force a full repaint of
 *      every frame for a panel that never touches a frame's pixels.
 *  (b) no chart data belongs in `ChronicleFrameLayers` — `chronicleGifExport.ts`
 *      redraws a GIF purely from `frame.image` + `frame.layers`, never the DOM,
 *      so this panel is structurally invisible to the export already. Keep it
 *      that way; do not go looking for a way to "include" it.
 */

const CHART_WIDTH = 300;
const CHART_HEIGHT = 120;
const MARGIN = { top: 8, right: 8, bottom: 16, left: 34 };
const INNER_WIDTH = CHART_WIDTH - MARGIN.left - MARGIN.right;
const INNER_HEIGHT = CHART_HEIGHT - MARGIN.top - MARGIN.bottom;

/** A small fixed palette drawn from the studio's own tokens, cycled by index —
 * breakdown keys are arbitrary server strings, so there is no fixed mapping. */
const BAND_COLORS = [
  "color-mix(in srgb, var(--tfmc-accent) 65%, transparent)",
  "color-mix(in srgb, var(--tfmc-moss) 80%, transparent)",
  "color-mix(in srgb, var(--tfmc-mist) 55%, transparent)",
  "color-mix(in srgb, var(--tfmc-stone) 45%, transparent)",
  "color-mix(in srgb, var(--tfmc-cream) 30%, transparent)",
];

const headingClass =
  "text-xs font-medium uppercase tracking-widest text-[var(--tfmc-mist)]";

function SectionHeading({ title }: { title: string }) {
  return <p className={headingClass}>{title}</p>;
}

/**
 * A card's title plus its own nation dropdown — one entry per exact registry
 * name for the built range, deleted nations included and a reused id's two
 * lifetimes already merged into a single entry under their shared name (see
 * `buildLedgerFactionOptions`). Stacked under the title rather than beside it
 * so a long nation name never pushes the card wider than the rail it lives in
 * (`w-72`, matching the left rail) — `selectClass` is already `w-full`, so
 * the dropdown fills the card instead of overflowing it, and the browser's
 * own `<option>` rendering wraps/truncates long labels rather than this
 * component measuring text.
 */
function CardHeader({
  title,
  options,
  selectedKey,
  onSelect,
}: {
  title: string;
  options: LedgerFactionOption[];
  selectedKey: string;
  onSelect: (key: string) => void;
}) {
  return (
    <div>
      <SectionHeading title={title} />
      <select
        className={`${selectClass} mt-1`}
        value={selectedKey}
        onChange={(event) => onSelect(event.target.value)}
        aria-label={`${title} nation`}
      >
        {options.map((option) => (
          <option key={option.name} value={option.name} title={option.label}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  );
}

/** Linear x scale over a day index — the one piece of scaling every builder
 * in `ledgerSeries.ts` takes as a parameter rather than assumes. */
function makeXScale(dayCount: number) {
  return (index: number): number => {
    if (dayCount <= 1) return MARGIN.left + INNER_WIDTH / 2;
    return MARGIN.left + (index / (dayCount - 1)) * INNER_WIDTH;
  };
}

/** Linear y scale over `[min, max]`, guarded against a zero-span domain.
 * `marginTop`/`innerHeight` default to the main chart's own dimensions, but
 * take an override so a secondary strip (its own axis, its own domain) can
 * reuse the same scaling logic at a different vertical extent. */
function makeYScale(
  min: number,
  max: number,
  marginTop: number = MARGIN.top,
  innerHeight: number = INNER_HEIGHT
) {
  const span = max - min || 1;
  return (value: number): number =>
    marginTop + innerHeight - ((value - min) / span) * innerHeight;
}

/** Widest finite value across any number of `number | null` arrays, or 0. */
function maxOf(...series: Array<Array<number | null>>): number {
  let max = 0;
  for (const values of series) {
    for (const v of values) {
      if (v != null && Number.isFinite(v) && v > max) max = v;
    }
  }
  return max;
}

function minOf(...series: Array<Array<number | null>>): number {
  let min = 0;
  for (const values of series) {
    for (const v of values) {
      if (v != null && Number.isFinite(v) && v < min) min = v;
    }
  }
  return min;
}

/**
 * The day index the playhead sits on, or `null` when today's exact day has no
 * ledger row. Deliberately an exact match only: the ledger genuinely has a
 * gap on days with no row, and snapping the dashed cursor to the closest
 * earlier day would draw it on a day the playhead isn't actually on —
 * dishonest geometry, so the cursor (and its readout line) simply stays
 * hidden on a gap day instead.
 * Not "geometry" in the chart sense — this is a lookup into the shared
 * `days[]` axis, the same job `sliceToRange` does for a range endpoint.
 */
function cursorIndex(days: string[], day: string | null): number | null {
  if (!day) return null;
  const index = days.indexOf(day);
  return index === -1 ? null : index;
}

function AxisLabels({
  ticks,
  yScale,
}: {
  ticks: number[];
  yScale: (v: number) => number;
}) {
  return (
    <>
      {ticks.map((tick) => (
        <g key={tick}>
          <line
            x1={MARGIN.left}
            x2={CHART_WIDTH - MARGIN.right}
            y1={yScale(tick)}
            y2={yScale(tick)}
            stroke="color-mix(in srgb, var(--tfmc-cream) 10%, transparent)"
            strokeWidth={1}
          />
          <text
            x={MARGIN.left - 4}
            y={yScale(tick)}
            textAnchor="end"
            dominantBaseline="middle"
            fontSize={8}
            fill="var(--tfmc-stone)"
          >
            {formatMoney(tick)}
          </text>
        </g>
      ))}
    </>
  );
}

function Cursor({
  index,
  xScale,
  top = MARGIN.top,
  bottom = CHART_HEIGHT - MARGIN.bottom,
}: {
  index: number | null;
  xScale: (i: number) => number;
  /** Vertical extent, overridable so a secondary strip's shorter cursor line
   * doesn't stretch into the main chart above it. */
  top?: number;
  bottom?: number;
}) {
  if (index == null) return null;
  const x = xScale(index);
  return (
    <line
      x1={x}
      x2={x}
      y1={top}
      y2={bottom}
      stroke="var(--tfmc-cream)"
      strokeWidth={1}
      strokeDasharray="2 2"
      opacity={0.6}
    />
  );
}

function StackedBands({
  stacked,
  dayCount,
  xScale,
  yScale,
}: {
  stacked: StackedBreakdown;
  dayCount: number;
  xScale: (i: number) => number;
  yScale: (v: number) => number;
}) {
  return (
    <>
      {stacked.keys.map((key, keyIndex) => {
        const tops: Array<number | null> = [];
        const baselines: Array<number | null> = [];
        for (let day = 0; day < dayCount; day++) {
          // No `?? 0` fallback here: `stacked.tops`/`baselines` already carry
          // an explicit `null` for a day the faction has no row at all
          // (see `stackBreakdown`), and re-filling it to 0 here would redraw
          // that gap as a dip to zero instead of a break in `buildAreaPath`.
          tops.push(stacked.tops[day]?.[keyIndex] ?? null);
          baselines.push(stacked.baselines[day]?.[keyIndex] ?? null);
        }
        const d = buildAreaPath(tops, baselines, xScale, yScale);
        if (!d) return null;
        return (
          <path
            key={key}
            d={d}
            fill={BAND_COLORS[keyIndex % BAND_COLORS.length]}
            stroke="none"
          />
        );
      })}
    </>
  );
}

/** Height/margins for the secondary server-wide-globals strip under the main
 * wealth chart — its own axis, its own y-domain, orders of magnitude apart
 * from a single faction's wealth on any real map. Sharing one y-domain with
 * the faction stack (the original layout) flattened the faction series onto
 * the axis; this keeps both readable without ever summing them. */
const GLOBALS_STRIP_HEIGHT = 56;
const GLOBALS_STRIP_MARGIN_TOP = 6;
const GLOBALS_STRIP_MARGIN_BOTTOM = 14;
const GLOBALS_STRIP_INNER_HEIGHT =
  GLOBALS_STRIP_HEIGHT - GLOBALS_STRIP_MARGIN_TOP - GLOBALS_STRIP_MARGIN_BOTTOM;

/** Every card's own nation-selection state, threaded from the hook down
 * through the panel to each chart — independent per card, so picking a
 * lifetime in one never touches the other two. */
type CardSelectProps = {
  options: LedgerFactionOption[];
  selectedKey: string;
  onSelect: (key: string) => void;
  /** The shared union fetch's own state, not this card's — a card whose key
   * is present in an already-loaded `series` renders normally even while a
   * different card's newly-picked key is still loading. */
  seriesLoading: boolean;
  seriesError: string | null;
};

/** The body shown in place of a chart when this card's selection has no data
 * yet — the union fetch is loading, failed, or (a selection whose range
 * genuinely has no rows) simply came back without this key. */
function CardStatusMessage({ seriesLoading, seriesError }: Omit<CardSelectProps, "options" | "selectedKey" | "onSelect">) {
  if (seriesError) {
    return <p className="mt-2 text-xs text-[var(--tfmc-accent)]">{seriesError}</p>;
  }
  return (
    <p className="mt-2 text-xs leading-snug text-[var(--tfmc-stone)]">
      {seriesLoading
        ? "Loading the ledger…"
        : "The selected nation has no ledger history in this range."}
    </p>
  );
}

/** Wealth: `wealth_breakdown` stacked area on its own axis, plus the two
 * global money-supply lines on a separate strip with its own axis below —
 * the invariant this panel exists to enforce is that those two numbers are
 * never summed into the faction's own wealth, and a shared y-domain made the
 * faction stack unreadable next to server-wide totals on any real map. */
function WealthChart({
  series,
  faction,
  cursorDay,
  options,
  selectedKey,
  onSelect,
  seriesLoading,
  seriesError,
}: {
  series: LedgerSeries | null;
  faction: MergedLedgerFaction | null;
  cursorDay: string | null;
} & CardSelectProps) {
  if (!series || !faction) {
    return (
      <div className={`${chroniclePanelClass} p-3`}>
        <CardHeader title="Wealth" options={options} selectedKey={selectedKey} onSelect={onSelect} />
        <CardStatusMessage seriesLoading={seriesLoading} seriesError={seriesError} />
      </div>
    );
  }

  const dayCount = series.days.length;
  const stacked = stackBreakdown(faction.breakdowns.wealth, dayCount);
  const pouch = series.global.pouch_wealth ?? [];
  const bank = series.global.player_bank_wealth ?? [];
  const wealth = faction.series.wealth ?? [];

  const topTotals = stacked.tops.map((row) => row[row.length - 1] ?? 0);
  const max = Math.max(maxOf(topTotals, wealth), 1);
  const ticks = niceTicks(0, max, 4);
  const xScale = makeXScale(dayCount);
  const yScale = makeYScale(0, ticks[ticks.length - 1] ?? max);
  const cursor = cursorIndex(series.days, cursorDay);
  const readout = ledgerCursorReadout(cursorDay, cursor, wealth);

  const globalsMax = Math.max(maxOf(pouch, bank), 1);
  const globalsTicks = niceTicks(0, globalsMax, 3);
  const globalsYScale = makeYScale(
    0,
    globalsTicks[globalsTicks.length - 1] ?? globalsMax,
    GLOBALS_STRIP_MARGIN_TOP,
    GLOBALS_STRIP_INNER_HEIGHT
  );
  const pouchPath = buildLinePath(pouch, xScale, globalsYScale);
  const bankPath = buildLinePath(bank, xScale, globalsYScale);

  return (
    <div className={`${chroniclePanelClass} p-3`}>
      <CardHeader title="Wealth" options={options} selectedKey={selectedKey} onSelect={onSelect} />
      <svg viewBox={`0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`} className="mt-2 w-full">
        <AxisLabels ticks={ticks} yScale={yScale} />
        <StackedBands stacked={stacked} dayCount={dayCount} xScale={xScale} yScale={yScale} />
        <Cursor index={cursor} xScale={xScale} />
      </svg>
      <div className="mt-1 flex flex-wrap gap-x-3 gap-y-1 text-[10px] text-[var(--tfmc-stone)]">
        {stacked.keys.map((key, i) => (
          <span key={key} className="inline-flex items-center gap-1">
            <span
              className="h-2 w-2 rounded-sm"
              style={{ background: BAND_COLORS[i % BAND_COLORS.length] }}
            />
            {key}
          </span>
        ))}
      </div>
      <p className="mt-2 text-xs leading-snug text-[var(--tfmc-stone)]">
        Server-wide money supply. It is <strong>not part of this faction&rsquo;s
        wealth</strong>, never summed with the stack above. Shown on its own
        axis below since it runs orders of magnitude larger.
      </p>
      <svg
        viewBox={`0 0 ${CHART_WIDTH} ${GLOBALS_STRIP_HEIGHT}`}
        className="mt-1 w-full"
      >
        <AxisLabels ticks={globalsTicks} yScale={globalsYScale} />
        {pouchPath ? (
          <path
            d={pouchPath}
            fill="none"
            stroke="var(--tfmc-mist)"
            strokeWidth={1.5}
            strokeDasharray="4 2"
          />
        ) : null}
        {bankPath ? (
          <path
            d={bankPath}
            fill="none"
            stroke="var(--tfmc-cream)"
            strokeWidth={1.5}
            strokeDasharray="1 2"
          />
        ) : null}
        <Cursor
          index={cursor}
          xScale={xScale}
          top={GLOBALS_STRIP_MARGIN_TOP}
          bottom={GLOBALS_STRIP_HEIGHT - GLOBALS_STRIP_MARGIN_BOTTOM}
        />
      </svg>
      <p className="mt-1 flex flex-wrap gap-x-3 gap-y-1 text-[10px] text-[var(--tfmc-stone)]">
        <span className="inline-flex items-center gap-1">
          <span className="inline-block h-0 w-3 border-t border-dashed border-[var(--tfmc-mist)]" />
          server pouch wealth
        </span>
        <span className="inline-flex items-center gap-1">
          <span className="inline-block h-0 w-3 border-t border-dotted border-[var(--tfmc-cream)]" />
          player bank wealth
        </span>
      </p>
      {readout ? (
        <p
          className={`mt-1 text-xs ${
            readout.hasData ? "text-[var(--tfmc-cream)]" : "text-[var(--tfmc-stone)]"
          }`}
        >
          {readout.hasData && cursor != null ? (
            <>
              {readout.day}: {formatMoney(wealth[cursor] ?? null)} faction wealth
            </>
          ) : (
            <>{readout.day}: no data</>
          )}
        </p>
      ) : null}
    </div>
  );
}

/** Prestige: line + `prestige_breakdown` stack, plus the real promotion/
 * demotion thresholds from this faction's own per-day `rank_up_at` /
 * `rank_down_at` — never `ranks.yml` or any fixed table. Drawn as steps
 * (`buildStepPath`, from `ledgerSeries.ts`) because each is a per-day
 * threshold that holds flat until the server recomputes it — a straight
 * line between two days would imply a threshold that "moves" continuously,
 * which it doesn't. A `null` day (rank has no next tier on that side, e.g.
 * already at the top or bottom rank) breaks the step rather than
 * interpolating across it. Rank-change ticks stay as a thin bottom-axis
 * mark — with the two threshold lines already on the chart they'd be
 * redundant as full-height bars, so they're kept minimal. The wealth-share
 * readout below the chart divides this faction's wealth by the server-wide
 * `global.faction_wealth` pool: the Wealth component of prestige is a share
 * of that pool, not an absolute amount, so this faction's prestige can drop
 * even while its own finances hold steady, purely because rivals grew
 * theirs faster. */
function PrestigeChart({
  series,
  faction,
  cursorDay,
  options,
  selectedKey,
  onSelect,
  seriesLoading,
  seriesError,
}: {
  series: LedgerSeries | null;
  faction: MergedLedgerFaction | null;
  cursorDay: string | null;
} & CardSelectProps) {
  if (!series || !faction) {
    return (
      <div className={`${chroniclePanelClass} p-3`}>
        <CardHeader title="Prestige" options={options} selectedKey={selectedKey} onSelect={onSelect} />
        <CardStatusMessage seriesLoading={seriesLoading} seriesError={seriesError} />
      </div>
    );
  }

  const dayCount = series.days.length;
  const stacked = stackBreakdown(faction.breakdowns.prestige, dayCount);
  const prestige = faction.series.prestige ?? [];
  const rankUpAt = faction.series.rank_up_at ?? [];
  const rankDownAt = faction.series.rank_down_at ?? [];
  const topTotals = stacked.tops.map((row) => row[row.length - 1] ?? 0);
  const max = Math.max(maxOf(topTotals, prestige, rankUpAt, rankDownAt), 1);
  const min = Math.min(minOf(topTotals, prestige, rankUpAt, rankDownAt), 0);
  const ticks = niceTicks(min, max, 4);
  const xScale = makeXScale(dayCount);
  const yScale = makeYScale(
    ticks[0] ?? min,
    ticks[ticks.length - 1] ?? max
  );
  const cursor = cursorIndex(series.days, cursorDay);
  const readout = ledgerCursorReadout(cursorDay, cursor, faction.series.wealth ?? []);
  const linePath = buildLinePath(prestige, xScale, yScale);
  const rankUpPath = buildStepPath(rankUpAt, xScale, yScale);
  const rankDownPath = buildStepPath(rankDownAt, xScale, yScale);

  const rankChanges: number[] = [];
  for (let i = 1; i < faction.rank.length; i++) {
    if (faction.rank[i] != null && faction.rank[i] !== faction.rank[i - 1]) {
      rankChanges.push(i);
    }
  }

  const wealthPool = series.global.faction_wealth ?? [];
  const share =
    cursor != null
      ? wealthShare(faction.series.wealth?.[cursor] ?? null, wealthPool[cursor] ?? null)
      : null;

  return (
    <div className={`${chroniclePanelClass} p-3`}>
      <CardHeader title="Prestige" options={options} selectedKey={selectedKey} onSelect={onSelect} />
      <svg viewBox={`0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`} className="mt-2 w-full">
        <AxisLabels ticks={ticks} yScale={yScale} />
        <StackedBands stacked={stacked} dayCount={dayCount} xScale={xScale} yScale={yScale} />
        {rankUpPath ? (
          <path
            d={rankUpPath}
            fill="none"
            stroke="var(--tfmc-moss)"
            strokeWidth={1.25}
            strokeDasharray="3 2"
          />
        ) : null}
        {rankDownPath ? (
          <path
            d={rankDownPath}
            fill="none"
            stroke="color-mix(in srgb, var(--tfmc-cream) 55%, transparent)"
            strokeWidth={1.25}
            strokeDasharray="3 2"
          />
        ) : null}
        {linePath ? (
          <path d={linePath} fill="none" stroke="var(--tfmc-accent)" strokeWidth={2} />
        ) : null}
        {rankChanges.map((i) => (
          <line
            key={i}
            x1={xScale(i)}
            x2={xScale(i)}
            y1={CHART_HEIGHT - MARGIN.bottom}
            y2={CHART_HEIGHT - MARGIN.bottom - 4}
            stroke="var(--tfmc-cream)"
            strokeWidth={1.5}
            opacity={0.7}
          />
        ))}
        <Cursor index={cursor} xScale={xScale} />
      </svg>
      <p className="mt-2 flex flex-wrap gap-x-3 gap-y-1 text-[10px] text-[var(--tfmc-stone)]">
        <span className="inline-flex items-center gap-1">
          <span className="inline-block h-0 w-3 border-t-2 border-[var(--tfmc-accent)]" />
          prestige
        </span>
        <span className="inline-flex items-center gap-1">
          <span className="inline-block h-0 w-3 border-t border-dashed border-[var(--tfmc-moss)]" />
          promotion threshold
        </span>
        <span className="inline-flex items-center gap-1">
          <span className="inline-block h-0 w-3 border-t border-dashed border-[var(--tfmc-cream)]" />
          demotion threshold
        </span>
      </p>
      {readout ? (
        <p
          className={`mt-1 text-xs ${
            readout.hasData ? "text-[var(--tfmc-cream)]" : "text-[var(--tfmc-stone)]"
          }`}
        >
          {readout.hasData && cursor != null ? (
            <>
              {readout.day}: <strong>{faction.rank[cursor] ?? "unranked"}</strong>. Wealth is{" "}
              {share == null ? "—" : `${(share * 100).toFixed(1)}%`} of the server&rsquo;s
              faction wealth pool.
            </>
          ) : (
            <>{readout.day}: no data</>
          )}
        </p>
      ) : null}
    </div>
  );
}

/** Income: `net_income` / `inflation_delta` (this faction) + `guild_income`
 * (server-wide) are full-day projections from the game, kept visually
 * separate from `diffConsecutive(wealth)` — `wealth[today] - wealth[yesterday]`,
 * computed client-side. The two are different quantities (a full-day
 * projection vs. a client-computed observed change) and must never be
 * blended, summed, or overlaid into one series. */
function IncomeChart({
  series,
  faction,
  cursorDay,
  options,
  selectedKey,
  onSelect,
  seriesLoading,
  seriesError,
}: {
  series: LedgerSeries | null;
  faction: MergedLedgerFaction | null;
  cursorDay: string | null;
} & CardSelectProps) {
  if (!series || !faction) {
    return (
      <div className={`${chroniclePanelClass} p-3`}>
        <CardHeader title="Income" options={options} selectedKey={selectedKey} onSelect={onSelect} />
        <CardStatusMessage seriesLoading={seriesLoading} seriesError={seriesError} />
      </div>
    );
  }

  const dayCount = series.days.length;
  const netIncome = faction.series.net_income ?? [];
  const inflationDelta = faction.series.inflation_delta ?? [];
  const guildIncome = series.global.guild_income ?? [];
  const observedDelta = diffConsecutive(series.days, faction.series.wealth ?? []);

  const max = maxOf(netIncome, inflationDelta, guildIncome, observedDelta);
  const min = minOf(netIncome, inflationDelta, guildIncome, observedDelta);
  const ticks = niceTicks(min, max, 4);
  const xScale = makeXScale(dayCount);
  const yScale = makeYScale(ticks[0] ?? min, ticks[ticks.length - 1] ?? max);
  const cursor = cursorIndex(series.days, cursorDay);
  const readout = ledgerCursorReadout(cursorDay, cursor, faction.series.wealth ?? []);
  const zeroY = yScale(0);

  const netPath = buildLinePath(netIncome, xScale, yScale);
  const inflationPath = buildLinePath(inflationDelta, xScale, yScale);
  const guildPath = buildLinePath(guildIncome, xScale, yScale);

  return (
    <div className={`${chroniclePanelClass} p-3`}>
      <CardHeader title="Income" options={options} selectedKey={selectedKey} onSelect={onSelect} />
      <p className="mt-1 text-xs text-[var(--tfmc-mist)]">Projections</p>
      <svg viewBox={`0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`} className="mt-1 w-full">
        <AxisLabels ticks={ticks} yScale={yScale} />
        <line
          x1={MARGIN.left}
          x2={CHART_WIDTH - MARGIN.right}
          y1={zeroY}
          y2={zeroY}
          stroke="var(--tfmc-stone)"
          strokeWidth={1}
        />
        {netPath ? (
          <path d={netPath} fill="none" stroke="var(--tfmc-cream)" strokeWidth={2} />
        ) : null}
        {inflationPath ? (
          <path
            d={inflationPath}
            fill="none"
            stroke="var(--tfmc-accent)"
            strokeWidth={1.5}
            strokeDasharray="8 3 2 3"
          />
        ) : null}
        {guildPath ? (
          <path
            d={guildPath}
            fill="none"
            stroke="var(--tfmc-stone)"
            strokeWidth={1.5}
            strokeDasharray="1 4"
          />
        ) : null}
        <Cursor index={cursor} xScale={xScale} />
      </svg>
      <p className="mt-1 text-xs leading-snug text-[var(--tfmc-stone)]">
        <span className="text-[var(--tfmc-cream)]">—</span> net income,{" "}
        <span className="text-[var(--tfmc-accent)]">— · —</span> inflation delta
        (this faction), <span className="text-[var(--tfmc-stone)]">· · ·</span>{" "}
        guild income (server-wide)
      </p>
      {readout ? (
        <p
          className={`mt-1 text-xs ${
            readout.hasData ? "text-[var(--tfmc-cream)]" : "text-[var(--tfmc-stone)]"
          }`}
        >
          {readout.hasData && cursor != null ? (
            <>
              {readout.day}: Net Income: {formatSignedMoney(netIncome[cursor] ?? null)} denar
            </>
          ) : (
            <>{readout.day}: no data</>
          )}
        </p>
      ) : null}
      <div className="mt-2 border-t border-[color-mix(in_srgb,var(--tfmc-cream)_12%,transparent)] pt-2">
        <p className="text-xs text-[var(--tfmc-stone)]">
          Observed change
        </p>
        <svg viewBox={`0 0 ${CHART_WIDTH} 36`} className="mt-1 w-full">
          {(() => {
            const barMax = Math.max(
              maxOf(observedDelta.map((v) => Math.abs(v ?? 0))),
              1
            );
            const half = 18;
            return observedDelta.map((value, i) => {
              if (value == null) return null;
              const h = (Math.abs(value) / barMax) * (half - 2);
              const x = xScale(i);
              const y = value >= 0 ? half - h : half;
              return (
                <rect
                  key={i}
                  x={x - 1}
                  y={y}
                  width={2}
                  height={Math.max(h, 0.5)}
                  fill={
                    value >= 0
                      ? "var(--tfmc-accent)"
                      : "color-mix(in srgb, var(--tfmc-cream) 40%, transparent)"
                  }
                />
              );
            });
          })()}
          <line
            x1={0}
            x2={CHART_WIDTH}
            y1={18}
            y2={18}
            stroke="color-mix(in srgb, var(--tfmc-cream) 15%, transparent)"
            strokeWidth={1}
          />
        </svg>
        <p className="mt-1 text-xs leading-snug text-[var(--tfmc-stone)]">
          <strong className="block">wealth[today] - wealth[yesterday]</strong>
          Different quantity from the projections above (an observed result
          vs. a forecast). Blank on any day the ledger has a gap
        </p>
      </div>
    </div>
  );
}

export default function LedgerChartsPanel({
  result,
  cursorDay,
}: {
  result: LedgerChartsResult;
  /** `frames[playIndex].day` — the day the playhead is on right now. */
  cursorDay: string | null;
}) {
  if (result.status === "idle") return null;

  if (result.status === "loading") {
    return (
      <div className={`${chroniclePanelClass} p-3`}>
        <SectionHeading title="Ledger" />
        <p className="mt-2 text-xs text-[var(--tfmc-stone)]">
          Loading the ledger…
        </p>
      </div>
    );
  }

  if (result.status === "empty") {
    return (
      <div className={`${chroniclePanelClass} p-3`}>
        <SectionHeading title="Ledger" />
        <p className="mt-2 text-xs leading-snug text-[var(--tfmc-stone)]">
          No economy data has been captured for this map yet — a fresh season,
          or SimpleFactions has not started posting snapshots here.
        </p>
      </div>
    );
  }

  if (result.status === "no-options") {
    return (
      <div className={`${chroniclePanelClass} p-3`}>
        <SectionHeading title="Ledger" />
        <p className="mt-2 text-xs leading-snug text-[var(--tfmc-stone)]">
          No nations are recorded in the ledger for this range.
        </p>
      </div>
    );
  }

  if (result.status === "error") {
    return (
      <div className={`${chroniclePanelClass} p-3`}>
        <SectionHeading title="Ledger" />
        <p className="mt-2 text-xs text-[var(--tfmc-accent)]">
          {result.message}
        </p>
      </div>
    );
  }

  const { options, selections, onSelect, series, seriesLoading, seriesError } = result;
  const cardProps = { options, seriesLoading, seriesError };
  return (
    <>
      <WealthChart
        {...cardProps}
        series={series}
        faction={factionForKey(series, options, selections.wealth)}
        cursorDay={cursorDay}
        selectedKey={selections.wealth}
        onSelect={(key) => onSelect("wealth", key)}
      />
      <PrestigeChart
        {...cardProps}
        series={series}
        faction={factionForKey(series, options, selections.prestige)}
        cursorDay={cursorDay}
        selectedKey={selections.prestige}
        onSelect={(key) => onSelect("prestige", key)}
      />
      <IncomeChart
        {...cardProps}
        series={series}
        faction={factionForKey(series, options, selections.income)}
        cursorDay={cursorDay}
        selectedKey={selections.income}
        onSelect={(key) => onSelect("income", key)}
      />
    </>
  );
}
