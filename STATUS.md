# desaparecidos.uy Project Status

Last updated: 2026-06-20 14:45 GMT-3

## Project purpose

`desaparecidos.uy` is a local-first computational memorial artwork triptych about detained-disappeared persons connected to Uruguay: **Todos somos familiares**, **Están en todas partes**, and **Seguimos buscando**. The current implementation actively supports the first two artworks on separate pages; **Seguimos buscando** remains future work. The system is not an archive, forensic tool, biometric system, deepfake, resurrection medium, or identity-matching workflow.

## Current implementation state

The repository now combines the current crawler/search-trail work with the newer `main` GUI, API, pipeline, corpus-import, preprocessing, and target-admin features. The branch keeps:

- canonical disappeared-person target records in `data/persons/disappeared.json`;
- target administration APIs and a GUI screen for missing-field review, portrait-review filtering, record editing, portrait candidate download, selected portrait processing, and target-manifest export;
- reviewed selected 3:4 target portrait derivatives under trackable `assets/targets/disappeared/selected/`, while raw downloads and rejected candidates remain ignored;
- a first full imported corpus pass: 204 person records, 202 selected portrait derivatives, 321 total portrait candidates, 118 review-only local alternate portrait candidates, and two unresolved public-portrait gaps (`camuyrano-bottini-mario`, `gadea-hernandez-liborio`) recorded in person notes after trusted-source and web checks;
- reviewed source-backed metadata overrides in `data/persons/metadata-overrides.csv`, applied to the canonical store with per-field `field_sources` and `field_source_refs`;
- four functional hash-routed GUI pages for Targets, Images, Todos somos familiares, and Están en todas partes;
- combined single-traversal crawling with separate place/people classification, manifests, run ids, trails, review states, and per-kind dedupe;
- artwork-aware still/video generation: approved face-region fragments for Todos somos familiares and approved place fragments for Están en todas partes;
- fragment-field process videos that never display complete source photographs or non-contributing raw candidates;
- `people` manifest support for internal contemporary people-source review and generation;
- crawler run/page/image trail persistence in SQLite plus JSONL run exports;
- exact SHA-256 and perceptual duplicate rejection;
- versioned per-kind CV cache classification;
- mundane contemporary Uruguay crawler presets;
- URL ticker process videos plus truthful `search_trail` / `search_candidates` sidecar metadata without raw candidate display;
- Sitios importer and portrait override tooling updated to write the canonical person store, 3:4 selected derivatives, current target manifest fields, explicit `date_of_death` values, and current gitignore protections.

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

The active focus combines target corpus curation with the first two artwork workflows: review-gated people/place acquisition, provenance-preserving source separation, and fragment-only generation that keeps contemporary source persons non-identifiable in outputs.

## Architecture overview

The application remains localhost-only. The GUI talks to FastAPI, FastAPI calls the person-store, manifest, crawler, preprocessing, output, and generation modules, and generated files stay in ignored local directories.

