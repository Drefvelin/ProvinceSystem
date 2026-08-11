/** Characters API client (creation catalog, redeem, list, create). */

export function getApiBase(): string {
  const base = (process.env.NEXT_PUBLIC_API_URL || "").trim().replace(/\/$/, "");
  if (!base) {
    throw new Error("NEXT_PUBLIC_API_URL is not set");
  }
  return base;
}

export class CharactersApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "CharactersApiError";
    this.status = status;
  }
}

function detailMessage(data: unknown, fallback: string): string {
  if (data && typeof data === "object" && "detail" in data) {
    const detail = (data as { detail: unknown }).detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) {
      return detail
        .map((item) =>
          typeof item === "object" && item && "msg" in item
            ? String((item as { msg: unknown }).msg)
            : String(item)
        )
        .join("; ");
    }
  }
  return fallback;
}

async function parseJson(res: Response): Promise<unknown> {
  try {
    return await res.json();
  } catch {
    return null;
  }
}

async function apiFetch(input: string, init?: RequestInit): Promise<Response> {
  try {
    return await fetch(input, init);
  } catch {
    throw new Error("Request failed. Please try again.");
  }
}

function authHeaders(token: string): HeadersInit {
  return {
    Authorization: `Bearer ${token}`,
    Accept: "application/json",
  };
}

export type RedeemResult = {
  session_token: string;
  player_uuid: string;
  expires_at: string;
  scope?: string;
  remember_me?: boolean;
};

export async function redeemCharacter(
  code: string,
  rememberMe = false
): Promise<RedeemResult> {
  const res = await apiFetch(`${getApiBase()}/skins/character/redeem`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      code: code.trim(),
      remember_me: rememberMe,
    }),
  });
  const data = await parseJson(res);
  if (!res.ok) {
    throw new CharactersApiError(
      detailMessage(data, `Redeem failed (${res.status})`),
      res.status
    );
  }
  const body = data as Partial<RedeemResult>;
  if (!body.session_token || !body.player_uuid || !body.expires_at) {
    throw new CharactersApiError("Invalid redeem response from API", res.status);
  }
  return {
    session_token: body.session_token,
    player_uuid: body.player_uuid,
    expires_at: body.expires_at,
    scope: typeof body.scope === "string" ? body.scope : "character",
    remember_me: body.remember_me === true || rememberMe,
  };
}

export async function logoutCharacter(sessionToken: string): Promise<void> {
  const res = await apiFetch(`${getApiBase()}/characters/logout`, {
    method: "POST",
    headers: authHeaders(sessionToken),
  });
  if (!res.ok && res.status !== 401) {
    const data = await parseJson(res);
    throw new CharactersApiError(
      detailMessage(data, `Logout failed (${res.status})`),
      res.status
    );
  }
}

export type CreationCatalog = {
  stages: CatalogStage[];
  attribute_point_buy: AttributePointBuy | null;
  races: CatalogIdRow[];
  traits: CatalogTrait[];
  classes: CatalogIdRow[];
  validation: CatalogValidation;
  slot_limits: SlotLimits;
  updated_at: string | null;
};

export type CatalogStage = {
  id: string;
  type: string;
  order?: number;
  target?: string;
  key?: string;
  min_select?: number;
  max_select?: number;
  points?: number;
  max_rank?: number;
  messages?: string[];
  /** Website-specific info copy; preferred over messages when present. */
  web_messages?: string[];
  message?: string;
  entries?: unknown;
  require_account_age_hours_min?: number;
  require_account_age_hours_max?: number;
  dependency?: {
    type?: string;
    mode?: string;
    depends_on?: string[];
  };
  [key: string]: unknown;
};

export type AttributePointBuy = {
  pool: number;
  max_rank: number;
  cost_for_rank: number[];
  attributes: string[];
  abbreviations?: Record<string, string>;
  trait_id_pattern?: string;
};

export type AttributeModifierDto = {
  type: string;
  amount: number;
};

export type ExperienceModifierDto = {
  profession: string;
  alias: string;
  amount: number;
};

export type CatalogIdRow = {
  id: string;
  name?: string;
  description?: string | string[];
  age_max?: number;
  attribute_modifiers?: AttributeModifierDto[];
  experience_modifiers?: ExperienceModifierDto[];
  attribute_description?: string[];
  [key: string]: unknown;
};

export type CatalogTrait = {
  id: string;
  name?: string;
  key?: string;
  description?: string | string[];
  cost?: number;
  attribute_modifiers?: AttributeModifierDto[];
  experience_modifiers?: ExperienceModifierDto[];
  mutually_exclusive?: string[];
  dependency?: {
    type?: string;
    mode?: string;
    depends_on?: string[];
  };
  required_account_playtime_hours?: number;
  [key: string]: unknown;
};

