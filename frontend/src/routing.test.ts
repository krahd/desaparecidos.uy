import { describe, expect, it } from 'vitest';
import {
  linkedPersonForTarget,
  linkedPersonNeedsReveal,
  linkedTargetForPerson,
  pageFromHashValue,
  reviewKindForPage,
} from './routing';
import type { ManifestRow, PersonRecord } from './api';

describe('workspace routing', () => {
  it('opens target review directly when #targets is reloaded', () => {
    const page = pageFromHashValue('#targets');
    expect(page).toBe('targets');
    expect(reviewKindForPage(page)).toBe('targets');
  });

  it('preserves the last Images review tab', () => {
    expect(reviewKindForPage(pageFromHashValue('#images'), 'people')).toBe('people');
  });

  it('recognises the third artwork route', () => {
    expect(pageFromHashValue('#seguimos-buscando')).toBe('seguimos-buscando');
  });
});

describe('linked target selection', () => {
  function target(id: string, sourceUrl = ''): ManifestRow {
    return {
      kind: 'targets',
      line_number: 2,
      id,
      label: id,
      approved: true,
      values: { source_url: sourceUrl },
    };
  }

  const person = {
    id: 'canonical-person',
    portrait_candidates: [{
      id: 'local-candidate',
      source_url: 'local://portrait.jpg',
      raw_path: 'doc/portrait.jpg',
      processed_path: '',
    }],
  } as PersonRecord;
  const canonicalTarget = target('canonical-person');
  const legacyTarget = target('legacy-row', 'local://portrait.jpg');

  it('links canonical IDs in both directions', () => {
    expect(linkedPersonForTarget([person], canonicalTarget)?.id).toBe(person.id);
    expect(linkedTargetForPerson([canonicalTarget], person)?.id).toBe(canonicalTarget.id);
  });

  it('links a legacy manifest row through portrait provenance', () => {
    expect(linkedPersonForTarget([person], legacyTarget)?.id).toBe(person.id);
    expect(linkedTargetForPerson([legacyTarget], person)?.id).toBe(legacyTarget.id);
  });

  it('leaves rows without unique evidence unmatched', () => {
    const unmatched = target('other', 'local://other.jpg');
    expect(linkedPersonForTarget([person], unmatched)).toBeNull();
  });

  it('reveals a linked person excluded by the current filter', () => {
    expect(linkedPersonNeedsReveal(['another-person'], 'basualdo-noguera-graciela-noemi')).toBe(true);
    expect(linkedPersonNeedsReveal(['basualdo-noguera-graciela-noemi'], 'basualdo-noguera-graciela-noemi')).toBe(false);
  });
});
