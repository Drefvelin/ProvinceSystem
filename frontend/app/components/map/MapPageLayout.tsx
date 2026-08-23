import type { ReactNode } from "react";

type MapPageLayoutProps = {
  mapDisplayName: string;
  children: ReactNode;
  mapModeSelector: ReactNode;
  drillStackBar: ReactNode;
  desktopSidePanel: ReactNode;
  headerAction?: ReactNode;
};

export default function MapPageLayout({
  mapDisplayName,
  children,
  mapModeSelector,
  drillStackBar,
  desktopSidePanel,
  headerAction,
}: MapPageLayoutProps) {
  return (
    <div className="relative min-h-[calc(100dvh-var(--tfmc-header-h))] text-[var(--tfmc-cream)]">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0"
        style={{
          background: `
            radial-gradient(ellipse 80% 50% at 50% 0%, color-mix(in srgb, var(--tfmc-moss) 45%, transparent), transparent 65%),
            radial-gradient(ellipse 100% 80% at 50% 100%, color-mix(in srgb, var(--tfmc-forest) 85%, #000), transparent),
            linear-gradient(165deg, var(--tfmc-forest-deep) 0%, var(--tfmc-forest) 50%, #152820 100%)
          `,
        }}
      />
      <div className="relative z-10 mx-auto flex max-w-[90rem] flex-col gap-4 px-4 py-6 sm:px-6 md:flex-row md:items-start md:gap-8 md:py-8">
        <div className="min-w-0 flex-1">
          <header className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
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
          <div className="mb-4">{mapModeSelector}</div>
          {children}
          <div className="mt-4">{drillStackBar}</div>
        </div>
        <aside className="hidden w-full shrink-0 space-y-4 md:block md:w-72 xl:w-80">
          {desktopSidePanel}
        </aside>
      </div>
    </div>
  );
}
