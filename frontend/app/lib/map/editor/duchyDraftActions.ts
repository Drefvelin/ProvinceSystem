import type { EditorTitleEntry, TitleDraft } from "@/app/hooks/useEditorDraft";

import {
  removeTitleFromDraft,
  toggleChildInParent,
  type ToggleChildInParentOptions,
} from "./childTitleDraftActions";

export type ToggleCountyInDuchyOptions = {
  countyRgb?: string;
  usedRgbs?: readonly string[];
};

export function toggleCountyInDuchy(
  entry: EditorTitleEntry,
  countyId: string,
  options?: ToggleCountyInDuchyOptions
): EditorTitleEntry {
  const childOptions: ToggleChildInParentOptions | undefined = options
    ? { childRgb: options.countyRgb, usedRgbs: options.usedRgbs }
    : undefined;
  return toggleChildInParent(entry, countyId, childOptions);
}

export function removeDuchyFromDraft(
  draft: TitleDraft,
  duchyId: string
): TitleDraft {
  return removeTitleFromDraft(draft, duchyId);
}