<svg width="980" height="390" viewBox="0 0 980 390" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="arch-title arch-desc">
  <title id="arch-title">Current local architecture</title>
  <desc id="arch-desc">React GUI and CLI call the local FastAPI and Python pipeline, which read person records, manifests, crawler cache, local corpus files, and write generated outputs.</desc>
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L8,3 L0,6 Z" fill="#555"/>
    </marker>
  </defs>
  <rect x="35" y="42" width="170" height="72" rx="8" fill="#f4f4f0" stroke="#333"/>
  <text x="120" y="68" text-anchor="middle" font-size="15" fill="#111">React/Vite GUI</text>
  <text x="120" y="90" text-anchor="middle" font-size="12" fill="#333">four routed workspaces</text>
  <rect x="35" y="150" width="170" height="72" rx="8" fill="#f4f4f0" stroke="#333"/>
  <text x="120" y="180" text-anchor="middle" font-size="15" fill="#111">CLI tools</text>
  <text x="120" y="202" text-anchor="middle" font-size="12" fill="#333">validate, crawl, run</text>
  <rect x="270" y="92" width="170" height="92" rx="8" fill="#f4f4f0" stroke="#333"/>
  <text x="355" y="126" text-anchor="middle" font-size="15" fill="#111">FastAPI backend</text>
  <text x="355" y="148" text-anchor="middle" font-size="12" fill="#333">review, dual crawl, generate</text>
  <rect x="505" y="32" width="170" height="72" rx="8" fill="#eef7ee" stroke="#333"/>
  <text x="590" y="62" text-anchor="middle" font-size="15" fill="#111">Persons + manifests</text>
  <text x="590" y="84" text-anchor="middle" font-size="12" fill="#333">targets, places, people</text>
  <rect x="505" y="134" width="170" height="72" rx="8" fill="#eef7ee" stroke="#333"/>
  <text x="590" y="164" text-anchor="middle" font-size="15" fill="#111">Crawler cache</text>
  <text x="590" y="186" text-anchor="middle" font-size="12" fill="#333">SQLite, store, JSONL</text>
  <rect x="505" y="236" width="170" height="72" rx="8" fill="#eef7ee" stroke="#333"/>
  <text x="590" y="266" text-anchor="middle" font-size="15" fill="#111">Local corpus</text>
  <text x="590" y="288" text-anchor="middle" font-size="12" fill="#333">doc and processed files</text>
  <rect x="760" y="92" width="170" height="92" rx="8" fill="#f4f4f0" stroke="#333"/>
  <text x="845" y="124" text-anchor="middle" font-size="15" fill="#111">Pipeline</text>
  <text x="845" y="142" text-anchor="middle" font-size="12" fill="#333">two artwork modes</text>
  <text x="845" y="164" text-anchor="middle" font-size="12" fill="#333">fragment-only video</text>
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

The current data flow shares one bounded crawl traversal, then keeps place and people decisions separate through review and generation. Both artwork modes display only fragments that contribute to the reconstructed target; complete source photographs and non-contributing raw candidates remain out of generated video frames.

