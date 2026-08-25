/** Local character UI iteration without redeem/API. */

export function isCharacterUiDev(): boolean {
  return process.env.NEXT_PUBLIC_CHARACTER_UI_DEV === "1";
}

export const UI_DEV_SESSION_TOKEN = "ui-dev-session";
