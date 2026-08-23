import type { TitleDraft } from "@/app/hooks/useEditorDraft";

import {
  buildChildToParentId,
  canSelectChild,
  findDuplicateChildIds,
  getChildOwnerName,
  type ParentDraft,
} from "./childTitleAssignment";

export type DuchyDraft = ParentDraft;

export function buildCountyToDuchyId(duchyDraft: DuchyDraft): Map<string, string> {
  return buildChildToParentId(duchyDraft);
}

export function canSelectCounty(
  countyId: string,
  editingDuchyId: string | null,
  assignment: Map<string, string>
): boolean {
  return canSelectChild(countyId, editingDuchyId, assignment);
}

export function findDuplicateCountyIds(duchyDraft: DuchyDraft): string[] {
  return findDuplicateChildIds(duchyDraft);
}

export function getCountyOwnerName(
  countyId: string,
  assignment: Map<string, string>,
  duchyDraft: TitleDraft
): string | null {
  return getChildOwnerName(countyId, assignment, duchyDraft);
}