export type CatalogValidation = {
  name?: { min_length?: number; max_length?: number };
  age?: { minimum?: number };
  calendar?: { year_offset?: number; era_suffix?: string };
  description?: { min_length?: number; max_length?: number };
  clues?: {
    default_required?: number;
    evil_required?: number;
    evil_min_account_age_hours?: number;
    min_length?: number;
    max_length?: number;
    max_clues?: number;
  };
};

export type SlotLimits = {
  hard_cap?: number;
  defaults?: {
    max_alive_characters?: number;
    name_colour_stops?: number;
  };
  groups?: unknown[];
};

export async function getCreationCatalog(
  sessionToken: string
): Promise<CreationCatalog> {
  const res = await apiFetch(`${getApiBase()}/characters/creation-catalog`, {
    headers: authHeaders(sessionToken),
  });
  const data = await parseJson(res);
  if (!res.ok) {
    throw new CharactersApiError(
      detailMessage(data, `Catalog failed (${res.status})`),
      res.status
    );
  }
  return data as CreationCatalog;
}

export type CharacterListItem = {
  id: string;
  name: string;
  status: string;
  race?: string | null;
  class?: string | null;
  created_at?: string | null;
  source?: string;
  create_id?: string;
};

export type CharacterListResponse = {
  characters: CharacterListItem[];
  player_uuid: string;
  max_alive_characters?: number;
  alive_count?: number;
  /** Player already answered the 18+ attestation (Yes or No). */
  real_age_set?: boolean;
  eighteen?: boolean;
  /** Wall-clock seconds since Minecraft account created_at. */
  account_age_seconds?: number;
  /** True when account age meets evil_min_account_age_hours. */
  evil_unlocked?: boolean;
  /** Rank perk: max name colour stops (0 = locked). */
  name_colour_stops?: number;
};

export async function listCharacters(
  sessionToken: string
): Promise<CharacterListResponse> {
  const res = await apiFetch(`${getApiBase()}/characters`, {
    headers: authHeaders(sessionToken),
  });
  const data = await parseJson(res);
  if (!res.ok) {
    throw new CharactersApiError(
      detailMessage(data, `List failed (${res.status})`),
      res.status
    );
  }
  const body = data as CharacterListResponse;
  return {
    characters: Array.isArray(body.characters) ? body.characters : [],
    player_uuid: body.player_uuid || "",
    max_alive_characters:
      typeof body.max_alive_characters === "number"
        ? body.max_alive_characters
        : undefined,
    alive_count:
      typeof body.alive_count === "number" ? body.alive_count : undefined,
    real_age_set: Boolean(body.real_age_set),
    eighteen:
      typeof body.eighteen === "boolean" ? body.eighteen : undefined,
    account_age_seconds:
      typeof body.account_age_seconds === "number"
        ? body.account_age_seconds
        : undefined,
    evil_unlocked:
      typeof body.evil_unlocked === "boolean" ? body.evil_unlocked : undefined,
    name_colour_stops:
      typeof body.name_colour_stops === "number"
        ? Math.max(0, body.name_colour_stops)
        : 0,
  };
}

export type CreateCharacterBody = {
  client_request_id?: string;
  name: string;
  age: number;
  /** Fantasy ISO birthday (YYYY-MM-DD); salted from client_request_id + age. */
  birthday?: string;
  /** Real-life 18+ attestation from creation_age_set_stage. */
  eighteen?: boolean;
  description: string;
  gender: string;
  race_id: string;
  class_id: string;
  attributes: Record<string, number>;
  traits: string[];
  clues: string[];
  /** Persona name colours (separate from name string). */
  name_colours?: string[];
};

export type CreateCharacterResult = {
  ok: boolean;
  id: string;
  status: string;
  client_request_id?: string | null;
  created_at?: string;
};

export async function createCharacter(
  sessionToken: string,
  body: CreateCharacterBody
): Promise<CreateCharacterResult> {
  const res = await apiFetch(`${getApiBase()}/characters`, {
    method: "POST",
    headers: {
      ...authHeaders(sessionToken),
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });
  const data = await parseJson(res);
  if (!res.ok) {
    throw new CharactersApiError(
      detailMessage(data, `Create failed (${res.status})`),
      res.status
    );
  }
  return data as CreateCharacterResult;
}

export function maxAliveSlots(slotLimits: SlotLimits | undefined): number {
  const hard = Number(slotLimits?.hard_cap ?? 10) || 10;
  const soft = Number(slotLimits?.defaults?.max_alive_characters ?? 3) || 3;
  return Math.min(soft, hard);
}
