"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  CharactersApiError,
  clearWardrobeSlot,
  fetchWardrobeTextureBlob,
  getWardrobe,
  setWardrobeActive,
  uploadWardrobeSlot,
  type SlotLimits,
  type WardrobeResponse,
  type WardrobeSlot,
} from "../../../lib/characters/api";
import { lockLabelForSlot } from "../../../lib/characters/wardrobeRanks";
import WardrobeSlotFrame from "./WardrobeSlotFrame";
import WardrobeSlotModal from "./WardrobeSlotModal";

const SLOT_ORDER = ["base", "extra_1", "extra_2", "masked"] as const;

const SLOT_LABELS: Record<string, string> = {
  base: "Base",
  extra_1: "Skin 2",
  extra_2: "Skin 3",
  masked: "Masked",
};

export type WardrobeDraftFiles = Partial<
  Record<(typeof SLOT_ORDER)[number], File | null>
>;

type LiveProps = {
  mode: "live";
  characterId: string;
  sessionToken: string;
  slotLimits?: SlotLimits;
  /** When true, skip API and show empty slots. */
  uiDev?: boolean;
};

type DraftProps = {
  mode: "draft";
  slotLimits?: SlotLimits;
  /** Player swappable slot count (1–3). */
  swappableSlots?: number;
  draftFiles: WardrobeDraftFiles;
  onDraftFilesChange: (next: WardrobeDraftFiles) => void;
};

export type WardrobeEditorProps = LiveProps | DraftProps;

function slotUnlocked(slot: string, swappable: number): boolean {
  if (slot === "base" || slot === "masked") return true;
  if (slot === "extra_1") return swappable >= 2;
  if (slot === "extra_2") return swappable >= 3;
  return false;
}

function emptySlots(swappable: number): WardrobeSlot[] {
  return SLOT_ORDER.map((slot) => ({
    slot,
    unlocked: slotUnlocked(slot, swappable),
    filled: false,
  }));
}

