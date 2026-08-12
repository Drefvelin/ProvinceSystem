"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  CharactersApiError,
  clearWardrobeSlot,
  fetchWardrobeTextureBlob,
  getWardrobe,
  renameWardrobeSlot,
  setWardrobeActive,
  uploadWardrobeSlot,
  wardrobeSlotLabel,
  WARDROBE_DEFAULT_LABELS,
  type SlotLimits,
  type WardrobeResponse,
  type WardrobeSlot,
} from "../../../lib/characters/api";
import { lockLabelForSlot } from "../../../lib/characters/wardrobeRanks";
import WardrobeSlotFrame from "./WardrobeSlotFrame";
import WardrobeSlotModal from "./WardrobeSlotModal";

const SLOT_ORDER = ["base", "extra_1", "extra_2", "masked"] as const;

export type WardrobeDraftFiles = Partial<
  Record<(typeof SLOT_ORDER)[number], File | null>
>;

export type WardrobeDraftNames = Partial<
  Record<(typeof SLOT_ORDER)[number], string>
>;

type LiveProps = {
  mode: "live";
  characterId: string;
  sessionToken: string;
  slotLimits?: SlotLimits;
  /** When true, skip API and show empty slots. */
  uiDev?: boolean;
  /** UI-dev: how many swappable slots are unlocked (1–3). Always shows 3 frames. */
  uiDevSwappableSlots?: number;
};

type DraftProps = {
  mode: "draft";
  slotLimits?: SlotLimits;
  /** Player swappable slot count (1–3). */
  swappableSlots?: number;
  draftFiles: WardrobeDraftFiles;
  draftNames: WardrobeDraftNames;
  onDraftFilesChange: (next: WardrobeDraftFiles) => void;
  onDraftNamesChange: (next: WardrobeDraftNames) => void;
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
    display_name: WARDROBE_DEFAULT_LABELS[slot],
    apply_pending: false,
  }));
}

