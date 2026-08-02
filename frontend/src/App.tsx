import { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';

import { App as AppCore } from './AppCore';
import {
  configureMosaicGeneration,
  type CompositionMode,
} from './api';

const STORAGE_KEY = 'desa.mosaic-options';

type StoredOptions = {
  compositionMode: CompositionMode;
  uniqueTiles: boolean;
  tileSize: number;
};

function loadOptions(): StoredOptions {
  const fallback: StoredOptions = {
    compositionMode: 'grid',
    uniqueTiles: true,
    tileSize: 36,
  };
  try {
    const stored = JSON.parse(window.localStorage.getItem(STORAGE_KEY) ?? '{}') as Partial<StoredOptions>;
    return {
      compositionMode: stored.compositionMode === 'free' ? 'free' : 'grid',
      uniqueTiles: stored.uniqueTiles ?? true,
      tileSize: Math.max(24, Math.min(128, Number(stored.tileSize) || 36)),
    };
  } catch {
    return fallback;
  }
}

function prepareGenerationInspector(): HTMLElement | null {
  const section = document.getElementById('controls-generate');
  if (!section) return null;

  let host = section.querySelector<HTMLElement>('[data-mosaic-mode-controls]');
  if (!host) {
    host = document.createElement('div');
    host.dataset.mosaicModeControls = 'true';
    host.className = 'mosaic-mode-controls';
    const firstLabel = section.querySelector('label');
    section.insertBefore(host, firstLabel);
  }

  section.querySelectorAll<HTMLElement>('label').forEach((label) => {
    const text = label.textContent?.trim() ?? '';
    if (text.startsWith('Block size:') || text.includes('Reuse limit')) {
      label.style.display = 'none';
    }
    if (
      text.startsWith('Max tiles per source:')
      && window.location.hash.includes('estan-en-todas-partes')
    ) {
      label.style.display = 'none';
    } else if (text.startsWith('Max tiles per source:')) {
      label.style.display = '';
    }
    label.childNodes.forEach((node) => {
      if (
        node.nodeType === Node.TEXT_NODE
        && node.textContent?.includes('Source fragment layout')
      ) {
        node.textContent = node.textContent.replace(
          'Source fragment layout',
          'Video source layout',
        );
      }
    });
  });

  return host;
}

export function App() {
  const initial = loadOptions();
  const [compositionMode, setCompositionMode] = useState<CompositionMode>(
    initial.compositionMode,
  );
  const [uniqueTiles, setUniqueTiles] = useState(initial.uniqueTiles);
  const [tileSize, setTileSize] = useState(initial.tileSize);
  const [host, setHost] = useState<HTMLElement | null>(null);

  useEffect(() => {
    configureMosaicGeneration({
      compositionMode,
      uniqueTiles,
      tileSize,
      matchingMode: 'spatial',
    });
    window.localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({ compositionMode, uniqueTiles, tileSize }),
    );
  }, [compositionMode, tileSize, uniqueTiles]);

  useEffect(() => {
    const update = () => setHost(prepareGenerationInspector());
    update();
    const observer = new MutationObserver(update);
    observer.observe(document.body, { childList: true, subtree: true });
    window.addEventListener('hashchange', update);
    return () => {
      observer.disconnect();
      window.removeEventListener('hashchange', update);
    };
  }, []);

  return (
    <>
      <AppCore />
      {host && createPortal(
        <div>
          <h3>Image composition</h3>
          <p className="section-note">
            Spatial matching compares the internal colour, luminance, and edge
            structure of each source region with the corresponding target region.
          </p>
          <label>
            Mode
            <select
              value={compositionMode}
              onChange={(event) => setCompositionMode(
                event.target.value as CompositionMode,
              )}
            >
              <option value="grid">Grid</option>
              <option value="free">Free-positioned</option>
            </select>
          </label>
          <label className="checkbox">
            <input
              type="checkbox"
              checked={uniqueTiles}
              onChange={(event) => setUniqueTiles(event.target.checked)}
            />
            Use each image region only once
          </label>
          <label className="slider-label">
            <span>Tile size: {tileSize}px</span>
            <input
              type="range"
              min={24}
              max={128}
              step={4}
              value={tileSize}
              onChange={(event) => setTileSize(Number(event.target.value))}
            />
          </label>
        </div>,
        host,
      )}
    </>
  );
}