export default function WardrobeEditor(props: WardrobeEditorProps) {
  const isDraft = props.mode === "draft";
  const slotLimits = props.slotLimits;
  const swappable = isDraft
    ? Math.max(1, Math.min(3, props.swappableSlots ?? 1))
    : 1;

  const [wardrobe, setWardrobe] = useState<WardrobeResponse | null>(null);
  const [textures, setTextures] = useState<Record<string, string>>({});
  const [error, setError] = useState<string | null>(null);
  const [modalSlot, setModalSlot] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [modalError, setModalError] = useState<string | null>(null);
  const [equipping, setEquipping] = useState<string | null>(null);

  const revokeTextures = useCallback((map: Record<string, string>) => {
    for (const url of Object.values(map)) {
      try {
        URL.revokeObjectURL(url);
      } catch {
        /* ignore */
      }
    }
  }, []);

  const loadTextures = useCallback(
    async (token: string, characterId: string, data: WardrobeResponse) => {
      const next: Record<string, string> = {};
      await Promise.all(
        data.slots
          .filter((s) => s.filled)
          .map(async (s) => {
            try {
              next[s.slot] = await fetchWardrobeTextureBlob(
                token,
                characterId,
                s.slot
              );
            } catch {
              /* leave empty */
            }
          })
      );
      setTextures((prev) => {
        revokeTextures(prev);
        return next;
      });
    },
    [revokeTextures]
  );

  // Live load
  useEffect(() => {
    if (isDraft) return;
    const { characterId, sessionToken, uiDev } = props;
    let cancelled = false;
    setError(null);
    void (async () => {
      try {
        if (uiDev) {
          if (!cancelled) {
            setWardrobe({
              character_id: characterId,
              active_slot: null,
              swappable_slots: 1,
              slots: emptySlots(1),
            });
          }
          return;
        }
        const w = await getWardrobe(sessionToken, characterId);
        if (cancelled) return;
        setWardrobe(w);
        await loadTextures(sessionToken, characterId, w);
      } catch (err) {
        if (cancelled) return;
        setError(
          err instanceof CharactersApiError
            ? err.message
            : err instanceof Error
              ? err.message
              : "Failed to load wardrobe"
        );
      }
    })();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isDraft, isDraft ? null : props.characterId, isDraft ? null : props.sessionToken]);

  // Draft texture blobs from files
  useEffect(() => {
    if (!isDraft) return;
    const files = props.draftFiles;
    const next: Record<string, string> = {};
    for (const id of SLOT_ORDER) {
      const f = files[id];
      if (f) next[id] = URL.createObjectURL(f);
    }
    setTextures((prev) => {
      revokeTextures(prev);
      return next;
    });
    return () => revokeTextures(next);
  }, [isDraft, isDraft ? props.draftFiles : null, revokeTextures]);

  useEffect(() => {
    return () => {
      revokeTextures(textures);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const liveSwappable = wardrobe?.swappable_slots ?? swappable;

  const slotsById = useMemo(() => {
    const map = new Map<string, WardrobeSlot>();
    if (isDraft) {
      for (const id of SLOT_ORDER) {
        const file = props.draftFiles[id];
        map.set(id, {
          slot: id,
          unlocked: slotUnlocked(id, swappable),
          filled: Boolean(file),
        });
      }
      return map;
    }
    for (const s of wardrobe?.slots || []) {
      map.set(String(s.slot), s);
    }
    for (const id of SLOT_ORDER) {
      if (!map.has(id)) {
        map.set(id, {
          slot: id,
          unlocked: slotUnlocked(id, liveSwappable),
          filled: false,
        });
      }
    }
    return map;
  }, [isDraft, isDraft ? props.draftFiles : null, wardrobe, swappable, liveSwappable]);

  const activeSlot =
    !isDraft && wardrobe?.active_slot ? String(wardrobe.active_slot) : null;
  const modalData = modalSlot ? slotsById.get(modalSlot) : null;
  const swappableIds = SLOT_ORDER.filter((s) => s !== "masked");

  async function handleSave(file: File, equip: boolean) {
    if (!modalSlot) return;
    if (isDraft) {
      props.onDraftFilesChange({
        ...props.draftFiles,
        [modalSlot]: file,
      });
      setModalSlot(null);
      setModalError(null);
      return;
    }
    const { characterId, sessionToken, uiDev } = props;
    if (uiDev) {
      setModalError("UI dev mode cannot upload.");
      return;
    }
    setSaving(true);
    setModalError(null);
    try {
      let w = await uploadWardrobeSlot(
        sessionToken,
        characterId,
        modalSlot,
        file
      );
      if (equip && modalSlot !== "masked") {
        w = await setWardrobeActive(sessionToken, characterId, modalSlot);
      }
      setWardrobe(w);
      await loadTextures(sessionToken, characterId, w);
      setModalSlot(null);
    } catch (err) {
      setModalError(
        err instanceof CharactersApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : "Upload failed"
      );
    } finally {
      setSaving(false);
    }
  }

  async function handleClear() {
    if (!modalSlot) return;
    if (isDraft) {
      props.onDraftFilesChange({
        ...props.draftFiles,
        [modalSlot]: null,
      });
      setModalSlot(null);
      return;
    }
    const { characterId, sessionToken, uiDev } = props;
    if (uiDev) return;
    setSaving(true);
    setModalError(null);
    try {
      const w = await clearWardrobeSlot(sessionToken, characterId, modalSlot);
      setWardrobe(w);
      await loadTextures(sessionToken, characterId, w);
      setModalSlot(null);
    } catch (err) {
      setModalError(
        err instanceof CharactersApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : "Clear failed"
      );
    } finally {
      setSaving(false);
    }
  }

  async function handleEquip(slot: string) {
    if (isDraft || slot === "masked") return;
    const { characterId, sessionToken, uiDev } = props;
    if (uiDev) return;
    setEquipping(slot);
    setError(null);
    try {
      const w = await setWardrobeActive(sessionToken, characterId, slot);
      setWardrobe(w);
    } catch (err) {
      setError(
        err instanceof CharactersApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : "Equip failed"
      );
    } finally {
      setEquipping(null);
    }
  }

  return (
    <div className="flex flex-col gap-6">
      {error ? (
        <p className="text-sm text-red-300" role="alert">
          {error}
        </p>
      ) : null}

      <section>
        {!isDraft ? (
          <h2 className="mb-3 text-sm font-medium uppercase tracking-wide text-[var(--tfmc-stone)]">
            Skins
          </h2>
        ) : null}
        <div className="flex flex-wrap gap-4">
          {swappableIds.map((id) => {
            const slot = slotsById.get(id)!;
            const lock = !slot.unlocked
              ? lockLabelForSlot(id, slotLimits)
              : null;
            return (
              <WardrobeSlotFrame
                key={id}
                slot={slot}
                label={SLOT_LABELS[id] || id}
                active={!isDraft && activeSlot === id}
                textureSrc={textures[id] || null}
                lockRuns={lock?.runs}
                lockPlain={lock?.plain}
                onOpen={() => {
                  setModalError(null);
                  setModalSlot(id);
                }}
                onEquip={
                  !isDraft && slot.filled && slot.unlocked
                    ? () => void handleEquip(id)
                    : undefined
                }
                equipping={equipping === id}
              />
            );
          })}
        </div>
      </section>

      <section>
        <h2 className="mb-3 text-sm font-medium uppercase tracking-wide text-[var(--tfmc-stone)]">
          Masked
        </h2>
        <p className="mb-3 text-sm text-[var(--tfmc-mist)]">
          Used while wearing an RP mask. Not selectable in{" "}
          <span className="text-[var(--tfmc-cream)]">/rpcharacterwardrobe</span>.
        </p>
        {(() => {
          const slot = slotsById.get("masked")!;
          return (
            <WardrobeSlotFrame
              slot={slot}
              label={SLOT_LABELS.masked}
              active={false}
              textureSrc={textures.masked || null}
              onOpen={() => {
                setModalError(null);
                setModalSlot("masked");
              }}
            />
          );
        })()}
      </section>

      <WardrobeSlotModal
        open={Boolean(modalSlot && modalData)}
        slotId={modalSlot || ""}
        slotLabel={modalSlot ? SLOT_LABELS[modalSlot] || modalSlot : "Skin"}
        filled={Boolean(modalData?.filled)}
        canEquip={!isDraft && modalSlot !== "masked"}
        defaultEquipOnSave={
          !isDraft &&
          modalSlot !== "masked" &&
          (!activeSlot || activeSlot === modalSlot)
        }
        existingTextureSrc={modalSlot ? textures[modalSlot] || null : null}
        saving={saving}
        error={modalError}
        onClose={() => {
          if (!saving) {
            setModalSlot(null);
            setModalError(null);
          }
        }}
        onSave={(file, equip) => void handleSave(file, equip)}
        onClear={modalData?.filled ? () => void handleClear() : undefined}
      />
    </div>
  );
}
