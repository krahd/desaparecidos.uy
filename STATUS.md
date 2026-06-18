# desaparecidos.uy - Project Status

Last updated: 2026-06-18 10:49 GMT-3

## Project purpose

`desaparecidos.uy` is a computational memorial artwork series about the persistence of disappearance in Uruguay's present. Stage 1 focuses on **Estan en todas partes**, a place-based prototype that reconstructs public target portraits from fragments of Uruguayan places and surfaces. The repository now also includes an importer for building a full target corpus of detained-disappeared persons connected to Uruguay from Sitios de Memoria Uruguay.

## Current implementation state

The repository contains the Stage 1 local software prototype: a Python pipeline, FastAPI localhost backend, React/Vite GUI, manifest templates, tests, a macOS launcher, a GUI-accessible synthetic demo fixture path, a bounded page-image crawler for explicit or preset pages, a persistent SQLite/content-addressed crawl cache, crawl-trail JSONL exports, exact and perceptual image dedupe, generated-output deletion controls, and browser-playable H.264 process-video rendering when `ffmpeg` is available.

The `import-full-disappeared-corpus` branch adds `scripts/import_sitios_memoria.py`, a source-specific importer that downloads the Sitios de Memoria forced-disappearance corpus, enriches records from individual person pages, downloads target portrait candidates, writes person metadata, and creates processed 4:5 portrait derivatives for review.

Crawler output is now split by source-corpus purpose: `places` rows support Stage 1 place-fragment generation, while `people` rows are internal Stage 2 contemporary public people-source candidates. `targets` remains reserved for disappeared-person portraits.

## Active focus

Build the complete disappeared-person target corpus automatically rather than by hand, while improving the crawler so it visibly documents the search through ordinary contemporary Uruguay. Portraits of disappeared persons are treated as target imagery, distinct from crawled place and people source-corpus imagery. Public release still requires provenance, legal, privacy, and historical-source review.

## Architecture overview

The project is organised as a localhost tool. The frontend calls a local API. The API validates target, place, and people manifests; performs bounded recursive image crawling on user-supplied or preset URLs; records every crawled page and image decision; updates row review status; deletes selected generated outputs on request; and invokes reusable Python pipeline code. The pipeline reads approved target/place inputs and writes ignored outputs plus JSON sidecars. Video generation uses the same assembly trace as still generation: each used source image is introduced full-screen, sampled fragment regions are highlighted, fragments animate into their actual positions in the reconstructed portrait, and crawled or fallback source URLs appear along the bottom as a visible search trace.

The corpus importer is an offline repository-maintenance script. It writes metadata under `data/persons/`, target manifests under `data/manifests/`, and target portraits under `assets/targets/disappeared/`.

### Architecture diagram

The current architecture is a local-only workflow with an offline import path for target portraits and a crawler/search-trail path for source imagery.

