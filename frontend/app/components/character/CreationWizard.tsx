"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import AttributeSheet from "./AttributeSheet";
import {
  CharactersApiError,
  createCharacter,
  type CatalogStage,
  type CreationCatalog,
} from "../../../lib/characters/api";
import {
  newDraft,
  playableStages,
  selectedTraitsForKey,
  setTraitsForKey,
  stageCanContinue,
  stripInfoLine,
  toCreateBody,
  traitsForKey,
  type WizardDraft,
} from "../../../lib/characters/wizardState";

type Props = {
  catalog: CreationCatalog;
  sessionToken: string;
  onLogout: () => void;
  loggingOut?: boolean;
};

function displayName(row: { id: string; name?: string }): string {
  return (row.name && String(row.name).trim()) || row.id;
}

function StageBody({
  stage,
  draft,
  catalog,
  setDraft,
  onJump,
}: {
  stage: CatalogStage;
  draft: WizardDraft;
  catalog: CreationCatalog;
  setDraft: (d: WizardDraft) => void;
  onJump: (stageId: string) => void;
}) {
  const type = String(stage.type || "").toLowerCase();
  const target = String(stage.target || "").toLowerCase();

  if (type === "info") {
    const messages = Array.isArray(stage.messages)
      ? stage.messages.map(stripInfoLine).filter(Boolean)
      : stage.message
        ? [stripInfoLine(String(stage.message))]
        : ["Continue when ready."];
    return (
      <div className="flex flex-col gap-3">
        {messages.map((line, i) => (
          <p
            key={`${stage.id}-${i}`}
            className={
              i === 0
                ? "font-[family-name:var(--font-fraunces)] text-2xl text-[var(--tfmc-cream)]"
                : "text-[var(--tfmc-mist)]"
            }
          >
            {line}
          </p>
        ))}
      </div>
    );
  }

  if (type === "setter" && target === "name") {
    return (
      <label className="flex flex-col gap-2">
        <span className="text-sm text-[var(--tfmc-stone)]">Name</span>
        <input
          value={draft.name}
          onChange={(e) => setDraft({ ...draft, name: e.target.value })}
          className="rounded-sm border border-[color-mix(in_srgb,var(--tfmc-cream)_25%,transparent)] bg-[color-mix(in_srgb,var(--tfmc-forest)_40%,transparent)] px-3 py-2.5 text-[var(--tfmc-cream)] outline-none focus:border-[var(--tfmc-accent)]"
        />
      </label>
    );
  }

  if (type === "setter" && target === "age") {
    return (
      <label className="flex flex-col gap-2">
        <span className="text-sm text-[var(--tfmc-stone)]">Age</span>
        <input
          type="number"
          inputMode="numeric"
          value={draft.age}
          onChange={(e) => setDraft({ ...draft, age: e.target.value })}
          className="rounded-sm border border-[color-mix(in_srgb,var(--tfmc-cream)_25%,transparent)] bg-[color-mix(in_srgb,var(--tfmc-forest)_40%,transparent)] px-3 py-2.5 text-[var(--tfmc-cream)] outline-none focus:border-[var(--tfmc-accent)]"
        />
      </label>
    );
  }

  if (type === "setter" && target === "description") {
    return (
      <div className="flex flex-col gap-4">
        <label className="flex flex-col gap-2">
          <span className="text-sm text-[var(--tfmc-stone)]">Description</span>
          <textarea
            rows={5}
            value={draft.description}
            onChange={(e) =>
              setDraft({ ...draft, description: e.target.value })
            }
            className="rounded-sm border border-[color-mix(in_srgb,var(--tfmc-cream)_25%,transparent)] bg-[color-mix(in_srgb,var(--tfmc-forest)_40%,transparent)] px-3 py-2.5 text-[var(--tfmc-cream)] outline-none focus:border-[var(--tfmc-accent)]"
          />
        </label>
        <label className="flex flex-col gap-2">
          <span className="text-sm text-[var(--tfmc-stone)]">
            Gender (optional)
          </span>
          <input
            value={draft.gender}
            onChange={(e) => setDraft({ ...draft, gender: e.target.value })}
            placeholder="unspecified"
            className="rounded-sm border border-[color-mix(in_srgb,var(--tfmc-cream)_25%,transparent)] bg-[color-mix(in_srgb,var(--tfmc-forest)_40%,transparent)] px-3 py-2.5 text-[var(--tfmc-cream)] outline-none placeholder:text-[color-mix(in_srgb,var(--tfmc-mist)_60%,transparent)] focus:border-[var(--tfmc-accent)]"
          />
        </label>
      </div>
    );
  }

  if (type === "selection" && target === "class") {
    return (
      <ul className="grid gap-2 sm:grid-cols-2">
        {(catalog.classes || []).map((c) => {
          const selected = draft.class_id === c.id;
          return (
            <li key={c.id}>
              <button
                type="button"
                onClick={() => setDraft({ ...draft, class_id: c.id })}
                className={`w-full rounded-sm border px-3 py-3 text-left transition ${
                  selected
                    ? "border-[var(--tfmc-accent)] bg-[color-mix(in_srgb,var(--tfmc-accent)_15%,transparent)]"
                    : "border-[color-mix(in_srgb,var(--tfmc-cream)_20%,transparent)] hover:border-[color-mix(in_srgb,var(--tfmc-cream)_40%,transparent)]"
                }`}
              >
                <span className="font-medium text-[var(--tfmc-cream)]">
                  {displayName(c)}
                </span>
              </button>
            </li>
          );
        })}
      </ul>
    );
  }

  if (type === "selection" && target === "race") {
    return (
      <ul className="grid gap-2 sm:grid-cols-2">
        {(catalog.races || []).map((r) => {
          const selected = draft.race_id === r.id;
          return (
            <li key={r.id}>
              <button
                type="button"
                onClick={() => setDraft({ ...draft, race_id: r.id })}
                className={`w-full rounded-sm border px-3 py-3 text-left transition ${
                  selected
                    ? "border-[var(--tfmc-accent)] bg-[color-mix(in_srgb,var(--tfmc-accent)_15%,transparent)]"
                    : "border-[color-mix(in_srgb,var(--tfmc-cream)_20%,transparent)] hover:border-[color-mix(in_srgb,var(--tfmc-cream)_40%,transparent)]"
                }`}
              >
                <span className="font-medium text-[var(--tfmc-cream)]">
                  {displayName(r)}
                </span>
              </button>
            </li>
          );
        })}
      </ul>
    );
  }

  if (type === "selection" && target === "trait") {
    const key = String(stage.key || "").trim();
    const options = traitsForKey(catalog, key);
    const selected = selectedTraitsForKey(draft, catalog, key);
    const max = Number(stage.max_select ?? 1);
    const min = Number(stage.min_select ?? 0);

    function toggle(id: string) {
      const set = new Set(selected);
      if (set.has(id)) {
        set.delete(id);
      } else if (max <= 1) {
        set.clear();
        set.add(id);
      } else if (set.size < max) {
        set.add(id);
      }
      setDraft(setTraitsForKey(draft, catalog, key, [...set]));
    }

    return (
      <div className="flex flex-col gap-3">
        <p className="text-sm text-[var(--tfmc-stone)]">
          Choose {min === max ? min : `${min}–${max}`}
          {key ? ` (${key})` : ""}
        </p>
        <ul className="grid gap-2">
          {options.map((t) => {
            const on = selected.includes(t.id);
            return (
              <li key={t.id}>
                <button
                  type="button"
                  onClick={() => toggle(t.id)}
                  className={`w-full rounded-sm border px-3 py-3 text-left transition ${
                    on
                      ? "border-[var(--tfmc-accent)] bg-[color-mix(in_srgb,var(--tfmc-accent)_15%,transparent)]"
                      : "border-[color-mix(in_srgb,var(--tfmc-cream)_20%,transparent)] hover:border-[color-mix(in_srgb,var(--tfmc-cream)_40%,transparent)]"
                  }`}
                >
                  <span className="font-medium text-[var(--tfmc-cream)]">
                    {displayName(t)}
                  </span>
                </button>
              </li>
            );
          })}
        </ul>
      </div>
    );
  }

  if (type === "attributes" && catalog.attribute_point_buy) {
    return (
      <AttributeSheet
        ranks={draft.attributes}
        apb={catalog.attribute_point_buy}
        onChange={(attributes) => setDraft({ ...draft, attributes })}
      />
    );
  }

  if (type === "clue") {
    const cfg = catalog.validation?.clues || {};
    const required = Number(cfg.default_required ?? 1);
    const maxClues = Number(cfg.max_clues ?? 5);

    function updateClue(i: number, value: string) {
      const next = [...draft.clues];
      next[i] = value;
      setDraft({ ...draft, clues: next });
    }

    function addClue() {
      if (draft.clues.length >= maxClues) return;
      setDraft({ ...draft, clues: [...draft.clues, ""] });
    }

    function removeClue(i: number) {
      if (draft.clues.length <= 1) return;
      setDraft({
        ...draft,
        clues: draft.clues.filter((_, idx) => idx !== i),
      });
    }

    return (
      <div className="flex flex-col gap-3">
        <p className="text-sm text-[var(--tfmc-stone)]">
          At least {required} clue{required === 1 ? "" : "s"} (max {maxClues})
        </p>
        {draft.clues.map((clue, i) => (
          <div key={i} className="flex gap-2">
            <input
              value={clue}
              onChange={(e) => updateClue(i, e.target.value)}
              placeholder={`Clue ${i + 1}`}
              className="flex-1 rounded-sm border border-[color-mix(in_srgb,var(--tfmc-cream)_25%,transparent)] bg-[color-mix(in_srgb,var(--tfmc-forest)_40%,transparent)] px-3 py-2.5 text-[var(--tfmc-cream)] outline-none focus:border-[var(--tfmc-accent)]"
            />
            {draft.clues.length > 1 ? (
              <button
                type="button"
                onClick={() => removeClue(i)}
                className="px-2 text-sm text-[var(--tfmc-stone)] hover:text-[var(--tfmc-cream)]"
              >
                Remove
              </button>
            ) : null}
          </div>
        ))}
        {draft.clues.length < maxClues ? (
          <button
            type="button"
            onClick={addClue}
            className="self-start text-sm text-[var(--tfmc-accent)] hover:underline"
          >
            Add clue
          </button>
        ) : null}
      </div>
    );
  }

  if (type === "summary") {
    const race = catalog.races.find((r) => r.id === draft.race_id);
    const klass = catalog.classes.find((c) => c.id === draft.class_id);
    const traitNames = draft.traitIds.map((id) => {
      const t = catalog.traits.find((x) => x.id === id);
      return t ? displayName(t) : id;
    });

    return (
      <div className="flex flex-col gap-4 text-sm text-[var(--tfmc-mist)]">
        <SummaryLine
          label="Name"
          value={draft.name}
          onEdit={() => onJump("name")}
        />
        <SummaryLine
          label="Age"
          value={draft.age}
          onEdit={() => onJump("age")}
        />
        <SummaryLine
          label="Race"
          value={race ? displayName(race) : draft.race_id}
          onEdit={() => onJump("race")}
        />
        <SummaryLine
          label="Class"
          value={klass ? displayName(klass) : draft.class_id}
          onEdit={() => onJump("class")}
        />
        <SummaryLine
          label="Attributes"
          value={Object.entries(draft.attributes)
            .map(([k, v]) => `${k} +${v}`)
            .join(", ")}
          onEdit={() => onJump("attributes")}
        />
        <SummaryLine
          label="Traits"
          value={traitNames.join(", ") || "—"}
          onEdit={() => onJump("trait")}
        />
        <SummaryLine
          label="Description"
          value={draft.description}
          onEdit={() => onJump("description")}
        />
        <SummaryLine
          label="Clues"
          value={draft.clues.filter((c) => c.trim()).join(" · ") || "—"}
          onEdit={() => onJump("clue")}
        />
      </div>
    );
  }

  return (
    <p className="text-[var(--tfmc-mist)]">
      Unsupported stage type “{type}”. Continue to skip.
    </p>
  );
}

