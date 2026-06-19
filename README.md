# desaparecidos.uy

`desaparecidos.uy` is a computational memorial artwork series by Tomas Laurenzo. It reconstructs public images of detained-disappeared persons connected to Uruguay from fragments of the country that survived them: people, places, streets, walls, landscapes, and public visual infrastructures.

The project is not an archive, forensic tool, biometric system, deepfake, or resurrection medium. It is an artistic system for making the continuing structure of disappearance perceptible. The created videos aim to metaphorically represent and reenact the continuing search for the disappeared.

The triptych is:

- **Todos somos familiares**: internal face-fragment work using contemporary public images of people without identity matching, classification, or representation of source persons.
- **Están en todas partes**: the current place-fragment prototype using Uruguay's places, surfaces, streets, landscapes, and material environments.
- **Seguimos buscando**: traversal/search work where scanning and continuing search become the temporal structure of the piece.

The full draft project statement is in [doc/desaparecidos-uy-project-description.md](doc/desaparecidos-uy-project-description.md).

## Stage 1: Están en todas partes

Stage 1 implements the place-based prototype. Public target portraits are reconstructed from fragments extracted from curated images of Uruguayan places, surfaces, streets, landscapes, and material environments.

The prototype provides:

- manifest-driven target, place-source, and internal people-source ingestion;
- a canonical disappeared-person JSON store for target curation, missing-field review, portrait candidate provenance, and target-manifest export;
- local target-portrait preprocessing that trims white scan borders/caption margins and writes 3:4 processed copies;
- provenance and checksum recording for downloaded files;
- review gates before imagery can be used;
- a bounded recursive crawler for explicit user-supplied or preset pages;
- a persistent crawl cache and crawl trail so page traversal can be replayed;
- exact and perceptual duplicate detection so repeated image variants do not enter manifests;
- Stage 1 place-source crawling and internal Stage 2 people-source crawling;
- a preset menu of ordinary contemporary Uruguay starting pages;
- stricter local OpenCV/NumPy crawler gating: `people` rows require a detected face and `places` rows require photo-like non-face scene material;
- deterministic, vectorised fragment matching using a deliberately modest six-dimensional colour/contrast/edge descriptor and L2 nearest-neighbour search;
- an active default per-source contribution cap so no single source image can dominate a generated portrait;
- still PNG outputs and optional browser-playable H.264 MP4 process videos with a fast search-candidate scan, bottom URL ticker, and commemorative outro;
- JSON sidecars for generated outputs;
- a localhost-only GUI so the workflow can be run without typing CLI commands.

Generated outputs, raw downloads, crawl caches, crawl trails, rejected candidates, temporary processed copies, and review manifests are intentionally ignored by git. The curated portrait collection in `doc/fotos-desaparecidos/`, the canonical target store at `data/persons/disappeared.json`, and reviewed selected portrait derivatives under `assets/targets/disappeared/selected/` are trackable project corpus files.

## Local GUI

The normal workflow is the local web GUI.

```bash
./start.sh
```

The launcher creates or reuses a local Python environment, installs Python and frontend dependencies when needed, starts the FastAPI backend, starts the Vite GUI, and opens the browser. It prefers backend port `8765` and frontend port `5173`, but automatically moves to free localhost ports when those are already occupied.

If the GUI reports that the server is not the FastAPI backend, close the old launcher window and run `./start.sh` again. The launcher prints the exact backend and frontend URLs it selected.

The GUI can administer target person records, validate manifests, crawl user-supplied or preset pages for candidate images, approve/reject/reset/delete individual manifest rows, select rows with checkboxes to bulk-approve or bulk-delete the selection (Select all, Select none, Approve selected, Delete selected), click a target thumbnail to set the working portrait, run still/video generation, inspect logs, review sidecars, and delete selected or all generated outputs. Crawling has its own running state, so review remains usable while a crawl is running.

The **Targets** screen edits `data/persons/disappeared.json`. It lists disappeared-person records, filters records with missing information, edits full name, birth/disappearance/remains fields, stores source/provenance notes, downloads explicit portrait candidates by URL, processes the selected candidate into a white-border-trimmed 3:4 portrait, and exports the derived `targets.csv` manifest. Online acquisition is controlled: trusted sources in `data/sources.json` are preferred, general web results are candidate evidence only, and arbitrary web images are never made authoritative without review.

Crawler controls expose only `places` and `people`. `targets` remain the disappeared-person portrait corpus. The `/api/download` route and CLI download command still exist, but the primary GUI no longer shows a download panel. Synthetic demo fixture controls are in the compact Utilities modal.

The GUI remembers the target, place, people, output, and crawl manifest paths across sessions. Crawler presets use mundane contemporary Uruguay sources such as Montevideo tourism/events/news and `gub.uy` public news pages rather than memory-site pages.

Generation controls include:

- `Block size`, wired to `fragment_size` (`8..128`, step `4`);
- `Max tiles per source`, wired to `max_contribution_per_source`; the running backend normalises `0` or unset legacy values to the active ethical default of `240`, not to unlimited use;
- `reuse_limit`, `output_width`, seed, still generation, and video generation.

Generated videos show the search before the selection: local crawl candidates that do not contribute are flashed quickly in crawl order, then a usable source is introduced full-screen, sampled fragment regions are highlighted, and those fragments animate into their actual positions in the reconstructed portrait. Crawler page URLs are written along the bottom during search/assembly frames, and the video finishes with a commemorative outro.