<svg width="900" height="330" viewBox="0 0 900 330" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="arch-title arch-desc">
  <title id="arch-title">Stage 1 local architecture plus crawler search trail</title>
  <desc id="arch-desc">The local GUI calls the FastAPI backend. The backend validates manifests, runs the crawler into a cache and trail, and invokes the pipeline to generate stills and videos with URL ticker metadata.</desc>
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="#555" />
    </marker>
  </defs>
  <rect x="25" y="45" width="145" height="62" rx="6" fill="#f7f7f5" stroke="#777" />
  <text x="97" y="72" text-anchor="middle" font-family="Arial, sans-serif" font-size="13">React GUI</text>
  <text x="97" y="91" text-anchor="middle" font-family="Arial, sans-serif" font-size="11">localhost</text>
  <rect x="230" y="45" width="150" height="62" rx="6" fill="#f7f7f5" stroke="#777" />
  <text x="305" y="72" text-anchor="middle" font-family="Arial, sans-serif" font-size="13">FastAPI backend</text>
  <text x="305" y="91" text-anchor="middle" font-family="Arial, sans-serif" font-size="11">local routes</text>
  <rect x="455" y="35" width="155" height="82" rx="6" fill="#f7f7f5" stroke="#777" />
  <text x="532" y="66" text-anchor="middle" font-family="Arial, sans-serif" font-size="13">Crawler</text>
  <text x="532" y="85" text-anchor="middle" font-family="Arial, sans-serif" font-size="11">caps + robots</text>
  <text x="532" y="102" text-anchor="middle" font-family="Arial, sans-serif" font-size="11">dedupe + CV</text>
  <rect x="695" y="35" width="170" height="82" rx="6" fill="#f7f7f5" stroke="#777" />
  <text x="780" y="66" text-anchor="middle" font-family="Arial, sans-serif" font-size="13">Crawl cache</text>
  <text x="780" y="85" text-anchor="middle" font-family="Arial, sans-serif" font-size="11">store + SQLite</text>
  <text x="780" y="102" text-anchor="middle" font-family="Arial, sans-serif" font-size="11">JSONL trails</text>
  <rect x="125" y="205" width="160" height="70" rx="6" fill="#fff" stroke="#999" />
  <text x="205" y="233" text-anchor="middle" font-family="Arial, sans-serif" font-size="13">Sitios importer</text>
  <text x="205" y="252" text-anchor="middle" font-family="Arial, sans-serif" font-size="11">target corpus</text>
  <rect x="370" y="205" width="165" height="70" rx="6" fill="#fff" stroke="#999" />
  <text x="452" y="233" text-anchor="middle" font-family="Arial, sans-serif" font-size="13">Manifests</text>
  <text x="452" y="252" text-anchor="middle" font-family="Arial, sans-serif" font-size="11">targets / places / people</text>
  <rect x="635" y="205" width="175" height="70" rx="6" fill="#fff" stroke="#999" />
  <text x="722" y="233" text-anchor="middle" font-family="Arial, sans-serif" font-size="13">Pipeline outputs</text>
  <text x="722" y="252" text-anchor="middle" font-family="Arial, sans-serif" font-size="11">still + URL-ticker video</text>
  <line x1="170" y1="76" x2="222" y2="76" stroke="#555" stroke-width="2" marker-end="url(#arrow)" />
  <line x1="380" y1="76" x2="447" y2="76" stroke="#555" stroke-width="2" marker-end="url(#arrow)" />
  <line x1="610" y1="76" x2="687" y2="76" stroke="#555" stroke-width="2" marker-end="url(#arrow)" />
  <line x1="532" y1="117" x2="470" y2="198" stroke="#777" stroke-width="2" marker-end="url(#arrow)" />
  <line x1="285" y1="240" x2="362" y2="240" stroke="#777" stroke-width="2" marker-end="url(#arrow)" />
  <line x1="535" y1="240" x2="627" y2="240" stroke="#777" stroke-width="2" marker-end="url(#arrow)" />
  <line x1="780" y1="117" x2="745" y2="198" stroke="#777" stroke-width="2" marker-end="url(#arrow)" />
</svg>

### Flow chart

The crawler flow records both accepted source images and the search path that will later appear in process videos.

