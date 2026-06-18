# desaparecidos.uy Project Status

Last updated: 2026-06-18 15:31 GMT-3

## Project purpose

`desaparecidos.uy` is a local-first computational memorial artwork triptych about detained-disappeared persons connected to Uruguay: **Todos somos familiares**, **Están en todas partes**, and **Seguimos buscando**. The current implementation focuses on the Stage 1 place-fragment prototype, **Están en todas partes**, while keeping internal review-gated ingestion for the later people-fragment work. The system is not an archive, forensic tool, biometric system, deepfake, resurrection medium, or identity-matching workflow.

## Current implementation state

The repository now combines the current crawler/search-trail work with the newer `main` GUI, API, pipeline, corpus-import, and preprocessing features. The branch keeps:

- `people` manifest support for internal Stage 2 contemporary people-source review.
- crawler run/page/image trail persistence in SQLite plus JSONL run exports;
- exact SHA-256 and perceptual duplicate rejection;
- versioned per-kind CV cache classification;
- mundane contemporary Uruguay crawler presets;
- fast search-candidate scan videos, URL ticker process videos, and `search_trail` / `search_candidates` sidecar metadata;
- Sitios importer, portrait override tooling, ignored crawler/review outputs, and current gitignore protections.

The restored current-state features include:

- pure black GUI theme;
- localStorage manifest paths;
- fixed review thumbnails;
- non-blocking crawl state;
- bulk review and row delete for `targets`, `places`, and `people`;
- target manifest builder and portrait preprocessing;
- stricter OpenCV/NumPy CV gating for detected faces and photo-like non-face place scenes;
- vectorised fragment matching;
- `max_contribution_per_source` feasibility checks and settings propagation;
- restored commemorative outro sequence in process videos.

## Active focus

The active focus is aligning the implementation with the project statement: the crawler should admit only stronger face/place candidates into review, videos should visibly perform the search through fast non-contributing candidate scans, and documentation should preserve the triptych, privacy, and non-identification constraints.

## Architecture overview

The application remains localhost-only. The GUI talks to FastAPI, FastAPI calls the manifest, crawler, preprocessing, output, and generation modules, and generated files stay in ignored local directories.