<svg width="1180" height="470" viewBox="0 0 1180 470" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="flow-title flow-desc">
  <title id="flow-title">Current corpus, crawler, review, and video flow</title>
  <desc id="flow-desc">Person records export reviewed targets; one crawler traversal classifies candidates into separate place and people manifests; approved rows feed the corresponding fragment-only artwork generator.</desc>
  <defs>
    <marker id="flow-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L8,3 L0,6 Z" fill="#555"/>
    </marker>
  </defs>
  <rect x="30" y="42" width="190" height="72" rx="8" fill="#f4f4f0" stroke="#333"/>
  <text x="125" y="70" text-anchor="middle" font-size="14" fill="#111">Person store + portraits</text>
  <text x="125" y="92" text-anchor="middle" font-size="12" fill="#333">Targets workspace</text>
  <rect x="290" y="42" width="190" height="72" rx="8" fill="#eef7ee" stroke="#333"/>
  <text x="385" y="70" text-anchor="middle" font-size="14" fill="#111">Approved targets</text>
  <text x="385" y="92" text-anchor="middle" font-size="12" fill="#333">derived CSV manifest</text>
  <rect x="30" y="218" width="190" height="72" rx="8" fill="#f4f4f0" stroke="#333"/>
  <text x="125" y="246" text-anchor="middle" font-size="14" fill="#111">Crawler seeds</text>
  <text x="125" y="268" text-anchor="middle" font-size="12" fill="#333">bounded, same-domain</text>
  <rect x="290" y="196" width="190" height="116" rx="8" fill="#f4f4f0" stroke="#333"/>
  <text x="385" y="226" text-anchor="middle" font-size="14" fill="#111">Combined crawl</text>
  <text x="385" y="248" text-anchor="middle" font-size="12" fill="#333">one traversal/download</text>
  <text x="385" y="270" text-anchor="middle" font-size="12" fill="#333">two CV decisions</text>
  <text x="385" y="292" text-anchor="middle" font-size="12" fill="#333">separate trails</text>
  <rect x="550" y="160" width="190" height="82" rx="8" fill="#eef7ee" stroke="#333"/>
  <text x="645" y="190" text-anchor="middle" font-size="14" fill="#111">Places manifest</text>
  <text x="645" y="214" text-anchor="middle" font-size="12" fill="#333">pending place photos</text>
  <rect x="550" y="298" width="190" height="82" rx="8" fill="#eef7ee" stroke="#333"/>
  <text x="645" y="328" text-anchor="middle" font-size="14" fill="#111">People manifest</text>
  <text x="645" y="352" text-anchor="middle" font-size="12" fill="#333">pending face regions</text>
  <rect x="790" y="160" width="160" height="82" rx="8" fill="#f4f4f0" stroke="#333"/>
  <text x="870" y="190" text-anchor="middle" font-size="14" fill="#111">Place review</text>
  <text x="870" y="214" text-anchor="middle" font-size="12" fill="#333">manual approval</text>
  <rect x="790" y="298" width="160" height="82" rx="8" fill="#f4f4f0" stroke="#333"/>
  <text x="870" y="328" text-anchor="middle" font-size="14" fill="#111">People review</text>
  <text x="870" y="352" text-anchor="middle" font-size="12" fill="#333">manual approval</text>
  <rect x="1000" y="150" width="160" height="102" rx="8" fill="#eef7ee" stroke="#333"/>
  <text x="1080" y="180" text-anchor="middle" font-size="14" fill="#111">Están en todas partes</text>
  <text x="1080" y="204" text-anchor="middle" font-size="12" fill="#333">place fragments only</text>
  <text x="1080" y="226" text-anchor="middle" font-size="12" fill="#333">PNG, MP4, JSON</text>
  <rect x="1000" y="288" width="160" height="102" rx="8" fill="#eef7ee" stroke="#333"/>
  <text x="1080" y="318" text-anchor="middle" font-size="14" fill="#111">Todos somos familiares</text>
  <text x="1080" y="342" text-anchor="middle" font-size="12" fill="#333">face fragments only</text>
  <text x="1080" y="364" text-anchor="middle" font-size="12" fill="#333">PNG, MP4, JSON</text>
  <line x1="220" y1="78" x2="290" y2="78" stroke="#555" stroke-width="2" marker-end="url(#flow-arrow)"/>
  <line x1="220" y1="254" x2="290" y2="254" stroke="#555" stroke-width="2" marker-end="url(#flow-arrow)"/>
  <path d="M480 234 L515 234 L515 201 L550 201" fill="none" stroke="#555" stroke-width="2" marker-end="url(#flow-arrow)"/>
  <path d="M480 274 L515 274 L515 339 L550 339" fill="none" stroke="#555" stroke-width="2" marker-end="url(#flow-arrow)"/>
  <line x1="740" y1="201" x2="790" y2="201" stroke="#555" stroke-width="2" marker-end="url(#flow-arrow)"/>
  <line x1="740" y1="339" x2="790" y2="339" stroke="#555" stroke-width="2" marker-end="url(#flow-arrow)"/>
  <line x1="950" y1="201" x2="1000" y2="201" stroke="#555" stroke-width="2" marker-end="url(#flow-arrow)"/>
  <line x1="950" y1="339" x2="1000" y2="339" stroke="#555" stroke-width="2" marker-end="url(#flow-arrow)"/>
  <path d="M480 78 L970 78 L970 174 L1000 174" fill="none" stroke="#555" stroke-width="2" marker-end="url(#flow-arrow)"/>
  <path d="M970 78 L970 312 L1000 312" fill="none" stroke="#555" stroke-width="2" marker-end="url(#flow-arrow)"/>
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
- `src/desaparecidos/persons.py`: canonical disappeared-person store, missing-field computation, portrait candidate handling, selected portrait processing, and target manifest export.
- `src/desaparecidos/preprocess.py`: portrait preprocessing for local target manifests.
- `scripts/import_sitios_memoria.py`: Sitios de Memoria importer; conservative `field-fotografia` portrait selection and per-field provenance.
- `scripts/apply_portrait_overrides.py`: replaces a person's portrait from an authoritative override source and records portrait provenance.
- `scripts/audit_target_corpus.py`: reports selected portrait coverage, portrait-review needs, missing metadata fields, portrait source counts, and unresolved target-person records.
- `scripts/apply_person_metadata_overrides.py`: applies reviewed per-field metadata corrections from `data/persons/metadata-overrides.csv` and records source ids/references.
- `scripts/suggest_local_portrait_matches.py`: compares the older local portrait corpus against canonical person names and can append strong matches as review-only candidates.
- `frontend/src/App.tsx`: black four-page hash-routed GUI for targets, images, and the first two artworks.
- `data/sources.json`: tracked registry of authoritative sources and review-only candidate corpora for disappeared-person fields and portraits.
- `data/persons/disappeared.json`: canonical target-person metadata/provenance store.
- `assets/targets/disappeared/selected/`: trackable reviewed 3:4 selected portrait derivatives.
- `data/manifests/people.csv`: tracked empty people manifest template.
- `data/manifests/crawled-*.csv`: ignored crawler review manifests.
- `assets/targets/disappeared/raw/`: ignored raw portrait candidate downloads.
- `data/raw/crawl/`: ignored image store, `cache.sqlite`, and JSONL run trails.
- `data/processed/`: ignored local derivatives.
- `doc/fotos-desaparecidos/`: tracked source portrait corpus.
- `outputs/stage1/`: ignored generated stills, videos, and sidecars.

