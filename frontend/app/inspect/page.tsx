"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

import CodeInspector from "@/app/components/site/CodeInspector";
import { useSiteStaffAccess } from "@/app/hooks/useSiteStaffAccess";

export default function InspectPage() {
  const router = useRouter();
  const { state } = useSiteStaffAccess({ enabled: true });

  useEffect(() => {
    if (state === "unauthenticated" || state === "denied") {
      router.replace("/");
    }
  }, [state, router]);

  if (state === "loading") {
    return (
      <main className="mx-auto w-full max-w-md px-6 py-10">
        <p className="text-sm text-[var(--tfmc-mist)]">Checking access…</p>
      </main>
    );
  }

  if (state !== "staff") {
    return null;
  }

  return (
    <main className="mx-auto w-full max-w-md px-6 py-10">
      <h1 className="font-[family-name:var(--font-fraunces)] text-2xl font-medium text-[var(--tfmc-cream)]">
        Token inspector
      </h1>
      <p className="mt-2 text-sm text-[var(--tfmc-stone)]">
        Check scope, entitlements, and staff flags for a minted code before
        redeeming.
      </p>
      <CodeInspector className="mt-8" showHeading={false} />
    </main>
  );
}