<svg width="980" height="390" viewBox="0 0 980 390" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="arch-title arch-desc">
  <title id="arch-title">Current local architecture</title>
  <desc id="arch-desc">React GUI and CLI call the local FastAPI and Python pipeline, which read manifests, crawler cache, local corpus files, and write generated outputs.</desc>
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L8,3 L0,6 Z" fill="#555"/>
    </marker>
  </defs>
  <rect x="35" y="42" width="170" height="72" rx="8" fill="#f4f4f0" stroke="#333"/>
  <text x="120" y="72" text-anchor="middle" font-size="15" fill="#111">React/Vite GUI</text>
  <text x="120" y="94" text-anchor="middle" font-size="12" fill="#333">localhost only</text>
  <rect x="35" y="150" width="170" height="72" rx="8" fill="#f4f4f0" stroke="#333"/>
  <text x="120" y="180" text-anchor="middle" font-size="15" fill="#111">CLI tools</text>
  <text x="120" y="202" text-anchor="middle" font-size="12" fill="#333">validate, crawl, run</text>
  <rect x="270" y="92" width="170" height="92" rx="8" fill="#f4f4f0" stroke="#333"/>
  <text x="355" y="126" text-anchor="middle" font-size="15" fill="#111">FastAPI backend</text>
  <text x="355" y="148" text-anchor="middle" font-size="12" fill="#333">review, crawl, generate</text>
  <rect x="505" y="32" width="170" height="72" rx="8" fill="#eef7ee" stroke="#333"/>
  <text x="590" y="62" text-anchor="middle" font-size="15" fill="#111">Manifests</text>
  <text x="590" y="84" text-anchor="middle" font-size="12" fill="#333">targets, places, people</text>
  <rect x="505" y="134" width="170" height="72" rx="8" fill="#eef7ee" stroke="#333"/>
  <text x="590" y="164" text-anchor="middle" font-size="15" fill="#111">Crawler cache</text>
  <text x="590" y="186" text-anchor="middle" font-size="12" fill="#333">SQLite, store, JSONL</text>
  <rect x="505" y="236" width="170" height="72" rx="8" fill="#eef7ee" stroke="#333"/>
  <text x="590" y="266" text-anchor="middle" font-size="15" fill="#111">Local corpus</text>
  <text x="590" y="288" text-anchor="middle" font-size="12" fill="#333">doc and processed files</text>
  <rect x="760" y="92" width="170" height="92" rx="8" fill="#f4f4f0" stroke="#333"/>
  <text x="845" y="124" text-anchor="middle" font-size="15" fill="#111">Pipeline</text>
  <text x="845" y="146" text-anchor="middle" font-size="12" fill="#333">match fragments</text>
  <text x="845" y="166" text-anchor="middle" font-size="12" fill="#333">write still/video</text>
  <rect x="760" y="236" width="170" height="72" rx="8" fill="#eef7ee" stroke="#333"/>
  <text x="845" y="266" text-anchor="middle" font-size="15" fill="#111">Outputs</text>
  <text x="845" y="288" text-anchor="middle" font-size="12" fill="#333">PNG, MP4, JSON</text>
  <line x1="205" y1="78" x2="270" y2="123" stroke="#555" stroke-width="2" marker-end="url(#arrow)"/>
  <line x1="205" y1="186" x2="270" y2="154" stroke="#555" stroke-width="2" marker-end="url(#arrow)"/>
  <line x1="440" y1="116" x2="505" y2="68" stroke="#555" stroke-width="2" marker-end="url(#arrow)"/>
  <line x1="440" y1="143" x2="505" y2="170" stroke="#555" stroke-width="2" marker-end="url(#arrow)"/>
  <line x1="440" y1="164" x2="505" y2="272" stroke="#555" stroke-width="2" marker-end="url(#arrow)"/>
  <line x1="675" y1="68" x2="760" y2="124" stroke="#555" stroke-width="2" marker-end="url(#arrow)"/>
  <line x1="675" y1="170" x2="760" y2="145" stroke="#555" stroke-width="2" marker-end="url(#arrow)"/>
  <line x1="675" y1="272" x2="760" y2="166" stroke="#555" stroke-width="2" marker-end="url(#arrow)"/>
  <line x1="845" y1="184" x2="845" y2="236" stroke="#555" stroke-width="2" marker-end="url(#arrow)"/>
</svg>

## Execution and data flow

The current data flow makes both the crawl and the search visible. Target portraits come from the curated or imported corpus; place and people source candidates come from crawler seeds. Every crawled page and image decision is persisted before review. Generated videos can replay page URLs and flash local non-contributing image candidates before showing the selected fragments assemble.

