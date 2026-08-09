/** Client-side UI-only bypass for local skins form work (no real API redeem). */
export function isUiDev(): boolean {
  return process.env.NEXT_PUBLIC_UI_DEV === "true";
}
