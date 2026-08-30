import type { ReactNode } from "react";
import DraggablePanel from "./DraggablePanel";

type MapPageLayoutProps = {
  mapDisplayName: string;
  children: ReactNode;
  mapModeSelectorMobile: ReactNode;
  mapModeSelectorDesktop: ReactNode;
  drillStackBar: ReactNode;
  desktopSidePanel: ReactNode;
  headerAction?: ReactNode;
  /** Cover/contain fit-mode switch, rendered inside the Controls legend. */
  fitModeToggle?: ReactNode;
  /** War-planning paint toolbar, floated as its own draggable panel. */
  paintPanel?: ReactNode;
};

const overlayPanelClass =
  "rounded-lg border border-[color-mix(in_srgb,var(--tfmc-cream)_15%,transparent)] bg-[color-mix(in_srgb,var(--tfmc-forest-deep)_92%,transparent)] shadow-xl backdrop-blur-sm";

/**
 * Full-bleed map shell: the map fills the entire area below the global nav,
 * pannable/zoomable edge to edge, with controls floating on top of it instead
 * of sharing page layout with it. Modeled on map viewers like WesterosCraft's
 * Dynmap page — mode selector top-left, nation detail top-right, active-layer
 * breadcrumb bottom-left.
 *
 * `children` (the map itself) is rendered exactly once. Its size comes purely
 * from CSS on the wrapper around it — `aspect-square` on mobile (there's no
 * room to float controls over a map that dense, so the mode selector and
 * title stay in normal document flow above it instead), `flex-1` filling the
 * remaining viewport height on desktop. Rendering the map twice to get
 * different mobile/desktop treatments would double every fetch, canvas
 * layer, and ResizeObserver it owns — only the cheap overlay controls
 * (a dropdown, some text) get a separate mobile/desktop copy.
 */
export default function MapPageLayout({
  mapDisplayName,
  children,
  mapModeSelectorMobile,
  mapModeSelectorDesktop,
  drillStackBar,
  desktopSidePanel,
  headerAction,
  fitModeToggle,
  paintPanel,
}: MapPageLayoutProps) {
  return (
    <div className="flex min-h-[calc(100dvh-var(--tfmc-header-h))] flex-col bg-[var(--tfmc-forest-deep)] text-[var(--tfmc-cream)] md:h-[calc(100dvh-var(--tfmc-header-h))] md:overflow-hidden">
      {/* Mobile-only header + mode bar, normal document flow above the map. */}
      <div className="md:hidden">
        <header className="flex flex-col gap-3 border-b border-[color-mix(in_srgb,var(--tfmc-cream)_10%,transparent)] px-4 py-4 sm:flex-row sm:items-end sm:justify-between sm:px-6">
          <div>
            <p className="text-sm font-medium uppercase tracking-widest text-[var(--tfmc-mist)]">
              World map
            </p>
            <h1 className="font-[family-name:var(--font-fraunces)] text-3xl font-medium tracking-tight text-[var(--tfmc-cream)] sm:text-4xl">
              {mapDisplayName}
            </h1>
          </div>
          {headerAction}
        </header>
        <div className="px-4 py-3 sm:px-6">{mapModeSelectorMobile}</div>
      </div>

      <div className="relative aspect-square w-full min-h-0 md:aspect-auto md:w-auto md:flex-1">
        {children}

        {/* Floating controls: desktop only. On mobile the map's own square
            box has no room to spare for overlays. */}
        <div className="pointer-events-none absolute inset-0 z-10 hidden p-4 md:block">
          <DraggablePanel
            storageKey="tfmc-map-panel-worldmap"
            className="pointer-events-auto absolute left-4 top-4 w-64"
          >
            <div className={`${overlayPanelClass} p-3`}>
              <p className="text-xs font-medium uppercase tracking-widest text-[var(--tfmc-mist)]">
                World map
              </p>
              <h1 className="font-[family-name:var(--font-fraunces)] text-xl font-medium tracking-tight text-[var(--tfmc-cream)]">
                {mapDisplayName}
              </h1>
              {headerAction ? <div className="mt-2">{headerAction}</div> : null}
            </div>
          </DraggablePanel>

          <DraggablePanel
            storageKey="tfmc-map-panel-mapmode"
            className="pointer-events-auto absolute left-4 top-[9.5rem] w-64"
          >
            {mapModeSelectorDesktop}
          </DraggablePanel>

          {paintPanel ? (
            <DraggablePanel
              storageKey="tfmc-map-panel-paint"
              className="pointer-events-auto absolute left-4 top-[13rem] w-64"
            >
              {paintPanel}
            </DraggablePanel>
          ) : null}

          <div className="pointer-events-auto absolute right-4 top-4 w-72 xl:w-80">
            {desktopSidePanel}
          </div>

          <div className="pointer-events-auto absolute bottom-4 left-4 right-4 flex flex-col items-start gap-2">
            {drillStackBar}
            <DraggablePanel storageKey="tfmc-map-panel-controls" className="pointer-events-auto w-fit">
              <div
                className={`${overlayPanelClass} w-fit px-3 py-2 text-xs text-[var(--tfmc-stone)]`}
              >
                <p className="mb-1 font-medium uppercase tracking-wide text-[var(--tfmc-mist)]">
                  Controls
                </p>
                <ul className="space-y-0.5">
                  <li>Scroll to zoom</li>
                  <li>Middle-click + drag to pan</li>
                </ul>
                {fitModeToggle ? (
                  <div className="mt-2 border-t border-[color-mix(in_srgb,var(--tfmc-cream)_12%,transparent)] pt-2">
                    {fitModeToggle}
                  </div>
                ) : null}
              </div>
            </DraggablePanel>
          </div>
        </div>
      </div>

      {/* Mobile: active-layer bar stays in normal document flow below the map. */}
      <div className="px-4 py-4 sm:px-6 md:hidden">{drillStackBar}</div>
    </div>
  );
}