<svg width="1120" height="470" viewBox="0 0 1120 470" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="flow-title flow-desc">
  <title id="flow-title">Current corpus, crawler, review, and video flow</title>
  <desc id="flow-desc">Target corpus and crawler seeds feed manifests and crawl trails; image candidates pass through dedupe and stricter CV; approved rows generate videos with a fast candidate scan and URL ticker.</desc>
  <defs>
    <marker id="flow-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L8,3 L0,6 Z" fill="#555"/>
    </marker>
  </defs>
  <rect x="35" y="52" width="180" height="76" rx="8" fill="#f4f4f0" stroke="#333"/>
  <text x="125" y="80" text-anchor="middle" font-size="14" fill="#111">Tracked target corpus</text>
  <text x="125" y="102" text-anchor="middle" font-size="12" fill="#333">doc/fotos-desaparecidos</text>
  <rect x="35" y="172" width="180" height="76" rx="8" fill="#f4f4f0" stroke="#333"/>
  <text x="125" y="200" text-anchor="middle" font-size="14" fill="#111">Local import tools</text>
  <text x="125" y="222" text-anchor="middle" font-size="12" fill="#333">preprocess, overrides</text>
  <rect x="275" y="112" width="180" height="76" rx="8" fill="#eef7ee" stroke="#333"/>
  <text x="365" y="140" text-anchor="middle" font-size="14" fill="#111">Target manifest</text>
  <text x="365" y="162" text-anchor="middle" font-size="12" fill="#333">review-gated portraits</text>
  <rect x="35" y="334" width="180" height="76" rx="8" fill="#f4f4f0" stroke="#333"/>
  <text x="125" y="362" text-anchor="middle" font-size="14" fill="#111">Crawler seeds</text>
  <text x="125" y="384" text-anchor="middle" font-size="12" fill="#333">Uruguay now presets</text>
  <rect x="275" y="308" width="170" height="96" rx="8" fill="#f4f4f0" stroke="#333"/>
  <text x="360" y="338" text-anchor="middle" font-size="14" fill="#111">Page trail</text>
  <text x="360" y="360" text-anchor="middle" font-size="12" fill="#333">crawl order, parent</text>
  <text x="360" y="382" text-anchor="middle" font-size="12" fill="#333">status, JSONL</text>
  <rect x="505" y="308" width="170" height="96" rx="8" fill="#f4f4f0" stroke="#333"/>
  <text x="590" y="338" text-anchor="middle" font-size="14" fill="#111">Image candidates</text>
  <text x="590" y="360" text-anchor="middle" font-size="12" fill="#333">local files, events</text>
  <text x="590" y="382" text-anchor="middle" font-size="12" fill="#333">accepted and rejected</text>
  <rect x="735" y="308" width="170" height="96" rx="8" fill="#f4f4f0" stroke="#333"/>
  <text x="820" y="338" text-anchor="middle" font-size="14" fill="#111">Dedupe and CV</text>
  <text x="820" y="360" text-anchor="middle" font-size="12" fill="#333">SHA-256, pHash</text>
  <text x="820" y="382" text-anchor="middle" font-size="12" fill="#333">faces or place photos</text>
  <rect x="935" y="250" width="155" height="76" rx="8" fill="#eef7ee" stroke="#333"/>
  <text x="1012" y="278" text-anchor="middle" font-size="14" fill="#111">Pending review</text>
  <text x="1012" y="300" text-anchor="middle" font-size="12" fill="#333">places, people</text>
  <rect x="735" y="102" width="170" height="96" rx="8" fill="#eef7ee" stroke="#333"/>
  <text x="820" y="132" text-anchor="middle" font-size="14" fill="#111">Generation</text>
  <text x="820" y="154" text-anchor="middle" font-size="12" fill="#333">approved target</text>
  <text x="820" y="176" text-anchor="middle" font-size="12" fill="#333">approved places</text>
  <rect x="935" y="102" width="155" height="96" rx="8" fill="#eef7ee" stroke="#333"/>
  <text x="1012" y="130" text-anchor="middle" font-size="14" fill="#111">Process video</text>
  <text x="1012" y="152" text-anchor="middle" font-size="12" fill="#333">fast scan, assembly</text>
  <text x="1012" y="174" text-anchor="middle" font-size="12" fill="#333">URL ticker, outro</text>
  <line x1="215" y1="90" x2="275" y2="132" stroke="#555" stroke-width="2" marker-end="url(#flow-arrow)"/>
  <line x1="215" y1="210" x2="275" y2="164" stroke="#555" stroke-width="2" marker-end="url(#flow-arrow)"/>
  <line x1="215" y1="372" x2="275" y2="356" stroke="#555" stroke-width="2" marker-end="url(#flow-arrow)"/>
  <line x1="445" y1="356" x2="505" y2="356" stroke="#555" stroke-width="2" marker-end="url(#flow-arrow)"/>
  <line x1="675" y1="356" x2="735" y2="356" stroke="#555" stroke-width="2" marker-end="url(#flow-arrow)"/>
  <line x1="905" y1="344" x2="935" y2="300" stroke="#555" stroke-width="2" marker-end="url(#flow-arrow)"/>
  <path d="M1012 250 C1012 215 965 185 905 156" fill="none" stroke="#555" stroke-width="2" marker-end="url(#flow-arrow)"/>
  <path d="M455 150 C560 150 640 150 735 150" fill="none" stroke="#555" stroke-width="2" marker-end="url(#flow-arrow)"/>
  <line x1="905" y1="150" x2="935" y2="150" stroke="#555" stroke-width="2" marker-end="url(#flow-arrow)"/>
  <path d="M590 308 C640 250 775 220 935 174" fill="none" stroke="#555" stroke-width="2" marker-end="url(#flow-arrow)"/>
