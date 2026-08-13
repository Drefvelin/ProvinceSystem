export function getApiBase(): string {
  const base = (process.env.NEXT_PUBLIC_API_URL || "").trim().replace(/\/$/, "");
  if (!base) {
    throw new Error("NEXT_PUBLIC_API_URL is not set");
  }
  return base;
}

export class DrinksApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "DrinksApiError";
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

export type DrinkRedeemResult = {
  session_token: string;
  player_uuid: string;
  expires_at: string;
  code_id: number;
  scope?: string;
  allow_drink_texture?: boolean;
};

export type DrinkIngredient = {
  id: string;
  brewery_token?: string;
  label?: string;
  category?: string;
  type?: string | null;
};

export type DrinkCatalog = {
  ingredients: DrinkIngredient[];
  effects_blacklist: string[];
  version: number;
};

export type DrinkTexture = {
  id: string;
  cmd: number | null;
  ia_item_id: string | null;
  refcount: number;
  created_at: string;
  applied: boolean;
};

export type DrinkSubmissionPublic = {
  id: string;
  player_uuid: string;
  code_id: number;
  slug: string;
  display_name: string;
  recipe: Record<string, unknown>;
  status: string;
  deny_reason: string | null;
  texture_id: string | null;
  new_texture: boolean;
  discord_user_id: string | null;
  created_at: string;
  reviewed_at: string | null;
  applied_at: string | null;
};

export type DrinkRecipeInput = {
  name: string;
  names?: string[] | string;
  ingredients: Array<{ id: string; amount: number }>;
  cooking_time?: number;
  distill_runs?: number;
  distill_time?: number;
  wood?: string | number | null;
  age?: number;
  difficulty?: number;
  alcohol?: number;
  effects?: Array<string | { type: string; level?: number; duration?: number }>;
  color?: string | null;
  lore?: string[];
  drink_message?: string | null;
  drink_title?: string | null;
  glint?: boolean;
};

export async function redeemDrink(code: string): Promise<DrinkRedeemResult> {
  const res = await apiFetch(`${getApiBase()}/drinks/redeem`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code: code.trim() }),
  });
  const data = await parseJson(res);
  if (!res.ok) {
    throw new DrinksApiError(
      detailMessage(data, `Redeem failed (${res.status})`),
      res.status
    );
  }
  const body = data as Partial<DrinkRedeemResult>;
  if (!body.session_token || !body.player_uuid || !body.expires_at) {
    throw new DrinksApiError("Invalid redeem response from API", res.status);
  }
  return {
    session_token: body.session_token,
    player_uuid: body.player_uuid,
    expires_at: body.expires_at,
    code_id: Number(body.code_id),
    ...(typeof body.scope === "string" ? { scope: body.scope } : {}),
    ...(typeof body.allow_drink_texture === "boolean"
      ? { allow_drink_texture: body.allow_drink_texture }
      : {}),
  };
}

export async function getCatalog(): Promise<DrinkCatalog> {
  const res = await apiFetch(`${getApiBase()}/drinks/catalog`);
  const data = await parseJson(res);
  if (!res.ok) {
    throw new DrinksApiError(
      detailMessage(data, `Catalog failed (${res.status})`),
      res.status
    );
  }
  const body = data as { catalog?: Partial<DrinkCatalog> };
  const catalog = body.catalog || {};
  return {
    ingredients: Array.isArray(catalog.ingredients) ? catalog.ingredients : [],
    effects_blacklist: Array.isArray(catalog.effects_blacklist)
      ? catalog.effects_blacklist.map((e) => String(e).toLowerCase())
      : [],
    version: Number(catalog.version) || 0,
  };
}

export async function getTextures(
  sessionToken: string
): Promise<DrinkTexture[]> {
  const res = await apiFetch(`${getApiBase()}/drinks/textures`, {
    headers: { Authorization: `Bearer ${sessionToken}` },
  });
  const data = await parseJson(res);
  if (!res.ok) {
    throw new DrinksApiError(
      detailMessage(data, `Textures failed (${res.status})`),
      res.status
    );
  }
  const body = data as { textures?: DrinkTexture[] };
  const list = Array.isArray(body.textures) ? body.textures : [];
  // Belt-and-suspenders: API returns applied-only; still filter client-side.
  return list.filter(
    (t) => t && t.applied !== false && t.cmd != null && Number(t.cmd) > 0
  );
}

export async function createSubmission(input: {
  sessionToken: string;
  recipe: DrinkRecipeInput;
  texture?: File | null;
  existingTextureId?: string | null;
}): Promise<DrinkSubmissionPublic> {
  const form = new FormData();
  form.append("recipe", JSON.stringify(input.recipe));
  if (input.existingTextureId?.trim()) {
    form.append("existing_texture_id", input.existingTextureId.trim());
  }
  if (input.texture) {
    form.append("texture", input.texture, input.texture.name || "texture.png");
  }
  const res = await apiFetch(`${getApiBase()}/drinks/submissions`, {
    method: "POST",
    headers: { Authorization: `Bearer ${input.sessionToken}` },
    body: form,
  });
  const data = await parseJson(res);
  if (!res.ok) {
    throw new DrinksApiError(
      detailMessage(data, `Submit failed (${res.status})`),
      res.status
    );
  }
  return data as DrinkSubmissionPublic;
}

export async function getSubmission(
  id: string,
  sessionToken: string
): Promise<DrinkSubmissionPublic> {
  const res = await apiFetch(
    `${getApiBase()}/drinks/submissions/${encodeURIComponent(id)}`,
    { headers: { Authorization: `Bearer ${sessionToken}` } }
  );
  const data = await parseJson(res);
  if (!res.ok) {
    throw new DrinksApiError(
      detailMessage(data, `Load failed (${res.status})`),
      res.status
    );
  }
  return data as DrinkSubmissionPublic;
}
