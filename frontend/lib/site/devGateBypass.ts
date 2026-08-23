/** Temporary client-only bypass for the Season 5 dev landing (not a login). */

export const SITE_DEV_GATE_BYPASS_CODE = "TEMP-CODE-4422";

const STORAGE_KEY = "tfmc_site_dev_gate_bypass";

export function isDevGateBypassCode(code: string): boolean {
  return code.trim() === SITE_DEV_GATE_BYPASS_CODE;
}

export function isDevGateBypassActive(): boolean {
  if (typeof sessionStorage === "undefined") {
    return false;
  }
  try {
    return sessionStorage.getItem(STORAGE_KEY) === "1";
  } catch {
    return false;
  }
}

/** Skip the dev landing for this browser tab only; does not create a session. */
export function setDevGateBypass(): void {
  if (typeof sessionStorage === "undefined") {
    return;
  }
  try {
    sessionStorage.setItem(STORAGE_KEY, "1");
  } catch {
    // ignore quota / private mode
  }
}

export function clearDevGateBypass(): void {
  if (typeof sessionStorage === "undefined") {
    return;
  }
  try {
    sessionStorage.removeItem(STORAGE_KEY);
  } catch {
    // ignore
  }
}