## Manual Setup

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
npm --prefix frontend install
```

Installing the package pulls in `opencv-python-headless`, used for crawler face/scene gating; no model download is required.

Video generation requires `ffmpeg` with H.264/libx264 support. On macOS with Homebrew:

```bash
brew install ffmpeg
```

Run the backend:

```bash
python -m desaparecidos serve --host 127.0.0.1 --port 8765
```

Run the GUI:

```bash
npm --prefix frontend run dev -- --host 127.0.0.1 --port 5173
```

## CLI

The CLI remains available for automation and testing.

```bash
python -m desaparecidos validate --targets data/manifests/targets.csv --sources data/manifests/places.csv
python -m desaparecidos download --manifest data/manifests/places.csv --kind places
python -m desaparecidos download --manifest data/manifests/people.csv --kind people
python -m desaparecidos run-stage1 --targets data/manifests/targets.csv --sources data/manifests/places.csv --output outputs/stage1 --seed 17 --max-contribution-per-source 240 --search-scan-frames-per-candidate 2 --search-scan-max-candidates 120
python scripts/build_targets_manifest.py --source doc/fotos-desaparecidos --output data/manifests/local-targets.csv --processed-root data/processed/targets --aspect 3:4
```

The Sitios de Memoria importer and portrait override tooling remain available for corpus preparation. The importer selects a portrait only from a person page's `field-fotografia` container, recording `portrait_status` as `ok` or `missing` rather than importing work posters or materials as a face. It writes the canonical person store at `data/persons/disappeared.json`, raw downloads under ignored `assets/targets/disappeared/raw/`, selected 3:4 derivatives under `assets/targets/disappeared/selected/`, and the derived `data/manifests/targets.csv`. Each person record carries a `field_sources` map noting which source (see the tracked `data/sources.json` registry) is authoritative for each field and for the portrait; `scripts/apply_portrait_overrides.py` swaps in a portrait from a better source (for example Parque de la Memoria for Argentine cases) and records that provenance.

## Manifests and Review

Tracked manifest templates live in `data/manifests/`.

- Target manifests describe disappeared persons' public images and source provenance.
- The canonical target corpus is `data/persons/disappeared.json`; target manifests are derived export files for generation compatibility.
- Place manifests describe place/surface images and reuse terms.
- People manifests describe contemporary public images of people for internal Stage 2 exploration. They are review-gated source-corpus material, not disappeared-person targets, and no identity matching is performed.
- Public availability is not treated as blanket permission. Source images of living people are privacy-sensitive; public release requires legal/ethical review, deletion or exclusion procedures, and output review so no living source person appears recognisably.
- `scripts/build_targets_manifest.py` remains available for ignored local manifests from `doc/fotos-desaparecidos/`. The newer target-admin workflow stores reviewed person metadata and selected portraits in the canonical corpus, then exports `targets.csv`.
- Rows must use `review_status=approved` before the Stage 1 pipeline can use the corresponding local file.
- The crawler fetches only page URLs entered or selected in the GUI, follows links within depth/page/image limits, honours `robots.txt` by default, and defaults preset runs to same-domain traversal.
- `people` crawling now requires an actual detected face before a pending row is written. It stores only the largest face box for review and does not infer identity, category, demographic traits, or relation to a disappeared person.
- `places` crawling uses conservative local statistics to reject flat graphics, logos/posters, prominent faces, and random-noise-like textures before manual review. This is a heuristic photo gate, not a semantic scene recogniser.
- The crawler saves discovered images under ignored `data/raw/crawl/store/`, records cache/trail data in ignored `data/raw/crawl/cache.sqlite`, exports each run under ignored `data/raw/crawl/runs/<run_id>.jsonl`, and appends pending rows to ignored `data/manifests/crawled-*.csv`.
- Crawled rows keep the direct image URL in `source_url`, the page where it was found in `source_page`, and crawl metadata (`crawl_run_id`, `content_sha256`, `perceptual_hash`). People rows also keep the largest accepted face-region box for manual review.
- Exact SHA-256 and perceptual hashes prevent repeated image variants from being added to manifests. Cache classification is per manifest kind, so one URL can be evaluated separately as a place or people candidate without re-downloading.
- Stage 1 matching uses non-overlapping 24-pixel tiles by default. Each fragment is described by mean RGB, luminance contrast, and horizontal/vertical edge energy, then matched by deterministic L2 nearest-neighbour search. This technical modesty is intentional: it keeps seams, mismatches, and fragment boundaries visible rather than smoothing the output into a synthetic restoration.
- `reuse_limit` is enforced per extracted source fragment. `max_contribution_per_source` caps how many output tiles any single source image fills; GUI/API/CLI generation now normalises `0` or unset legacy values to `240`, and infeasible caps fail before generation.
- Video sidecars record settings, source usage, source sequence, tile counts, per-source animated fragment counts, video process metadata, search-trail URLs/run ids, and displayed search-candidate frame references used by the fast scan and bottom ticker.
- Output deletion in the GUI removes local sidecars and sibling still/video files from the selected output directory.

Downloaded and crawled files are written under `data/raw/`; processed target copies are written under `data/processed/`; generated stills, videos, and sidecars are written under `outputs/stage1/`. These directories are ignored.

## Verification

```bash
python -m compileall src tests
python -m pytest -q
npm --prefix frontend run build
zsh -n start.sh
git diff --check
```

## Repository Notes

Agents and contributors must read [AGENTS.md](AGENTS.md) and keep [STATUS.md](STATUS.md) current after meaningful changes.
