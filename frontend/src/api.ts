export * from './apiCore';

import {
  generateStage1 as generateStage1Core,
  type GenerateResponse,
} from './apiCore';

export type CompositionMode = 'grid' | 'free';
export type MatchingMode = 'spatial' | 'legacy';

export type MosaicGenerationOptions = {
  compositionMode: CompositionMode;
  uniqueTiles: boolean;
  tileSize: number;
  matchingMode: MatchingMode;
};

const defaults: MosaicGenerationOptions = {
  compositionMode: 'grid',
  uniqueTiles: true,
  tileSize: 36,
  matchingMode: 'spatial',
};

let mosaicOptions = { ...defaults };

export function configureMosaicGeneration(
  options: Partial<MosaicGenerationOptions>,
): MosaicGenerationOptions {
  mosaicOptions = { ...mosaicOptions, ...options };
  return { ...mosaicOptions };
}

export function getMosaicGenerationOptions(): MosaicGenerationOptions {
  return { ...mosaicOptions };
}

type CoreGeneratePayload = Parameters<typeof generateStage1Core>[0];
type ExtendedGeneratePayload = CoreGeneratePayload & {
  composition_mode: CompositionMode;
  unique_tiles: boolean;
  matching_mode: MatchingMode;
};

export function generateStage1(
  payload: CoreGeneratePayload,
): Promise<GenerateResponse> {
  const extended: ExtendedGeneratePayload = {
    ...payload,
    fragment_size: mosaicOptions.tileSize,
    reuse_limit: mosaicOptions.uniqueTiles ? 1 : payload.reuse_limit,
    // Place-derived work may use many distinct regions from the same reviewed
    // parent photograph. Exact region reuse is governed separately.
    max_contribution_per_source:
      payload.artwork === 'estan-en-todas-partes'
        ? 0
        : payload.max_contribution_per_source,
    composition_mode: mosaicOptions.compositionMode,
    unique_tiles: mosaicOptions.uniqueTiles,
    matching_mode: mosaicOptions.matchingMode,
  };
  return generateStage1Core(extended as CoreGeneratePayload);
}
