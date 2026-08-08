/** API base for skins + map (no trailing slash). */
export function getApiBase(): string {
  const base = (process.env.NEXT_PUBLIC_API_URL || "").trim().replace(/\/$/, "");
  if (!base) {
    throw new Error("NEXT_PUBLIC_API_URL is not set");
  }
  return base;
}

export class SkinsApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "SkinsApiError";
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

/** fetch with a clearer error when the API is unreachable. */
async function apiFetch(
  input: string,
  init?: RequestInit
): Promise<Response> {
  try {
    return await fetch(input, init);
  } catch {
    throw new Error("Upload failed. Please try again.");
  }
}

export type RedeemResult = {
  session_token: string;
  player_uuid: string;
  expires_at: string;
  code_id: number;
};

export async function redeemCode(code: string): Promise<RedeemResult> {
  const res = await apiFetch(`${getApiBase()}/skins/redeem`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code: code.trim() }),
  });

  const data = await parseJson(res);

  if (!res.ok) {
    throw new SkinsApiError(
      detailMessage(data, `Redeem failed (${res.status})`),
      res.status
    );
  }

  const body = data as Partial<RedeemResult>;
  if (!body.session_token || !body.player_uuid || !body.expires_at) {
    throw new SkinsApiError("Invalid redeem response from API", res.status);
  }

  return {
    session_token: body.session_token,
    player_uuid: body.player_uuid,
    expires_at: body.expires_at,
    code_id: Number(body.code_id),
  };
}

export type SubmissionPublic = {
  id: string;
  kind: string;
  slug: string;
  display_name: string;
  grip_preset: string | null;
  base_set: string | null;
  tiers?: string[];
  tier_aliases?: Record<string, string>;
  add_name?: boolean;
  name_colours?: string[];
  name_styles?: string[];
  status: string;
  deny_reason: string | null;
  created_at: string;
  reviewed_at: string | null;
  applied_at: string | null;
};

export type SubmissionCheckResult = {
  ok: boolean;
  conflicts: Array<{
    id: string;
    slug: string;
    display_name: string;
    status: string;
    kind: string;
    reasons: string[];
  }>;
};

export type CreateSubmissionInput = {
  sessionToken: string;
  kind: string;
  display_name: string;
  base_set?: string | null;
  tiers?: string[];
  tier_aliases?: Record<string, string>;
  grip_preset?: string | null;
  add_name?: boolean;
  name_colours?: string[];
  name_styles?: string[];
  files: Record<string, File>;
};

export async function checkSubmissionConflict(input: {
  sessionToken: string;
  display_name: string;
}): Promise<SubmissionCheckResult> {
  const params = new URLSearchParams();
  if (input.display_name.trim()) {
    params.set("display_name", input.display_name.trim());
  }
  const res = await apiFetch(
    `${getApiBase()}/skins/submissions/check?${params.toString()}`,
    {
      headers: { Authorization: `Bearer ${input.sessionToken}` },
    }
  );
  const data = await parseJson(res);
  if (!res.ok) {
    throw new SkinsApiError(
      detailMessage(data, `Conflict check failed (${res.status})`),
      res.status
    );
  }
  return data as SubmissionCheckResult;
}

export async function createSubmission(
  input: CreateSubmissionInput
): Promise<SubmissionPublic> {
  const form = new FormData();
  form.append("kind", input.kind);
  form.append("display_name", input.display_name);
  if (input.base_set) {
    form.append("base_set", input.base_set);
  }
  if (input.tiers?.length) {
    form.append("tiers", JSON.stringify(input.tiers));
  }
  if (input.tier_aliases && Object.keys(input.tier_aliases).length) {
    form.append("tier_aliases", JSON.stringify(input.tier_aliases));
  }
  if (input.grip_preset) {
    form.append("grip_preset", input.grip_preset);
  }
  if (input.add_name) {
    form.append("add_name", "true");
  }
  if (input.name_colours?.length) {
    form.append("name_colours", JSON.stringify(input.name_colours));
  }
  if (input.name_styles?.length) {
    form.append("name_styles", JSON.stringify(input.name_styles));
  }
  for (const [name, file] of Object.entries(input.files)) {
    form.append(name, file, file.name);
  }

  const res = await apiFetch(`${getApiBase()}/skins/submissions`, {
    method: "POST",
    headers: { Authorization: `Bearer ${input.sessionToken}` },
    body: form,
  });

  const data = await parseJson(res);
  if (!res.ok) {
    throw new SkinsApiError(
      detailMessage(data, `Upload failed (${res.status})`),
      res.status
    );
  }
  return data as SubmissionPublic;
}

export async function getReviewSheet(
  id: string,
  sessionToken: string
): Promise<string> {
  const res = await apiFetch(
    `${getApiBase()}/skins/submissions/${id}/review-sheet`,
    {
      headers: { Authorization: `Bearer ${sessionToken}` },
    }
  );
  if (!res.ok) {
    const data = await parseJson(res);
    throw new SkinsApiError(
      detailMessage(data, `Could not load review sheet (${res.status})`),
      res.status
    );
  }
  const blob = await res.blob();
  return URL.createObjectURL(blob);
}

export async function getSubmission(
  id: string,
  sessionToken: string
): Promise<SubmissionPublic> {
  const res = await apiFetch(`${getApiBase()}/skins/submissions/${id}`, {
    headers: { Authorization: `Bearer ${sessionToken}` },
  });
  const data = await parseJson(res);
  if (!res.ok) {
    throw new SkinsApiError(
      detailMessage(data, `Could not load submission (${res.status})`),
      res.status
    );
  }
  return data as SubmissionPublic;
}
