"use client";

import {
  useEffect,
  useRef,
  useState,
  type ReactNode,
  type PointerEvent as ReactPointerEvent,
} from "react";

type DraggablePanelProps = {
  children: ReactNode;
  className?: string;
  /** When set, the dragged position is remembered per-browser (localStorage) across sessions. */
  storageKey?: string;
};

function loadStoredPos(storageKey: string): { x: number; y: number } | null {
  try {
    const raw = window.localStorage.getItem(storageKey);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (typeof parsed?.x === "number" && typeof parsed?.y === "number") return parsed;
  } catch {
    // ignore malformed/unavailable storage
  }
  return null;
}

function clampToViewport(x: number, y: number, width: number, height: number) {
  const margin = 4;
  return {
    x: Math.min(Math.max(margin, x), window.innerWidth - width - margin),
    y: Math.min(Math.max(margin, y), window.innerHeight - height - margin),
  };
}

/**
 * Wraps a floating overlay panel so it can be dragged anywhere on screen.
 * Stays in its default position (via `className`) until first dragged, then
 * switches to viewport-fixed coordinates that follow the pointer, clamped to
 * stay on screen. Clicks on interactive children (select/button/etc.) are
 * left alone so dragging never steals them. With `storageKey`, the dragged
 * position persists in this browser's localStorage across visits.
 */
export default function DraggablePanel({ children, className, storageKey }: DraggablePanelProps) {
  const panelRef = useRef<HTMLDivElement>(null);
  const [pos, setPos] = useState<{ x: number; y: number } | null>(null);
  const drag = useRef<{ dx: number; dy: number; pointerId: number } | null>(null);

  useEffect(() => {
    if (!storageKey) return;
    const stored = loadStoredPos(storageKey);
    if (!stored || !panelRef.current) return;
    const rect = panelRef.current.getBoundingClientRect();
    setPos(clampToViewport(stored.x, stored.y, rect.width, rect.height));
    // Only re-run if the panel identity changes, not on every render.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [storageKey]);

  function persist(next: { x: number; y: number }) {
    if (!storageKey) return;
    try {
      window.localStorage.setItem(storageKey, JSON.stringify(next));
    } catch {
      // ignore write failures (private browsing, storage disabled, etc.)
    }
  }

  function onPointerDown(e: ReactPointerEvent<HTMLDivElement>) {
    const target = e.target as HTMLElement;
    if (target.closest("select, button, a, input, textarea")) return;
    const panel = panelRef.current;
    if (!panel) return;
    const rect = panel.getBoundingClientRect();
    drag.current = { dx: e.clientX - rect.left, dy: e.clientY - rect.top, pointerId: e.pointerId };
    panel.setPointerCapture(e.pointerId);
    e.preventDefault();
  }

  function onPointerMove(e: ReactPointerEvent<HTMLDivElement>) {
    if (!drag.current || drag.current.pointerId !== e.pointerId) return;
    const panel = panelRef.current;
    if (!panel) return;
    const next = clampToViewport(
      e.clientX - drag.current.dx,
      e.clientY - drag.current.dy,
      panel.offsetWidth,
      panel.offsetHeight,
    );
    setPos(next);
  }

  function onPointerUp(e: ReactPointerEvent<HTMLDivElement>) {
    if (drag.current?.pointerId === e.pointerId) {
      panelRef.current?.releasePointerCapture(e.pointerId);
      drag.current = null;
      if (pos) persist(pos);
    }
  }

  return (
    <div
      ref={panelRef}
      className={`${className ?? ""} cursor-move touch-none select-none`}
      style={
        pos
          ? { position: "fixed", left: pos.x, top: pos.y, right: "auto", bottom: "auto", margin: 0 }
          : undefined
      }
      onPointerDown={onPointerDown}
      onPointerMove={onPointerMove}
      onPointerUp={onPointerUp}
      onPointerCancel={onPointerUp}
    >
      {children}
    </div>
  );
}