function SummaryLine({
  label,
  value,
  onEdit,
}: {
  label: string;
  value: string;
  onEdit: () => void;
}) {
  return (
    <div className="flex items-start justify-between gap-3 border-b border-[color-mix(in_srgb,var(--tfmc-cream)_10%,transparent)] pb-3">
      <div>
        <p className="text-xs uppercase tracking-wide text-[var(--tfmc-stone)]">
          {label}
        </p>
        <p className="mt-1 text-[var(--tfmc-cream)]">{value || "—"}</p>
      </div>
      <button
        type="button"
        onClick={onEdit}
        className="shrink-0 text-xs text-[var(--tfmc-accent)] hover:underline"
      >
        Edit
      </button>
    </div>
  );
}

export default function CreationWizard({
  catalog,
  sessionToken,
  onLogout,
  loggingOut = false,
}: Props) {
  const router = useRouter();
  const stages = useMemo(() => playableStages(catalog), [catalog]);
  const [index, setIndex] = useState(0);
  const [draft, setDraft] = useState(() => newDraft(catalog));
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const stage = stages[index];
  const isLast = index >= stages.length - 1;
  const canNext = stage
    ? stageCanContinue(stage, draft, catalog)
    : false;

  function jumpToKind(kind: string) {
    const k = kind.toLowerCase();
    const i = stages.findIndex((s) => {
      const t = String(s.type || "").toLowerCase();
      const target = String(s.target || "").toLowerCase();
      if (k === "name" || k === "age" || k === "description") {
        return t === "setter" && target === k;
      }
      if (k === "race" || k === "class") {
        return t === "selection" && target === k;
      }
      if (k === "trait") {
        return t === "selection" && target === "trait";
      }
      if (k === "attributes") return t === "attributes";
      if (k === "clue") return t === "clue";
      return s.id === k;
    });
    if (i >= 0) setIndex(i);
  }

  async function onSubmit() {
    setError(null);
    setSubmitting(true);
    try {
      await createCharacter(sessionToken, toCreateBody(draft));
      router.replace("/character");
    } catch (err) {
      setError(
        err instanceof CharactersApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : "Create failed"
      );
    } finally {
      setSubmitting(false);
    }
  }

  if (!stage) {
    return (
      <p className="mt-8 text-[var(--tfmc-mist)]">
        Creation catalog has no stages. Ask staff to sync RPCharacters.
      </p>
    );
  }

  const type = String(stage.type || "").toLowerCase();
  const isSummary = type === "summary";
  const showSubmit = isSummary || isLast;

  return (
    <div className="mt-6 flex flex-1 flex-col">
      <div className="mb-4 flex items-center justify-between gap-3">
        <p className="text-xs text-[var(--tfmc-stone)]">
          Step {index + 1} / {stages.length}
        </p>
        <button
          type="button"
          onClick={onLogout}
          disabled={loggingOut}
          className="text-sm text-[var(--tfmc-stone)] underline-offset-2 hover:text-[var(--tfmc-cream)] hover:underline disabled:opacity-50"
        >
          {loggingOut ? "Logging out…" : "Log out"}
        </button>
      </div>

      <div key={stage.id} className="char-step flex-1">
        {!isSummary && type !== "info" ? (
          <h2 className="mb-4 font-[family-name:var(--font-fraunces)] text-2xl text-[var(--tfmc-cream)]">
            {stageTitle(stage)}
          </h2>
        ) : null}
        <StageBody
          stage={stage}
          draft={draft}
          catalog={catalog}
          setDraft={setDraft}
          onJump={jumpToKind}
        />
      </div>

      {error ? (
        <p className="mt-4 text-sm text-[#e8a0a0]" role="alert">
          {error}
        </p>
      ) : null}

      <div className="sticky bottom-0 mt-8 flex gap-3 border-t border-[color-mix(in_srgb,var(--tfmc-cream)_12%,transparent)] bg-[color-mix(in_srgb,var(--tfmc-forest-deep)_92%,transparent)] py-4 backdrop-blur-sm">
        <button
          type="button"
          disabled={index === 0 || submitting}
          onClick={() => setIndex((i) => Math.max(0, i - 1))}
          className="rounded-sm border border-[color-mix(in_srgb,var(--tfmc-cream)_30%,transparent)] px-4 py-2.5 text-sm font-semibold text-[var(--tfmc-cream)] disabled:opacity-40"
        >
          Back
        </button>
        {showSubmit ? (
          <button
            type="button"
            disabled={!canNext || submitting}
            onClick={() => void onSubmit()}
            className="flex-1 rounded-sm bg-[var(--tfmc-accent)] px-4 py-2.5 text-sm font-semibold text-[var(--tfmc-forest-deep)] disabled:opacity-50"
          >
            {submitting ? "Creating…" : "Create character"}
          </button>
        ) : (
          <button
            type="button"
            disabled={!canNext || submitting}
            onClick={() =>
              setIndex((i) => Math.min(stages.length - 1, i + 1))
            }
            className="flex-1 rounded-sm bg-[var(--tfmc-accent)] px-4 py-2.5 text-sm font-semibold text-[var(--tfmc-forest-deep)] disabled:opacity-50"
          >
            Next
          </button>
        )}
      </div>
    </div>
  );
}

function stageTitle(stage: CatalogStage): string {
  const type = String(stage.type || "").toLowerCase();
  const target = String(stage.target || "").toLowerCase();
  if (type === "setter" && target) return target.charAt(0).toUpperCase() + target.slice(1);
  if (type === "selection" && target === "class") return "Class";
  if (type === "selection" && target === "race") return "Race";
  if (type === "selection" && target === "trait") {
    const key = String(stage.key || "Traits");
    return key.charAt(0).toUpperCase() + key.slice(1);
  }
  if (type === "attributes") return "Attributes";
  if (type === "clue") return "Clues";
  if (type === "summary") return "Summary";
  return stage.id;
}