<svg width="900" height="210" viewBox="0 0 900 210" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="flow-title flow-desc">
  <title id="flow-title">Crawler search-trail flow</title>
  <desc id="flow-desc">Seed pages are crawled into page-trail events, images are deduplicated and classified, pending rows are reviewed, and the video renders the URL ticker.</desc>
  <defs>
    <marker id="flow-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="#555" />
    </marker>
  </defs>
  <rect x="18" y="70" width="125" height="60" rx="6" fill="#f7f7f5" stroke="#777" />
  <text x="80" y="96" text-anchor="middle" font-family="Arial, sans-serif" font-size="13">Seed pages</text>
  <text x="80" y="115" text-anchor="middle" font-family="Arial, sans-serif" font-size="11">ordinary Uruguay</text>
  <rect x="172" y="70" width="125" height="60" rx="6" fill="#f7f7f5" stroke="#777" />
  <text x="234" y="96" text-anchor="middle" font-family="Arial, sans-serif" font-size="13">Page trail</text>
  <text x="234" y="115" text-anchor="middle" font-family="Arial, sans-serif" font-size="11">all URLs</text>
  <rect x="326" y="70" width="130" height="60" rx="6" fill="#f7f7f5" stroke="#777" />
  <text x="391" y="96" text-anchor="middle" font-family="Arial, sans-serif" font-size="13">Image cache</text>
  <text x="391" y="115" text-anchor="middle" font-family="Arial, sans-serif" font-size="11">SHA + pHash</text>
  <rect x="485" y="70" width="125" height="60" rx="6" fill="#f7f7f5" stroke="#777" />
  <text x="547" y="96" text-anchor="middle" font-family="Arial, sans-serif" font-size="13">Dedupe + CV</text>
  <text x="547" y="115" text-anchor="middle" font-family="Arial, sans-serif" font-size="11">place / people</text>
  <rect x="640" y="70" width="125" height="60" rx="6" fill="#f7f7f5" stroke="#777" />
  <text x="702" y="96" text-anchor="middle" font-family="Arial, sans-serif" font-size="13">Pending rows</text>
  <text x="702" y="115" text-anchor="middle" font-family="Arial, sans-serif" font-size="11">manual review</text>
  <rect x="795" y="70" width="90" height="60" rx="6" fill="#f7f7f5" stroke="#777" />
  <text x="840" y="96" text-anchor="middle" font-family="Arial, sans-serif" font-size="13">Video</text>
  <text x="840" y="115" text-anchor="middle" font-family="Arial, sans-serif" font-size="11">URL ticker</text>
  <line x1="143" y1="100" x2="164" y2="100" stroke="#555" stroke-width="2" marker-end="url(#flow-arrow)" />
  <line x1="297" y1="100" x2="318" y2="100" stroke="#555" stroke-width="2" marker-end="url(#flow-arrow)" />
  <line x1="456" y1="100" x2="477" y2="100" stroke="#555" stroke-width="2" marker-end="url(#flow-arrow)" />
  <line x1="610" y1="100" x2="632" y2="100" stroke="#555" stroke-width="2" marker-end="url(#flow-arrow)" />
  <line x1="765" y1="100" x2="787" y2="100" stroke="#555" stroke-width="2" marker-end="url(#flow-arrow)" />
</svg>

## Setup and run instructions

Use the local launcher for the GUI:

```bash
./start.sh
```