## Current capabilities

- Validate `targets`, `places`, and `people` manifests.
- Administer target-person records in the GUI: search, filter missing information or portrait-review needs, edit biographical/remains fields, add explicit online portrait candidates, process selected portraits to 3:4, and export the derived target manifest.
- Serve person-store APIs for list/get/save/delete, source registry, search-plan links, portrait candidate download, selected portrait processing/selection, and target manifest export.
- Review rows for all three manifest kinds: per-row approve/reject/reset/delete, plus checkbox selection with Select all, Select none, Approve selected, and Delete selected.
- Import disappeared-person metadata and portraits from Sitios de Memoria into the canonical store with conservative portrait selection (only the `field-fotografia` image) and `portrait_status` of `ok`/`missing`; record per-field provenance in `field_sources` against `data/sources.json`.
- Audit the target corpus from the command line with `scripts/audit_target_corpus.py`; the current audit reports 204 records, 202 selected portraits, 321 portrait candidates, 119 records needing portrait review, 187 records with at least one required-field gap, zero missing birth dates, zero missing loss dates, and two unresolved portrait gaps.
- Suggest review-only local portrait alternatives with `scripts/suggest_local_portrait_matches.py`; the current pass added 118 high-confidence local candidates from `doc/fotos-desaparecidos` without changing selected portraits or `targets.csv`.
- Crawl ordinary contemporary Uruguay pages once while independently classifying each candidate for both place and people manifests.
- Record every crawled page URL in crawl order with depth, parent, status, error, and fetch time.
- Record image candidate decisions, duplicate status, hashes, CV decision, and accepted row id.
- Avoid duplicate image variants with exact SHA-256 and perceptual hash checks.
- Classify the same cached URL separately per manifest kind and CV policy version.
- Store `source_url`, `source_page`, `crawl_run_id`, `content_sha256`, and `perceptual_hash` on crawled rows.
- Store face-region metadata for accepted `people` rows for manual review only; `people` rows now require a detected face and no fallback face box is generated.
- Reject obvious non-photo place candidates before review: flat graphics, limited-palette graphics/logos, prominent faces, and random-noise-like textures.
- Generate stills and MP4 process videos for **Todos somos familiares** from approved face regions and for **Están en todas partes** from approved place images.
- Show only patches that contribute to the reconstruction in process videos; never introduce complete source photographs or non-contributing raw candidates.
- Cap source contribution with `max_contribution_per_source`; the default is `1`, place generation permits explicit `0`/unlimited use, and people generation requires a positive cap.
- Control output block size through the GUI `Block size` slider wired to `fragment_size`.
- Record artwork/source identifiers, settings, source usage, source sequence, search trail URLs/run ids, truthful candidate counts, privacy/display policy, and video process metadata in sidecars.
- Keep URL ticker overlays on fragment assembly frames followed by a readable commemorative outro.

