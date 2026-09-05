import { afterEach, describe, expect, it, vi } from 'vitest';

import {
  configureMosaicGeneration,
  generateStage1,
} from './api';

describe('mosaic generation facade', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('sends unique spatial grid and free-positioned settings', async () => {
    const fetchMock = vi.fn(async (_input: RequestInfo | URL, _init?: RequestInit) => (
      new Response(JSON.stringify({ ok: true, outputs: [] }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      })
    ));
    vi.stubGlobal('fetch', fetchMock);

    configureMosaicGeneration({
      compositionMode: 'free',
      uniqueTiles: true,
      tileSize: 40,
      matchingMode: 'spatial',
    });

    await generateStage1({
      targets: 'targets.csv',
      sources: 'places.csv',
      output_dir: 'outputs',
      seed: 17,
      fragment_size: 24,
      reuse_limit: 8,
      output_width: 720,
      max_contribution_per_source: 1,
      search_scan_frames_per_candidate: 2,
      search_scan_max_candidates: 120,
      video_source_layout: 'grid',
      make_video: false,
      artwork: 'estan-en-todas-partes',
      contribution_seconds: 4,
      final_hold_seconds: 6,
      closing_text: 'Están en todas partes',
      duration_seconds: 90,
      fps: 30,
      split_orientation: 'side-by-side',
      colour_output: false,
    });

    const init = fetchMock.mock.calls[0][1] as RequestInit;
    const body = JSON.parse(String(init.body));
    expect(body.fragment_size).toBe(40);
    expect(body.reuse_limit).toBe(1);
    expect(body.max_contribution_per_source).toBe(0);
    expect(body.composition_mode).toBe('free');
    expect(body.unique_tiles).toBe(true);
    expect(body.matching_mode).toBe('spatial');
    expect(body.contribution_seconds).toBe(4);
    expect(body.final_hold_seconds).toBe(6);
    expect(body.duration_seconds).toBe(90);
    expect(body.fps).toBe(30);
    expect(body.closing_text).toBe('Están en todas partes');
    expect(body.split_orientation).toBe('side-by-side');
    expect(body.colour_output).toBe(false);
  });
});
