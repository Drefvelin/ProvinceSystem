import type {
  CatalogStage,
  CatalogTrait,
  CreateCharacterBody,
  CreationCatalog,
} from "./api";
import { emptyRanks, isExactSpend } from "./pointBuy";

export type WizardDraft = {
  client_request_id: string;
  name: string;
  age: string;
  description: string;
  gender: string;
  race_id: string;
  class_id: string;
  attributes: Record<string, number>;
  /** trait id → selected */
  traitIds: string[];
  clues: string[];
};

export function newDraft(catalog: CreationCatalog): WizardDraft {
  const attrs = catalog.attribute_point_buy?.attributes ?? [];
  return {
    client_request_id: crypto.randomUUID(),
    name: "",
    age: "",
    description: "",
    gender: "",
    race_id: "",
    class_id: "",
    attributes: emptyRanks(attrs),
    traitIds: [],
    clues: [""],
  };
}

export function playableStages(catalog: CreationCatalog): CatalogStage[] {
  const stages = [...(catalog.stages || [])];
  stages.sort((a, b) => Number(a.order ?? 0) - Number(b.order ?? 0));
  return stages.filter((s) => {
    const t = String(s.type || "").toLowerCase();
    return Boolean(t);
  });
}

/** Strip Minecraft-style title()/subtitle() wrappers for web display. */
export function stripInfoLine(raw: string): string {
  let s = String(raw || "");
  s = s.replace(/title\(([^)]*)\)/gi, "$1");
  s = s.replace(/subtitle\(([^)]*)\)/gi, "$1");
  // strip simple color codes / hex leftovers loosely
  s = s.replace(/§[0-9a-fk-or]/gi, "");
  s = s.replace(/#[0-9a-fA-F]{6}/g, "");
  return s.trim();
}

export function traitsForKey(
  catalog: CreationCatalog,
  key: string
): CatalogTrait[] {
  const k = key.trim().toLowerCase();
  return (catalog.traits || []).filter(
    (t) => String(t.key || "").trim().toLowerCase() === k
  );
}

export function selectedTraitsForKey(
  draft: WizardDraft,
  catalog: CreationCatalog,
  key: string
): string[] {
  const allowed = new Set(traitsForKey(catalog, key).map((t) => t.id));
  return draft.traitIds.filter((id) => allowed.has(id));
}

export function setTraitsForKey(
  draft: WizardDraft,
  catalog: CreationCatalog,
  key: string,
  selected: string[]
): WizardDraft {
  const allowed = new Set(traitsForKey(catalog, key).map((t) => t.id));
  const kept = draft.traitIds.filter((id) => !allowed.has(id));
  return { ...draft, traitIds: [...kept, ...selected] };
}

export function stageCanContinue(
  stage: CatalogStage,
  draft: WizardDraft,
  catalog: CreationCatalog
): boolean {
  const type = String(stage.type || "").toLowerCase();
  const target = String(stage.target || "").toLowerCase();

  if (type === "info" || type === "summary") return true;

  if (type === "setter") {
    if (target === "name") {
      const min = catalog.validation?.name?.min_length ?? 1;
      const max = catalog.validation?.name?.max_length ?? 32;
      const n = draft.name.trim().length;
      return n >= min && n <= max;
    }
    if (target === "age") {
      const age = Number(draft.age);
      const min = catalog.validation?.age?.minimum ?? 1;
      return Number.isFinite(age) && age >= min;
    }
    if (target === "description") {
      const min = catalog.validation?.description?.min_length ?? 1;
      const max = catalog.validation?.description?.max_length ?? 2000;
      const n = draft.description.trim().length;
      return n >= min && n <= max;
    }
    return true;
  }

  if (type === "selection") {
    if (target === "class") return Boolean(draft.class_id);
    if (target === "race") return Boolean(draft.race_id);
    if (target === "trait") {
      const key = String(stage.key || "").trim();
      if (!key) return true;
      const min = Number(stage.min_select ?? 0);
      const max = Number(stage.max_select ?? 99);
      const count = selectedTraitsForKey(draft, catalog, key).length;
      return count >= min && count <= max;
    }
  }

  if (type === "attributes") {
    const apb = catalog.attribute_point_buy;
    if (!apb) return false;
    return isExactSpend(draft.attributes, apb);
  }

  if (type === "clue") {
    const cfg = catalog.validation?.clues || {};
    const required = Number(cfg.default_required ?? 0);
    const minLen = Number(cfg.min_length ?? 1);
    const maxLen = Number(cfg.max_length ?? 500);
    const maxClues = Number(cfg.max_clues ?? 20);
    const clues = draft.clues.map((c) => c.trim()).filter(Boolean);
    if (clues.length < required || clues.length > maxClues) return false;
    return clues.every((c) => c.length >= minLen && c.length <= maxLen);
  }

  return true;
}

export function toCreateBody(draft: WizardDraft): CreateCharacterBody {
  const clues = draft.clues.map((c) => c.trim()).filter(Boolean);
  const gender = draft.gender.trim() || "unspecified";
  return {
    client_request_id: draft.client_request_id,
    name: draft.name.trim(),
    age: Number(draft.age),
    description: draft.description.trim(),
    gender,
    race_id: draft.race_id,
    class_id: draft.class_id,
    attributes: { ...draft.attributes },
    traits: [...draft.traitIds],
    clues,
  };
}