## Recent changes

- Replaced the scrolling dashboard with four functional hash-routed pages: Targets, Images, Todos somos familiares, and Están en todas partes. Seguimos buscando is explicitly marked as future work.
- Added `POST /api/crawl/combined`: one traversal and cached download per unique candidate now produces independent place/people CV decisions, manifests, run ids, trails, and review rows under one overall candidate cap. The legacy single-kind endpoint remains available.
- Added artwork-aware API/pipeline/CLI generation. Todos somos familiares requires approved people rows with valid face boxes and extracts fragments only from the reviewed face region; Están en todas partes consumes approved place rows. Sidecars record the artwork, source kind, and source manifest, and legacy outputs default to Están en todas partes in the GUI.
- Replaced full-source and raw-candidate video frames with a deterministic contributing-fragment field for both artworks. Only patches actually placed in the target are displayed and animated.
- Reconciled the prior merge inconsistencies: the contribution default is again `1`, place-only `0` remains unlimited, search trails fall back to manifest pages when cache trails are absent, and candidate sidecars distinguish available, selected, displayed, and omitted counts.
- Merged `origin/paper-ai-society-open-forum-import` into `import-full-disappeared-corpus`, adding the AI & Society/Open Forum drafts, source audit, summer publication plan, and paper figure SVGs under `doc/writings/`.
- Added canonical target corpus administration: `src/desaparecidos/persons.py`, person-store FastAPI routes, React Targets screen, missing-field filters, explicit portrait candidate download, selected portrait processing, source provenance display, and target-manifest export.
- Updated target corpus tracking policy: `data/persons/disappeared.json` and `assets/targets/disappeared/selected/` are trackable curated corpus paths; raw portrait downloads, rejected candidates, crawl outputs, and local generated derivatives remain ignored.
- Converted the Sitios importer and portrait override helper to 3:4 full-frame portrait preprocessing with white-border trimming, canonical person-store output, and current target manifest fields.
- Aligned root and compatibility documentation with `doc/desaparecidos-uy-project-description.md`, including the triptych structure, non-identification/privacy constraints, and search-as-process language. Replaced stale `doc/AGENTS.md` and `doc/STATUS.md` templates with canonical pointers.
- Tightened crawler CV: `people` crawling requires a detected face with a minimum face box/area; `places` crawling now accepts only conservative `place-photo` candidates and rejects flat graphics, limited-palette graphics, prominent faces, and noise-like textures. Added `CV_POLICY_VERSION=2` so old cached decisions are recomputed.
- Earlier fast raw-candidate scans were removed from the active video path when fragment-only source display was adopted; acquisition evidence remains in sidecars.
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
- Selectively adopted the useful source-cap/matcher documentation ideas from PR #1 without merging its failing pipeline rewrite: Python/API/CLI/GUI now default `max_contribution_per_source` to `1`, and `0` remains explicit unlimited use.
- Ran the first full Sitios de Memoria corpus import into `data/persons/disappeared.json` and `assets/targets/disappeared/selected/`: 204 records imported, 202 target portraits selected/exported to `data/manifests/targets.csv`, five missing/weak portraits replaced from Madres y Familiares, and the Abeledo override re-applied from Parque de la Memoria.
- Fixed Sitios/person-store metadata normalisation so embedded `Fecha de muerte` labels become explicit `date_of_death` fields instead of contaminating detention country/place fields; current canonical JSON has no embedded `Fecha de muerte` strings and 19 records with `date_of_death`.
- Added `scripts/audit_target_corpus.py` and exposed `date_of_death`, detention, and remains fields in the target-admin form.
- Audited the two remaining missing portraits. `camuyrano-bottini-mario` and `gadea-hernandez-liborio` have explicit notes recording checked public/trusted sources and remain unresolved rather than filled with unverified images.
- Set generated target CSV writers to LF line endings so regenerated `targets.csv` passes `git diff --check`.
- Added `scripts/suggest_local_portrait_matches.py` and a `local-fotos-desaparecidos` source-registry entry. Ran it with `--write --min-score 0.85`, adding 118 local review-only portrait candidates; raw-only candidates are no longer auto-selected during person-store normalisation.
- Added computed `portrait_review` metadata to person records returned by the API, exposed a Targets-screen Review filter and candidate dimensions/confidence/status, and added `--portrait-review-only` to the audit command.
- Added `place_of_death` and `field_source_refs` to the canonical person model/API/Targets screen. Death date/place now satisfy the curation loss-date/loss-place audit fields for killed cases without fabricating disappearance data, and target-manifest export falls back to reviewed death metadata when no separate disappearance location exists.
- Added tracked `data/persons/metadata-overrides.csv` plus `scripts/apply_person_metadata_overrides.py`. Applied eleven official Investigación Histórica corrections: D’Elía and O’Neill birth/place/disappearance fields, country of disappearance for both, and reviewed death places for Barry, Mata, and Camuyrano.