Manual setup:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
npm --prefix frontend install
python -m desaparecidos serve --host 127.0.0.1 --port 8765
npm --prefix frontend run dev -- --host 127.0.0.1 --port 5173
```

Run a small importer test:

```bash
python scripts/import_sitios_memoria.py --limit 5 --download-images --process-images
```

Run the full target-corpus import:

```bash
python scripts/import_sitios_memoria.py --download-images --process-images
```

## Configuration and environment variables

- No secrets are required.
- The backend must bind to `127.0.0.1` by default.
- Raw crawler downloads belong under ignored `data/raw/`.
- Crawler cache and trails belong under ignored `data/raw/crawl/` (`store/`, `cache.sqlite`, and `runs/*.jsonl`).
- Generated outputs belong under ignored `outputs/stage1/`.
- Target portraits of disappeared persons are written under ignored `assets/targets/disappeared/` by the importer.
- Browser-playable video generation requires `ffmpeg` with H.264/libx264 support.

## Important files and directories

- `README.md`: project overview and setup.
- `AGENTS.md`: repository instructions for AI coding agents.
- `STATUS.md`: mandatory project state report.
- `src/desaparecidos/`: Python pipeline and API.
- `frontend/`: local GUI.
- `scripts/import_sitios_memoria.py`: automated Sitios de Memoria metadata and target portrait importer.
- `src/desaparecidos/cache.py`: SQLite/content-addressed crawl cache plus crawl-run trail export.
- `src/desaparecidos/cv.py`: no-dependency perceptual hashing and lightweight place/people candidate gating.
- `src/desaparecidos/crawl.py`: bounded crawler, dedupe, manifest-row creation, and trail recording.
- `doc/import-sitios-de-memoria.md`: importer usage notes.
- `data/persons/`: ignored importer output for disappeared-person metadata.
- `data/manifests/`: tracked manifest templates and importer target manifest output.
- `data/manifests/people.csv`: tracked empty template for Stage 2 contemporary people-source candidates.
- `assets/targets/disappeared/`: ignored raw and processed target portraits imported from historical-memory sources.
- `data/raw/crawl/`: ignored crawler cache and crawl-trail runtime state.
- `outputs/stage1/`: ignored generated stills, videos, and sidecars.
- GitHub: private repository at `https://github.com/krahd/desaparecidos.uy`.

## Current capabilities

- Generate Stage 1 stills and process videos from reviewed local manifests.
- Operate through a localhost GUI and backend.
- Crawl bounded user-supplied or preset ordinary-Uruguay place/source pages into pending manifests.
- Crawl internal Stage 2 contemporary people-source candidates into a separate `people` manifest path without treating them as disappeared-person targets.
- Store direct image URLs, source page URLs, crawl run ids, content hashes, perceptual hashes, and per-run page trails for crawler output.
- Render a bottom URL ticker in Stage 1 videos from crawl trails or source-row URL fallbacks.
- Import the Sitios de Memoria disappearance corpus automatically into structured JSON/CSV plus target-portrait manifests.
- Download and normalise target portrait candidates to 4:5, 1200 x 1500 pixels.

## Recent changes

- Initial project documentation, Stage 1 pipeline, local GUI, manifest templates, tests, and launcher were created.
- Private GitHub repository `krahd/desaparecidos.uy` was created and `main` was pushed.
- GUI demo fixtures, review controls, constrained crawler, generated-output deletion controls, and source-first process video rendering were added.
- 2026-06-18 00:38 GMT-3 follow-up: added `scripts/import_sitios_memoria.py` for automated import of the full Sitios de Memoria disappearance corpus and target portrait candidates; added `doc/import-sitios-de-memoria.md` documenting test and full-import commands.
- 2026-06-18 09:45 GMT-3 follow-up: implemented crawler search-trail support. Added a `people` manifest kind for internal Stage 2 contemporary people-source candidates; extended place rows with crawl metadata; added `src/desaparecidos/cache.py` and `src/desaparecidos/cv.py`; made the crawler bounded recursive with same-domain defaults, robots support, exact SHA-256 dedupe, perceptual hash dedupe, per-kind image classification, page/image event storage, and JSONL run exports; replaced memory/archive crawler presets with mundane contemporary Uruguay sources; added bottom URL ticker rendering and `search_trail` sidecar metadata for Stage 1 videos.
- 2026-06-18 10:21 GMT-3 follow-up: renamed the local launcher to `start.sh` and updated repository references accordingly.
- 2026-06-18 10:49 GMT-3 follow-up: expanded `.gitignore` so local importer/crawler outputs stay untracked, including `assets/`, `data/persons/`, `data/processed/`, local manifests, and generated Sitios de Memoria target manifests.

## Tests and verification status

Previous verification on 2026-06-17 passed for compile, pytest, frontend build, synthetic fixtures, CLI smoke runs, backend health checks, GUI load, API validation, and process-video smoke rendering.

2026-06-18 importer follow-up:

- Repository files were inspected through the GitHub connector.
- The importer script and documentation were added through GitHub commits on `import-full-disappeared-corpus`.
- The importer was not executed in this environment because the active container has no direct internet access for repository-local Python execution.
- The GitHub Actions self-commit workflow was attempted but blocked by the connector safety layer, so it was not added.
- No automated test, build, or import run was performed after adding the script.

2026-06-18 crawler search-trail follow-up:

- `python -m compileall src tests`: not runnable because `python` is not on PATH in this shell.
- `python3 -m compileall src tests`: passed.
- `.venv/bin/python -m compileall src tests`: passed.
- `.venv/bin/python -m pytest -q`: passed, 29 tests; one upstream FastAPI/Starlette deprecation warning.
- `npm --prefix frontend run build`: passed.

## Known issues, risks, and limitations

- Public release requires provenance, legal, privacy, and historical-source review.
- The importer depends on the current Sitios de Memoria CSV/HTML structure.
- Automated portrait border removal is conservative and does not guarantee removal of all lettering, frames, or layout artefacts.
- The importer does not yet merge SDHPR fichas as a secondary verification layer.
- The Stage 1/Stage 2 crawler is bounded recursive and seeded only by explicit user-entered or preset ordinary-Uruguay pages. It writes pending rows that require explicit approval before generation or internal Stage 2 use.
- Crawler people-source handling is not identity matching and does not identify individuals; it records manual-review people/face candidate regions only.
- The no-dependency people/place classifier is intentionally lightweight. Manual review remains authoritative before approval.
- Crawler cache and trail state is intentionally persisted locally under ignored `data/raw/crawl/`; it can grow and should not be committed.
- MP4 generation depends on `ffmpeg` with H.264/libx264 support.
- The GitHub remote is `origin` at `https://github.com/krahd/desaparecidos.uy.git`.

## Recurring tasks

- Keep `STATUS.md` updated after meaningful implementation or verification changes.
- Keep generated outputs and local caches untracked.
- Keep crawler cache databases and JSONL crawl trails untracked.
- Review provenance and `review_status` before generation.
- Keep target portraits of disappeared persons separated from crawled source-corpus imagery.

## Pending tasks

- Run the importer against the live source.
- Inspect generated metadata and portraits.
- Decide whether imported target portraits should remain `candidate` or be marked `approved`.
- Add SDHPR verification/merge support.
- Remove unused empty import branches if desired; the active branch is `import-full-disappeared-corpus`.
- Run a real bounded crawl from the new mundane Uruguay presets and inspect the resulting `places` and `people` pending rows.

## Next steps

1. Run `python scripts/import_sitios_memoria.py --limit 5 --download-images --process-images` locally and inspect outputs.
2. Run the full import after the five-record test succeeds.
3. Keep generated `data/persons/`, `data/manifests/targets-sitios-de-memoria.csv`, and `assets/targets/disappeared/` files local unless a later release policy explicitly changes this.
4. Add SDHPR fiche cross-checking.
5. Review the visual effect of the URL ticker in a real generated process video.

## Longer-term steps

1. Expand visual method documentation.
2. Add public website pages after Stage 1 output review.
3. Prepare legal and privacy review materials before any public release.
4. Decide which target portraits become canonical and how alternates are represented.

## Decisions and rationale

- Stage 1 uses place/surface imagery first because it is visually strong and has lower privacy risk than face-fragment processing.
- Portraits of disappeared persons are treated as target imagery, not source-corpus imagery.
- Contemporary public people images are separate `people` source-corpus candidates for internal Stage 2 review only; they are not `targets`.
- Crawler videos should make the search visible by writing the traversed or source URLs along the bottom of the frame.
- The GUI is localhost-only so the artist/developer can operate the pipeline without exposing data or outputs.
- Manifests remain the boundary for generation; crawler output is only a pending manifest-building aid.
- The Sitios de Memoria importer is source-specific to keep provenance explicit and reduce manual collection work.

## Documentation alignment notes

- The root README summarises the long project description in `doc/desaparecidos-uy-project-description.md`.
- `doc/import-sitios-de-memoria.md` documents the corpus importer.
- `README.md` now documents `people` manifests, crawler dedupe/cache/trails, mundane presets, and URL-ticker videos.
- `AGENTS.md` requires `STATUS.md` to stay current.

---

Last updated: 2026-06-18 10:49 GMT-3
