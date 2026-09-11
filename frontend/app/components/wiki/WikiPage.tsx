import type { ReactNode } from "react";

import { cx, wikiBodyText, wikiDisplayFont } from "./wikiStyles";

/** Reading width of the page body. Prose pages are `md`; table/grid-heavy pages are `lg`. */
export type WikiPageWidth = "sm" | "md" | "lg";

export interface WikiPageProps {
  /** The `<h1>`. Should match the page's `WikiNavItem.label`. */
  title: ReactNode;
  /** One or two sentences under the title. Inline markup (code, links) is fine. */
  intro?: ReactNode;
  /**
   * When the content was last checked against the live server, e.g. `"2026-09-01"`
   * or `"Season 5, week 3"`. Rendered as a quiet note under the intro.
   */
  lastVerified?: ReactNode;
  /** `sm` = 2xl, `md` = 3xl (default), `lg` = 4xl. */
  width?: WikiPageWidth;
  children?: ReactNode;
}

const WIDTHS: Record<WikiPageWidth, string> = {
  sm: "max-w-2xl",
  md: "max-w-3xl",
  lg: "max-w-4xl",
};

/**
 * The standard wiki page frame: `<article>` + `<h1>` + optional intro and
 * "last modified" note. Every `/wiki/*` page body should start here so titles,
 * spacing and reading width stay identical across ~40 pages.
 */
export default function WikiPage({
  title,
  intro,
  lastVerified,
  width = "md",
  children,
}: WikiPageProps) {
  return (
    <article className={WIDTHS[width]}>
      <h1 className={cx(wikiDisplayFont, "text-3xl text-[var(--tfmc-cream)] sm:text-4xl")}>
        {title}
      </h1>
      {intro ? <p className={cx("mt-2", wikiBodyText)}>{intro}</p>: null}
      {lastVerified ? (
        <p className="mt-2 text-xs text-[var(--tfmc-stone)]">Last modified: {lastVerified}</p>
      ): null}
      {children}
    </article>
  );
}