## Tests and verification status

Latest local verification (four-page, combined-crawl, two-artwork work):

- `.venv/bin/python -m pytest -q`: passed, 110 tests, 1 upstream Starlette/httpx deprecation warning.
- `.venv/bin/python -m compileall src tests scripts`: passed.
- `npm --prefix frontend run build`: passed (`tsc` and Vite production build).
- `zsh -n start.sh`: exited successfully with the known `nice(5)` permission warnings.
- `git diff --check`: passed.
- Built-frontend HTTP smoke on `127.0.0.1:5174`: `/` and all four hash URLs returned the Vite `index.html` with HTTP 200. Hash navigation interaction remains browser-unverified for the reasons below.

Previous target corpus metadata override verification:

- `.venv/bin/python scripts/apply_person_metadata_overrides.py --write --json`: passed; applied eleven source-backed corrections.
- `.venv/bin/python -c "from desaparecidos.persons import export_targets_manifest; print(export_targets_manifest())"`: passed; wrote 202 derived target rows from 204 person records and skipped the two known missing-portrait records.
- `.venv/bin/python scripts/audit_target_corpus.py --json`: passed; current missing-field summary is `place_of_birth: 4`, `place_of_disappearance: 131`, `remains_status: 164`, `selected_portrait: 2`, with zero missing `date_of_birth` and zero missing `date_of_disappearance` under the loss-date policy.
- `.venv/bin/python -m compileall src tests scripts`: passed.
- `.venv/bin/python -m pytest -q`: passed, 104 tests, 1 upstream Starlette/httpx deprecation warning.
- `npm --prefix frontend run build`: passed.
- `zsh -n start.sh`: exited successfully with the known `nice(5)` permission warnings.
- `git diff --check`: passed.
- Live/trusted-source checks performed: full Sitios import, Madres y Familiares portrait downloads for five records, Parque de la Memoria Abeledo override download, direct Madres list/API/guessed URL checks for unresolved portraits, broad web searches for Camuyrano/Gadea, and local official PDF text search.