</svg>

## Setup and run instructions

Normal GUI run:

```bash
./start.sh
```

Manual run:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
npm --prefix frontend install
python -m desaparecidos serve --host 127.0.0.1 --port 8765
npm --prefix frontend run dev -- --host 127.0.0.1 --port 5173
```

Verification:

```bash
.venv/bin/python -m compileall src tests scripts
.venv/bin/python -m pytest -q
npm --prefix frontend run build
zsh -n start.sh
git diff --check
```

## Configuration and environment variables

- `VITE_API_BASE` can point the frontend at a non-default local API during development.
- The backend and GUI must remain bound to localhost unless explicitly changed.
- `ffmpeg` with H.264/libx264 support is required for browser-playable MP4 video generation.
- OpenCV is provided by `opencv-python-headless` and is used only for local CV filtering; no remote model or identity service is involved.

## Important files and directories

- `start.sh`: local launcher.
- `pyproject.toml`: Python package and CLI metadata.
- `src/desaparecidos/api.py`: FastAPI routes.
- `src/desaparecidos/pipeline.py`: Stage 1 assembly, sidecars, still/video rendering, URL ticker, outro.
- `src/desaparecidos/crawl.py`: bounded crawler, presets-compatible ingestion, dedupe, CV decisions, manifest row creation.
- `src/desaparecidos/cache.py`: ignored SQLite/file cache plus crawl run/page/image trail persistence.
- `src/desaparecidos/cv.py`: local non-identity CV filters and perceptual hash helpers.
- `src/desaparecidos/manifests.py`: manifest schemas, validation, review, bulk review, single and bulk row delete.
- `src/desaparecidos/preprocess.py`: portrait preprocessing for local target manifests.
- `scripts/import_sitios_memoria.py`: Sitios de Memoria importer; conservative `field-fotografia` portrait selection and per-field provenance.
- `scripts/apply_portrait_overrides.py`: replaces a person's portrait from an authoritative override source and records portrait provenance.
- `frontend/src/App.tsx`: restored black GUI workflow.
- `data/sources.json`: tracked registry of authoritative sources for disappeared-person fields and portraits.
- `data/manifests/people.csv`: tracked empty people manifest template.
- `data/manifests/crawled-*.csv`: ignored crawler review manifests.
- `data/raw/crawl/`: ignored image store, `cache.sqlite`, and JSONL run trails.
- `data/processed/`: ignored local derivatives.
- `doc/fotos-desaparecidos/`: tracked source portrait corpus.
- `outputs/stage1/`: ignored generated stills, videos, and sidecars.

## Current capabilities

- Validate `targets`, `places`, and `people` manifests.
- Review rows for all three manifest kinds: per-row approve/reject/reset/delete, plus checkbox selection with Select all, Select none, Approve selected, and Delete selected.
- Import disappeared-person metadata and portraits from Sitios de Memoria with conservative portrait selection (only the `field-fotografia` image) and `portrait_status` of `ok`/`missing`; record per-field provenance in `field_sources` against `data/sources.json`.
- Crawl ordinary contemporary Uruguay pages for place and people candidates from the GUI.
- Record every crawled page URL in crawl order with depth, parent, status, error, and fetch time.
- Record image candidate decisions, duplicate status, hashes, CV decision, and accepted row id.
- Avoid duplicate image variants with exact SHA-256 and perceptual hash checks.
- Classify the same cached URL separately per manifest kind and CV policy version.
- Store `source_url`, `source_page`, `crawl_run_id`, `content_sha256`, and `perceptual_hash` on crawled rows.
- Store face-region metadata for accepted `people` rows for manual review only; `people` rows now require a detected face and no fallback face box is generated.
- Reject obvious non-photo place candidates before review: flat graphics, limited-palette graphics/logos, prominent faces, and random-noise-like textures.
- Generate Stage 1 stills and MP4 process videos from approved targets and approved places.
- Cap source contribution with `max_contribution_per_source`; `0` means unlimited.
- Control output block size through the GUI `Block size` slider wired to `fragment_size`.
- Record settings, source usage, source sequence, search trail URLs/run ids, search candidate counts/frame references, and video process metadata in sidecars.
- Keep a fast capped search-candidate scan and URL ticker overlays on search/assembly frames, followed by a readable commemorative outro.

## Recent changes

- Aligned root and compatibility documentation with `doc/desaparecidos-uy-project-description.md`, including the triptych structure, non-identification/privacy constraints, and search-as-process language. Replaced stale `doc/AGENTS.md` and `doc/STATUS.md` templates with canonical pointers.
- Tightened crawler CV: `people` crawling requires a detected face with a minimum face box/area; `places` crawling now accepts only conservative `place-photo` candidates and rejects flat graphics, limited-palette graphics, prominent faces, and noise-like textures. Added `CV_POLICY_VERSION=2` so old cached decisions are recomputed.
- Added fast search-candidate scans to Stage 1 process videos. Videos can flash local crawl candidates that did not contribute, then switch into the existing full-source fragment highlight/assembly sequence when a usable source contributes. Sidecars now record `search_candidates` metadata.
- Fixed portrait preprocessing so processed target copies no longer keep a white scan border. `content_bbox` now tightens each edge past rows/columns that are still mostly white (`_tighten_white_edges`), correcting cases where thin dark artefacts dragged component detection into the margin. Regenerated the local `doc/fotos-desaparecidos` corpus (142 portraits) accordingly.
- Finished purging the redundant 348MB `doc/fotos-desaparecidos.zip` from git history (leftover `refs/original` from an earlier `git filter-branch`, reflog expiry, and `gc`); `.git` shrank from 911MB to ~577MB. The zip stays only as ignored `ignore/fotos-desaparecidos.zip`. No live branch or `origin/*` referenced it; no force-push was required.
- Replaced the review "Approve all" button with checkbox selection: Select all, Select none, Approve selected, Delete selected. Added `delete_manifest_rows` and bulk `row_ids` support to `POST /api/review/delete`.
- Made the Sitios importer's portrait selection conservative: only the person's `field--name-field-fotografia` image is accepted, otherwise `portrait_status="missing"` (no false poster/work imagery). Fixed field extraction so trailing fields (e.g. `victim_type`) no longer absorb the "Obras de interés"/"Materiales de interés"/footer text.
- Added `data/sources.json` (authoritative source registry) and per-field `field_sources` provenance in person records and portrait overrides. Corrected the Abeledo record: metadata from Sitios de Memoria, portrait from Parque de la Memoria.
- Reconciled `import-full-disappeared-corpus` with `main` without resetting either history.
- Restored the black GUI theme and current review ergonomics.
- Removed the primary GUI Download panel; `/api/download` and CLI download remain.
- Moved synthetic demo fixture controls into a Utilities modal.
- Restored localStorage manifest paths and non-blocking crawler state.
- Extended review tabs/actions to `Targets`, `Places`, and `People`.
- Restored and extended `max_contribution_per_source` through settings, API, GUI, sidecars, and tests.
- Added the GUI `Block size` slider for `fragment_size`.
- Combined URL ticker videos with the restored commemorative outro.
- Reintroduced OpenCV face/scene gating while keeping people ingestion non-identifying and review-gated.
- Updated `.gitignore`, `README.md`, `AGENTS.md`, and this status report for the current workflow.

## Tests and verification status

Latest local verification (documentation alignment, stricter crawler CV, search-candidate process videos):

- `.venv/bin/python -m compileall src tests scripts`: passed.
- `.venv/bin/python -m pytest -q`: passed, 86 tests, 1 upstream Starlette/httpx deprecation warning.
- `npm --prefix frontend run build`: passed (tsc + vite, no type errors).
- `zsh -n start.sh`: exited successfully with the known `nice(5)` permission warnings.
- `git diff --check`: passed.

Earlier verification retained from the current branch reconciliation:

- Importer validated against live Sitios de Memoria pages: the Abeledo page yields no portrait (`portrait_status="missing"`) and a clean `victim_type`; four other persons resolve to their correct `field-fotografia` portraits. Parque de la Memoria override applied for Abeledo (portrait provenance `parque-de-la-memoria`).
- Git: confirmed the 348MB zip blob is gone from all refs (`git rev-list --objects --all` has no match) and `.git` is ~577MB.
- Local smoke: backend health on `127.0.0.1:8766` passed; built frontend served from `frontend/dist` on `127.0.0.1:5174` returned HTTP 200; static checks confirmed black CSS background, no primary `Download` panel text in the React app, Utilities modal demo controls, crawler `places/people`, and both generation sliders.

Browser-rendered Playwright/Safari smoke is not complete in this environment: the Homebrew `playwright` executable points to a missing Python 3.11 interpreter, the virtualenv has no Playwright module, and `safaridriver --enable` requires an interactive password.

## Known issues, risks, and limitations

- Full browser-pixel verification remains blocked until Playwright or Safari WebDriver is repaired locally.
- `zsh -n start.sh` reports `nice(5)` permission warnings even though syntax validation exits successfully.
- The GUI static smoke uses the built output, not Vite dev server, because Vite port binding was blocked by sandbox permissions.
- People crawling is for internal review-gated source-corpus exploration only. It performs no identity matching and must not be used as a disappeared-person identification workflow.
- Crawler CV is stricter but still heuristic and local; manual review remains mandatory and false positives/negatives are expected.
- Process videos require local `ffmpeg` with H.264/libx264 support.
- Generated imagery, raw crawls, JSONL trails, processed target copies, and review manifests remain ignored local data.

## Pending tasks

- Build the targets curation GUI page (deferred from this change): a new top-level view to list/edit person records, set the per-field authoritative source, view/replace/choose portraits, and trigger download-from-web. Requires a persons store module and persons/sources API endpoints.
- Run the full ~205-person Sitios import with the corrected importer, then add portraits from `madres-familiares` / `parque-de-la-memoria` for persons whose `portrait_status` is `missing`.
- Repair or install a working Playwright/Safari WebDriver path for visual GUI regression checks.
- Run a full manual GUI smoke in a browser once browser automation is available.
- Review the merged `doc/DDHH/` archive additions for repository size policy if needed.
- Keep checking that crawler presets stay mundane and contemporary rather than memory/archive oriented.
- Continue improving CV thresholds only with manual review evidence from real crawl runs.

## Next steps

- Commit the combined branch once the user confirms or asks for a commit.
- Use the Utilities modal only for synthetic fixture workflows; keep primary GUI space dedicated to the real artwork workflow.
- Use crawled page trails and local image-candidate events in videos as the visible trace of the search process.

## Longer-term steps

- Add a reliable automated browser smoke suite for the GUI.
- Add further Stage 2 internal people-source tooling without identity matching.
- Decide whether future gallery installation should run the live crawler/search process or replay documented crawl trails.
- Revisit crawler persistence policy after the review workflow stabilises.

## Decisions and rationale

- `targets` remain only the disappeared-person portrait corpus.
- `people` is separate from `targets` so contemporary public people imagery cannot be confused with disappeared-person portraits.
- Crawler presets default to same-domain traversal; cross-domain remains a manual opt-in.
- Crawler CV cache entries are versioned; old decisions are recomputed rather than silently reused after policy changes.
- Download controls are hidden from the primary GUI because they are no longer central to the workflow, but API/CLI support remains for automation.
- `max_contribution_per_source=0` means unlimited for backwards compatibility and explicitness.
- Fast search-candidate scan frames and URL ticker frames are preserved during the search/assembly sequence; outro cards remain readable and untickered.

## Documentation alignment notes

- `README.md` describes the current GUI, crawler, people review gate, hidden download controls, Utilities modal, contribution cap, block-size slider, stricter CV gates, and search-scan/URL-ticker videos.
- `AGENTS.md` records current safety invariants, the tracked portrait-corpus exception, strict people/place CV expectations, and non-identification requirements.
- `CLAUDE.md` remains a short pointer to `AGENTS.md`, `STATUS.md`, and the project description.

Last updated: 2026-06-18 15:31 GMT-3
