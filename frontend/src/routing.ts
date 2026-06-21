import type { ArtworkKind, ManifestRow, PersonRecord, PortraitCandidate } from './api';

export type PageId = 'targets' | 'images' | ArtworkKind;
export type ReviewKind = 'targets' | 'places' | 'people';

export function pageFromHashValue(hash: string): PageId {
  const value = hash.replace(/^#/, '');
  if (
    value === 'targets'
    || value === 'images'
    || value === 'todos-somos-familiares'
    || value === 'estan-en-todas-partes'
    || value === 'seguimos-buscando'
  ) return value;
  return 'images';
}

export function reviewKindForPage(
  page: PageId,
  imageReviewKind: 'places' | 'people' = 'places',
): ReviewKind {
  if (page === 'targets') return 'targets';
  if (page === 'images') return imageReviewKind;
  return imageReviewKind;
}

function candidateValues(person: PersonRecord): PortraitCandidate[] {
  const candidates = person.portrait_candidates ?? [];
  if (!person.selected_portrait) return candidates;
  return candidates.some((candidate) => candidate.id === person.selected_portrait?.id)
    ? candidates
    : [...candidates, person.selected_portrait];
}

function basename(value: string): string {
  const clean = value.split(/[?#]/, 1)[0].replace(/\\/g, '/');
  return clean.slice(clean.lastIndexOf('/') + 1).toLowerCase();
}

function targetMatchesPerson(target: ManifestRow, person: PersonRecord): boolean {
  if (target.id === person.id) return true;
  const sourceUrl = target.values.source_url?.trim();
  const localBasename = basename(target.file_path ?? target.values.local_path ?? '');
  return candidateValues(person).some((candidate) => (
    Boolean(sourceUrl && candidate.source_url?.trim() === sourceUrl)
    || Boolean(localBasename && [candidate.raw_path, candidate.processed_path].some(
      (path) => path && basename(path) === localBasename,
    ))
  ));
}

export function linkedPersonForTarget(
  persons: PersonRecord[],
  target: ManifestRow,
): PersonRecord | null {
  const exact = persons.find((person) => person.id === target.id);
  if (exact) return exact;
  const matches = persons.filter((person) => targetMatchesPerson(target, person));
  return matches.length === 1 ? matches[0] : null;
}

export function linkedTargetForPerson(
  targets: ManifestRow[],
  person: PersonRecord,
): ManifestRow | null {
  const exact = targets.find((target) => target.id === person.id);
  if (exact) return exact;
  const matches = targets.filter((target) => targetMatchesPerson(target, person));
  return matches.length === 1 ? matches[0] : null;
}

export function linkedPersonNeedsReveal(visiblePersonIds: string[], personId: string): boolean {
  return !visiblePersonIds.includes(personId);
}