Previous full local verification (source-cap default update and prior crawler/video work, before current corpus import):

- `.venv/bin/python -m compileall src tests scripts`: passed.
- `.venv/bin/python -m pytest -q`: passed, 96 tests, 1 upstream Starlette/httpx deprecation warning.
- `npm --prefix frontend run build`: passed (tsc + vite, no type errors).
- `zsh -n start.sh`: exited successfully with the known `nice(5)` permission warnings.
- `git diff --check`: passed.
- Local GUI smoke: FastAPI health responded on `http://127.0.0.1:8765`, Vite served the GUI on `http://127.0.0.1:5173/`, and `/api/persons?store=data/persons/disappeared.json` returned the empty canonical person store summary before the full import.

Earlier verification retained from the current branch reconciliation:

- Importer validated against live Sitios de Memoria pages: the Abeledo page yields no portrait (`portrait_status="missing"`) and a clean `victim_type`; four other persons resolve to their correct `field-fotografia` portraits. Parque de la Memoria override applied for Abeledo (portrait provenance `parque-de-la-memoria`).
- Git: confirmed the 348MB zip blob is gone from all refs (`git rev-list --objects --all` has no match) and `.git` is ~577MB.
- Local smoke: backend health on `127.0.0.1:8766` passed; built frontend served from `frontend/dist` on `127.0.0.1:5174` returned HTTP 200; static checks confirmed black CSS background, no primary `Download` panel text in the React app, Utilities modal demo controls, crawler `places/people`, and both generation sliders.

Browser-rendered smoke is not complete in this environment: the Browser plugin is unavailable, neither the project nor the existing temporary tool directory contains a Playwright executable, the previously documented Homebrew `playwright` executable points to a missing Python 3.11 interpreter, and `safaridriver --enable` requires an interactive password. No browser dependency was added solely for this check.

## Known issues, risks, and limitations

- Full browser-pixel verification remains blocked until Playwright or Safari WebDriver is repaired locally.
- `zsh -n start.sh` reports `nice(5)` permission warnings even though syntax validation exits successfully.
- The GUI static smoke uses the built output, not Vite dev server, because Vite port binding was blocked by sandbox permissions.
- The target corpus is not yet complete: 187 of 204 records still have at least one required-field gap under the current strict missing-field policy, mostly `remains_status` and `place_of_disappearance`. Birth-date and loss-date gaps are currently resolved; four birthplace gaps remain.
- Two selected portraits remain unresolved after the current public/trusted-source audit: `camuyrano-bottini-mario` and `gadea-hernandez-liborio`.
- The older `data/manifests/local-targets.csv`/`doc/fotos-desaparecidos` corpus has 142 approved local portraits. A name-match pass added 118 review-only candidates to canonical records, and the target-admin GUI now flags records needing portrait review, but the candidates remain unselected until reviewed and processed.
- People crawling and Todos somos familiares generation are internal and review-gated. They perform no identity matching; generation uses only reviewed face boxes and fragment fields, but outputs still require human privacy review before publication.
- Crawler CV is stricter but still heuristic and local; manual review remains mandatory and false positives/negatives are expected.
- Process videos require local `ffmpeg` with H.264/libx264 support.
- Generated imagery, raw crawls, JSONL trails, raw portrait candidates, rejected candidates, temporary processed target copies, and review manifests remain ignored local data. Reviewed selected target portraits under `assets/targets/disappeared/selected/` are the explicit corpus exception.

## Pending tasks