function hasPendingSlots(data: WardrobeResponse | null): boolean {
  if (!data) return false;
  return data.slots.some(
    (s) => s.filled && s.unlocked && Boolean(s.apply_pending)
  );
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
    const uiDevUnlocked = Math.max(
      1,
      Math.min(3, Number(props.uiDevSwappableSlots) || 1)
    );
    let cancelled = false;
    setError(null);
    void (async () => {
      try {
        if (uiDev) {
          if (!cancelled) {
            setWardrobe({
              character_id: characterId,
              active_slot: null,
              swappable_slots: uiDevUnlocked,
              slots: emptySlots(uiDevUnlocked),
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
  }, [
    isDraft,
    isDraft ? null : props.characterId,
    isDraft ? null : props.sessionToken,
    isDraft ? null : props.uiDev,
    isDraft ? null : props.uiDevSwappableSlots,
  ]);

  // Poll while any slot is apply-pending
  useEffect(() => {
    if (isDraft || props.mode !== "live" || props.uiDev) return;
    if (!hasPendingSlots(wardrobe)) return;
    const { characterId, sessionToken } = props;
    let cancelled = false;
    const timer = window.setInterval(() => {
      void (async () => {
        try {
          const w = await getWardrobe(sessionToken, characterId);
          if (cancelled) return;
          setWardrobe(w);
          if (!hasPendingSlots(w)) {
            await loadTextures(sessionToken, characterId, w);
          }
        } catch {
          /* keep last good state */
        }
      })();
    }, 4000);
    return () => {
      cancelled = true;
      window.clearInterval(timer);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [
    isDraft,
    wardrobe,
    isDraft ? null : props.mode === "live" ? props.characterId : null,
    isDraft ? null : props.mode === "live" ? props.sessionToken : null,
  ]);

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
        const name = props.draftNames[id];
        map.set(id, {
          slot: id,
          unlocked: slotUnlocked(id, swappable),
          filled: Boolean(file),
          display_name: wardrobeSlotLabel(id, name),
          custom_name: Boolean(String(name || "").trim()),
          apply_pending: false,
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
          display_name: WARDROBE_DEFAULT_LABELS[id],
          apply_pending: false,
        });
      }
    }
    return map;
  }, [
    isDraft,
    isDraft ? props.draftFiles : null,
    isDraft ? props.draftNames : null,
    wardrobe,
    swappable,
    liveSwappable,
  ]);

  const activeSlot =
    !isDraft && wardrobe?.active_slot ? String(wardrobe.active_slot) : null;
  const modalData = modalSlot ? slotsById.get(modalSlot) : null;
  const swappableIds = SLOT_ORDER.filter((s) => s !== "masked");

  async function handleSave(input: {
    file: File | null;
    equip: boolean;
    displayName: string | null;
  }) {
    if (!modalSlot) return;
    if (isDraft) {
      if (input.file) {
        props.onDraftFilesChange({
          ...props.draftFiles,
          [modalSlot]: input.file,
        });
      }
      const nextNames = { ...props.draftNames };
      if (input.displayName) {
        nextNames[modalSlot as keyof WardrobeDraftNames] = input.displayName;
      } else {
        delete nextNames[modalSlot as keyof WardrobeDraftNames];
      }
      props.onDraftNamesChange(nextNames);
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
      let w: WardrobeResponse;
      if (input.file) {
        w = await uploadWardrobeSlot(
          sessionToken,
          characterId,
          modalSlot,
          input.file,
          input.displayName
        );
        if (input.equip && modalSlot !== "masked") {
          w = await setWardrobeActive(sessionToken, characterId, modalSlot);
        }
      } else {
        w = await renameWardrobeSlot(
          sessionToken,
          characterId,
          modalSlot,
          input.displayName
        );
      }
      setWardrobe(w);
      if (input.file) {
        await loadTextures(sessionToken, characterId, w);
      }
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
      const nextNames = { ...props.draftNames };
      delete nextNames[modalSlot as keyof WardrobeDraftNames];
      props.onDraftNamesChange(nextNames);
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
    const data = slotsById.get(slot);
    if (data?.apply_pending) return;
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

  function labelFor(id: string, slot: WardrobeSlot): string {
    return wardrobeSlotLabel(id, slot.display_name);
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
                label={labelFor(id, slot)}
                active={!isDraft && activeSlot === id}
                textureSrc={textures[id] || null}
                lockRuns={lock?.runs}
                lockPlain={lock?.plain}
                onOpen={() => {
                  setModalError(null);
                  setModalSlot(id);
                }}
                onEquip={
                  !isDraft &&
                  slot.filled &&
                  slot.unlocked &&
                  !slot.apply_pending
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
          <span className="text-[var(--tfmc-cream)]">/rpcharacter wardrobe</span>.
        </p>
        {(() => {
          const slot = slotsById.get("masked")!;
          return (
            <WardrobeSlotFrame
              slot={slot}
              label={labelFor("masked", slot)}
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
        slotLabel={
          modalSlot && modalData
            ? labelFor(modalSlot, modalData)
            : "Skin"
        }
        filled={Boolean(modalData?.filled)}
        canEquip={!isDraft && modalSlot !== "masked"}
        defaultEquipOnSave={
          !isDraft &&
          modalSlot !== "masked" &&
          (!activeSlot || activeSlot === modalSlot)
        }
        existingTextureSrc={modalSlot ? textures[modalSlot] || null : null}
        initialDisplayName={
          modalSlot && modalData?.custom_name
            ? String(modalData.display_name || "")
            : isDraft && modalSlot
              ? String(props.draftNames[modalSlot as keyof WardrobeDraftNames] || "")
              : ""
        }
        namePlaceholder={
          modalSlot
            ? WARDROBE_DEFAULT_LABELS[modalSlot] || "Skin"
            : "Skin"
        }
        saving={saving}
        error={modalError}
        onClose={() => {
          if (!saving) {
            setModalSlot(null);
            setModalError(null);
          }
        }}
        onSave={(input) => void handleSave(input)}
        onClear={modalData?.filled ? () => void handleClear() : undefined}
      />
    </div>
  );
}
