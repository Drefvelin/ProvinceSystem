"use client";

import { useEffect, useId, useMemo, useRef, useState } from "react";

import { searchWikiIndex, type WikiSearchEntry } from "@/lib/wikiSearch";

type LoadState = "loading" | "ready" | "error";

export default function WikiSearch() {
  const [entries, setEntries] = useState<WikiSearchEntry[]>([]);
  const [loadState, setLoadState] = useState<LoadState>("loading");
  const [query, setQuery] = useState("");
  const [activeIndex, setActiveIndex] = useState(-1);
  const inputRef = useRef<HTMLInputElement>(null);
  const resultRefs = useRef<Array<HTMLAnchorElement | null>>([]);
  const listId = useId();
  const results = useMemo(() => searchWikiIndex(entries, query), [entries, query]);
  const isOpen = query.trim().length > 0;

  useEffect(() => {
    const controller = new AbortController();
    fetch("/wiki/search-index.json", { signal: controller.signal })
      .then((response) => {
        if (!response.ok) throw new Error("Search index unavailable");
        return response.json() as Promise<WikiSearchEntry[]>;
      })
      .then((index) => {
        setEntries(index);
        setLoadState("ready");
      })
      .catch((error: unknown) => {
        if (error instanceof DOMException && error.name === "AbortError") return;
        setLoadState("error");
      });
    return () => controller.abort();
  }, []);

  useEffect(() => {
    setActiveIndex(results.length ? 0 : -1);
  }, [query, results.length]);

  useEffect(() => {
    if (activeIndex >= 0) {
      const activeResult = resultRefs.current[activeIndex];
      if (typeof activeResult?.scrollIntoView === "function") {
        activeResult.scrollIntoView({ block: "nearest" });
      }
    }
  }, [activeIndex]);

  function onKeyDown(event: React.KeyboardEvent<HTMLInputElement>) {
    if (event.key === "Escape") {
      setQuery("");
      setActiveIndex(-1);
      inputRef.current?.focus();
      return;
    }
    if (!results.length) return;
    if (event.key === "ArrowDown" || event.key === "ArrowUp") {
      event.preventDefault();
      const direction = event.key === "ArrowDown" ? 1 : -1;
      setActiveIndex((current) => (current + direction + results.length) % results.length);
    }
    if (event.key === "Enter" && activeIndex >= 0) {
      event.preventDefault();
      resultRefs.current[activeIndex]?.click();
    }
  }

  return (
    <div className="relative mt-3" role="search">
      <label className="sr-only" htmlFor={`${listId}-input`}>Search the gameplay guide</label>
      <input
        ref={inputRef}
        id={`${listId}-input`}
        type="search"
        value={query}
        placeholder="Search the guide"
        autoComplete="off"
        role="combobox"
        aria-autocomplete="list"
        aria-expanded={isOpen}
        aria-controls={isOpen ? listId : undefined}
        aria-activedescendant={activeIndex >= 0 ? `${listId}-${activeIndex}` : undefined}
        onChange={(event) => setQuery(event.target.value)}
        onKeyDown={onKeyDown}
        className="w-full rounded-md border border-[color-mix(in_srgb,var(--tfmc-stone)_45%,transparent)] bg-[var(--tfmc-forest-deep)] px-3 py-2 text-sm text-[var(--tfmc-cream)] outline-none placeholder:text-[var(--tfmc-stone)] focus:border-[var(--tfmc-mist)]"
      />
      {isOpen ? (
        <div className="absolute left-0 z-50 mt-1 max-h-80 w-[min(22rem,calc(100vw-3rem))] overflow-y-auto rounded-md border border-[color-mix(in_srgb,var(--tfmc-stone)_45%,transparent)] bg-[var(--tfmc-forest-deep)] p-1 shadow-xl">
          {loadState === "loading" ? <p className="px-3 py-2 text-sm text-[var(--tfmc-stone)]">Loading search...</p> : null}
          {loadState === "error" ? <p role="status" className="px-3 py-2 text-sm text-[var(--tfmc-stone)]">Search is unavailable right now.</p> : null}
          {loadState === "ready" && !results.length ? <p role="status" className="px-3 py-2 text-sm text-[var(--tfmc-stone)]">No guide results found.</p> : null}
          {loadState === "ready" && results.length ? (
            <ul id={listId} role="listbox" aria-label="Guide search results">
              {results.map((result, index) => (
                <li key={`${result.href}:${result.sectionTitle ?? result.pageTitle}`}>
                  <a
                    ref={(node) => { resultRefs.current[index] = node; }}
                    id={`${listId}-${index}`}
                    role="option"
                    aria-selected={index === activeIndex}
                    href={result.href}
                    onMouseEnter={() => setActiveIndex(index)}
                    className={`block rounded px-3 py-2 ${index === activeIndex ? "bg-[color-mix(in_srgb,var(--tfmc-cream)_10%,transparent)]" : ""}`}
                  >
                    <span className="block text-sm text-[var(--tfmc-cream)]">{result.sectionTitle ?? result.pageTitle}</span>
                    {result.sectionTitle ? <span className="block text-xs text-[var(--tfmc-mist)]">{result.pageTitle}</span> : null}
                    <span className="mt-0.5 block line-clamp-2 text-xs leading-relaxed text-[var(--tfmc-stone)]">{result.snippet}</span>
                  </a>
                </li>
              ))}
            </ul>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
