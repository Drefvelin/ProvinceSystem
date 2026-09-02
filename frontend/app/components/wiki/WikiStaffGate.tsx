"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { useSiteStaffAccess } from "@/app/hooks/useSiteStaffAccess";

type Props = {
  children: React.ReactNode;
};

export default function WikiStaffGate({ children }: Props) {
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

  return children;
}
