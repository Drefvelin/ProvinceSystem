import { Suspense } from "react";

import MapEditorPage from "./MapEditorPageClient";

export default function Page() {
  return (
    <div className="overflow-x-hidden">
      <Suspense
        fallback={
          <div className="flex min-h-[calc(100dvh-var(--tfmc-header-h))] items-center justify-center bg-[var(--tfmc-forest-deep)]">
            <p className="text-sm text-[var(--tfmc-stone)]">Loading map editor...</p>
          </div>
        }
      >
        <MapEditorPage />
      </Suspense>
    </div>
  );
}
