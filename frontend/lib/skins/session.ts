const STORAGE_KEY = "tfmc_skins_session";

export type SkinsSession = {
  session_token: string;
  player_uuid: string;
  expires_at: string;
  /** True when code scope is skin_staff. */
  staff?: boolean;
  scope?: string;
};

type StoredSession = SkinsSession & {
  last_submission_id?: string;
};

function canUseStorage(): boolean {
  return typeof window !== "undefined" && typeof sessionStorage !== "undefined";
}

function readStored(): StoredSession | null {
  if (!canUseStorage()) return null;
  const raw = sessionStorage.getItem(STORAGE_KEY);
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw) as Partial<StoredSession>;
    if (!parsed.session_token || !parsed.player_uuid || !parsed.expires_at) {
      return null;
    }
    const out: StoredSession = {
      session_token: parsed.session_token,
      player_uuid: parsed.player_uuid,
      expires_at: parsed.expires_at,
    };
    if (parsed.staff === true) {
      out.staff = true;
    }
    if (typeof parsed.scope === "string" && parsed.scope.trim()) {
      out.scope = parsed.scope.trim();
    }
    const lastId =
      typeof parsed.last_submission_id === "string"
        ? parsed.last_submission_id.trim()
        : "";
    if (lastId) {
      out.last_submission_id = lastId;
    }
    return out;
  } catch {
    return null;
  }
}

function writeStored(stored: StoredSession): void {
  if (!canUseStorage()) return;
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(stored));
}

export function getSession(): SkinsSession | null {
  const stored = readStored();
  if (!stored) return null;
  const out: SkinsSession = {
    session_token: stored.session_token,
    player_uuid: stored.player_uuid,
    expires_at: stored.expires_at,
  };
  if (stored.staff) out.staff = true;
  if (stored.scope) out.scope = stored.scope;
  return out;
}

export function getLastSubmissionId(): string | null {
  const stored = readStored();
  const id = stored?.last_submission_id?.trim();
  return id ? id : null;
}

export function setLastSubmissionId(id: string): void {
  const stored = readStored();
  if (!stored) return;
  const trimmed = (id || "").trim();
  if (!trimmed) {
    const { last_submission_id: _, ...rest } = stored;
    writeStored(rest);
    return;
  }
  writeStored({ ...stored, last_submission_id: trimmed });
}

/** New redeem: store session token fields only (no leftover last submission). */
export function setSession(session: SkinsSession): void {
  if (!canUseStorage()) return;
  const stored: StoredSession = {
    session_token: session.session_token,
    player_uuid: session.player_uuid,
    expires_at: session.expires_at,
  };
  if (session.staff) stored.staff = true;
  if (session.scope) stored.scope = session.scope;
  writeStored(stored);
}

/** Wipe token and last submission id. */
export function clearSession(): void {
  if (!canUseStorage()) return;
  sessionStorage.removeItem(STORAGE_KEY);
}

/** True if a session exists and expires_at is still in the future (UTC ISO). */
export function isSessionValid(session: SkinsSession | null = getSession()): boolean {
  if (!session) return false;
  const exp = Date.parse(session.expires_at);
  if (Number.isNaN(exp)) return false;
  return exp > Date.now();
}