- Resolve or explicitly close the two remaining missing portrait gaps with trusted sources only; do not use unverified web images as selected portraits.
- Continue filling missing person metadata, prioritising `remains_status`, `place_of_disappearance`, and the four remaining missing birthplaces.
- Review the 119 records flagged by `portrait_review` / the Targets Review filter; select and process only the local candidates that are verified as better portraits.
- Repair or install a working Playwright/Safari WebDriver path for visual GUI regression checks.
- Run a full manual GUI smoke in a browser once browser automation is available.
- Review the merged `doc/DDHH/` archive additions and `doc/writings/` publication materials for repository size and publication-readiness policy if needed.
- Keep checking that crawler presets stay mundane and contemporary rather than memory/archive oriented.
- Continue improving CV thresholds only with manual review evidence from real crawl runs.

## Next steps

- Use `scripts/audit_target_corpus.py` and the Targets screen to work down missing fields and unresolved portraits.
- Compare trusted source portraits and reviewed local portraits to choose the best selected portrait per person.
- Use the Utilities modal only for synthetic fixture workflows; keep primary GUI space dedicated to the real artwork workflow.
- Use crawled page trails and local image-candidate events as provenance evidence; generated frames show only contributing fragments.

## Longer-term steps

- Add a reliable automated browser smoke suite for the GUI.
- Continue strengthening internal people-source privacy tooling without identity matching.
- Implement **Seguimos buscando** only after its traversal-specific interaction and source policy are designed; it is not part of the current runtime.
- Decide whether future gallery installation should run the live crawler/search process or replay documented crawl trails.
- Revisit crawler persistence policy after the review workflow stabilises.

## Decisions and rationale

- `targets` remain only the disappeared-person portrait corpus.
- `data/persons/disappeared.json` is the canonical disappeared-person data store; `targets.csv` is a derived generation manifest.
- `data/persons/metadata-overrides.csv` is the tracked correction ledger for source-backed metadata fixes that should survive re-imports.
- Death metadata stays separate from disappearance metadata. For killed cases with no separate disappearance date/place, audit/export uses `date_of_death`/`place_of_death` as the loss date/place rather than copying them into disappearance fields.
- Reviewed selected target portrait derivatives are allowed under `assets/targets/disappeared/selected/`; raw downloads and temporary candidates remain ignored.
- Raw-only portrait candidates are never selected automatically. Local filename matches are candidate evidence, not identity/provenance proof.
- `people` is separate from `targets` so contemporary public people imagery cannot be confused with disappeared-person portraits.
- The GUI has separate generation pages for the first two artworks. The artwork identifier, rather than a free source selector, determines whether a request consumes `people` or `places` rows.
- A combined crawl shares traversal/download work but assigns separate run ids and trails so downstream artwork provenance cannot mix the two source kinds.
- People fragments come only from a valid reviewed face box. Both artwork videos display contributing fragments only; complete source and rejected/non-contributing candidate images remain out of generated frames.
- Crawler presets default to same-domain traversal; cross-domain remains a manual opt-in.
- Crawler CV cache entries are versioned; old decisions are recomputed rather than silently reused after policy changes.
- Download controls are hidden from the primary GUI because they are no longer central to the workflow, but API/CLI support remains for automation.
- `max_contribution_per_source` defaults to `1` so a source image cannot dominate by default; `0` remains explicit unlimited use for controlled place tests but is rejected for people generation.
- URL ticker frames are preserved during fragment assembly; outro cards remain readable and untickered.

## Documentation alignment notes

- `README.md` describes the four routed workspaces, combined dual classification, separate artwork generation, face-region-only people fragments, fragment-only videos, contribution policy, and JSON sidecars.
- `AGENTS.md` records current safety invariants, the canonical person-store/metadata-override/selected-portrait corpus exceptions, local portrait candidate review policy, strict people/place CV expectations, and non-identification requirements.
- `doc/writings/` now contains merged AI & Society/Open Forum drafts, figures, source audit, and publication planning material.
- `CLAUDE.md` remains a short pointer to `AGENTS.md`, `STATUS.md`, and the project description.

Last updated: 2026-06-20 14:45 GMT-3
