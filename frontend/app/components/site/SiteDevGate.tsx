"use client";

import { useSiteStaffAccess } from "@/app/hooks/useSiteStaffAccess";
import { isCharacterUiDev } from "@/lib/characters/uiDev";
import { isSiteDevGateEnabled } from "@/lib/site/config";
import SiteHeader from "../shell/SiteHeader";
import DevLandingPage from "./DevLandingPage";

type Props = {
  children: React.ReactNode;
};

export default function SiteDevGate({ children }: Props) {
  const gateEnabled = isSiteDevGateEnabled() && !isCharacterUiDev();
  const { state, retry } = useSiteStaffAccess({ enabled: gateEnabled });

  if (!gateEnabled) {
    return (
      <>
        <SiteHeader />
        {children}
      </>
    );
  }

  if (state === "staff") {
    return (
      <>
        <SiteHeader />
        {children}
      </>
    );
  }

  return (
    <DevLandingPage
      loading={state === "loading"}
      accessDenied={state === "denied"}
      onStaffVerified={retry}
    />
  );
}
