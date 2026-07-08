# desaparecidos.uy

`desaparecidos.uy` is a computational memorial artwork series by Tomas Laurenzo. It reconstructs public images of detained-disappeared persons connected to Uruguay from fragments of the country that survived them: people, places, streets, walls, landscapes, and public visual infrastructures.

The project is not an archive, forensic tool, biometric system, deepfake, or resurrection medium. It is an artistic system for making the continuing structure of disappearance perceptible. The created videos aim to metaphorically represent and reenact the continuing search for the disappeared.

The triptych is:

- **Todos somos familiares**: internal face-fragment work using contemporary public images of people without identity matching, classification, or representation of source persons.
- **Están en todas partes**: the current place-fragment prototype using Uruguay's places, surfaces, streets, landscapes, and material environments.
- **Seguimos buscando**: traversal/search work where scanning and continuing search become the temporal structure of the piece.

The full draft project statement is in [doc/desaparecidos-uy-project-description.md](doc/desaparecidos-uy-project-description.md).

## Current implementation

The runtime supports the three artwork workspaces. Public target portraits are reconstructed from reviewed people or place fragments in the first two works, while the third combines reviewed street-level traversal imagery with progressively available fragments.

The prototype provides:

- manifest-driven target, place-source, and internal people-source ingestion;
- a canonical disappeared-person JSON store for target curation, incomplete-record review, portrait candidate provenance, and target-manifest export;
- local target-portrait preprocessing that trims white scan borders/caption margins and writes 3:4 processed copies;
- provenance and checksum recording for downloaded files;
- review gates before imagery can be used;
- a bounded recursive crawler for explicit user-supplied or preset pages;
- a persistent crawl cache and crawl trail so page traversal can be replayed;
- exact and perceptual duplicate detection so repeated image variants do not enter manifests;
- one combined traversal that classifies each downloaded candidate independently as a place and as a contemporary-people source;
- a preset menu of ordinary contemporary Uruguay starting pages;
- stricter local OpenCV/NumPy crawler gating: `people` rows require a detected face and `places` rows require photo-like non-face scene material;
- deterministic, vectorised fragment matching using a deliberately modest six-dimensional colour/contrast/edge descriptor and L2 nearest-neighbour search;
- an active default per-source contribution cap so no single source image can dominate a generated portrait;
- separate generation workspaces for **Todos somos familiares** and **Están en todas partes**;
- a provider-neutral street-level traversal workflow for **Seguimos buscando**, with Mapillary discovery, local acquisition, frame review, and deterministic offline video rendering;
- still PNG outputs and optional browser-playable H.264 MP4 process videos that reveal an approved place source or reviewed people face region, fade away everything except contributing fragments, transfer those fragments to the portrait, retain a bottom URL ticker, and finish with a commemorative outro;
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

The GUI has five hash-routed workspaces: **Targets**, **Images**, **Todos somos familiares**, **Están en todas partes**, and **Seguimos buscando**. Each artwork has its own generation page and filtered output gallery. Browser back/forward and refresh preserve the selected workspace.

The **Targets** screen edits `data/persons/disappeared.json`. It lists disappeared-person records, filters **Incomplete** records, edits full name, birth/disappearance/remains fields, stores source/provenance notes, downloads explicit portrait candidates by URL, processes the selected candidate into a white-border-trimmed 3:4 portrait, and explicitly exports the derived `targets.csv` manifest. “Incomplete” means one or more required curation fields are absent; it does not describe the person's disappeared status. Target administration and target-image review link exact canonical IDs and legacy rows with matching portrait provenance. Clicking a review image or its selection checkbox selects and scrolls to the corresponding person, and selecting a person selects and scrolls to the corresponding review image. A cross-panel selection clears a filter/query that would otherwise hide the selected person. Unsaved editor changes require confirmation before another target is selected. The Target administration toolbar stays fixed while its person/editor content scrolls.

The **Images** workspace crawls every page once for both `places` and `people`, downloads each candidate once, applies the two CV policies independently, and appends accepted candidates to separate pending manifests. Manual approval remains mandatory. `targets` remain the disappeared-person portrait corpus. The `/api/download` route and CLI download command still exist, but the primary GUI no longer shows a download panel. Synthetic demo fixture controls are in the compact Utilities modal.

The **Seguimos buscando** workspace authors a route interactively, imports GeoJSON/GPX, or runs autonomously. Autonomous mode has two scopes. With a **drawn region**, discovery divides the region's bounding box into grid cells and selects one coherent capture sequence per cell — a walk — joined by direct jump cuts and recorded as `walks` metadata. With the **all-Uruguay scope** (the autonomous default), the walk chooses its own places: localities are sampled with population-proportional weight from a coarse tracked gazetteer (`src/desaparecidos/geography.py`), a configurable rural share instead samples a uniform point on Uruguayan land, and each sampled place becomes a small search cell; cells without street-level coverage are skipped until enough coherent walks are found. The chosen places are recorded as `places`/`place_name` metadata and the route geometry becomes the national path through them. The backend discovers Mapillary sequence metadata and caches a bounded set of frames under ignored `data/raw/traversals/`.

Frame approval supports two policies. Manual review in the contact sheet remains the default for drawn/imported routes. Acquisition may instead auto-approve frames that pass the local CV place gate (`auto_approve`, the GUI default) — an explicit artist decision recorded in `AGENTS.md`; auto-approved frames carry `review_policy: "auto-cv-accepted"`, stay reversible in frame review, and a manual decision always survives re-acquisition. Rendering follows captured sequence order, inserts direct jump cuts across sequence gaps, and supports traversal overlay, alternating traversal/assembly, and split-screen composition at a default output quality of 1920 px / 24 fps. Single-target and ordered multi-target videos are supported; the ordered mode splits the walk into contiguous segments, one per target. Assembly is incremental: as the walk reaches each frame, its fragments join the found pool and a proportional share of the still-empty portrait tiles is filled with the best-matching found fragment, so the face is assembled strictly from the bits found so far (`assembly_policy: "incremental-found-fragments"` in sidecars) and no tile is ever matched against a frame the walk has not reached.

The **Search Uruguay & generate** button (backed by `POST /api/traversals/auto`) runs the whole third-artwork flow in one step: sample places, discover coherent walks, acquire frames, auto-approve CV-accepted frames, and render the video. Every stage's record stays on disk and the frames remain open to review afterwards; outputs stay `internal_unreviewed`.

The provider-neutral traversal API is `GET /api/traversals`, `GET /api/traversals/{id}`, `POST /api/traversals/discover`, `POST /api/traversals/acquire`, `POST /api/traversals/auto`, `POST /api/traversals/{id}/frames/review`, and `POST /api/generate/traversal`. Route records and third-artwork sidecars use `artwork: "seguimos-buscando"`; older sidecars without an artwork continue to display as **Están en todas partes**.

The GUI remembers the target, place, people, output, and crawl manifest paths across sessions. Crawler presets use mundane contemporary Uruguay sources such as Montevideo tourism/events/news and `gub.uy` public news pages rather than memory-site pages.

Generation controls include:

- `Block size`, wired to `fragment_size` (`8..128`, step `4`);
- `Max tiles per source`, wired to `max_contribution_per_source`; the default is `1`, `0` means unlimited for place generation, and people generation requires a positive cap;
- `Source fragment layout`, selecting either a regular grid or a deterministic non-grid scatter derived from each fragment's matched target section;
- `reuse_limit`, `output_width`, seed, still generation, and video generation.

For each contributing source, generated videos begin with the approved source region at full opacity, quickly fade non-contributing pixels, and transfer the remaining fragments into their actual target positions. The `grid` mode stages selected fragments in a regular field before transfer; the `match` mode uses a deterministic non-grid scatter derived only from each fragment's matched target section. Place videos may reveal the complete approved place image. People videos reveal only the reviewed detected face region used for extraction, never the surrounding source photograph. Rejected and non-contributing candidate images remain excluded. Crawler page URLs remain visible along the bottom during assembly, and the video finishes with a commemorative outro.

Each generated PNG/MP4 has an adjacent JSON **sidecar**. The sidecar is output metadata: it records the artwork, source kind and manifest, target, settings, source/fragment usage, output paths, crawl trail, and candidate counts without modifying the media file.

## Manual Setup

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
npm --prefix frontend install
```

Installing the package pulls in `opencv-python-headless`, used for crawler face/scene gating; no model download is required.

Mapillary route discovery requires a backend-only access token:

```bash
export MAPILLARY_ACCESS_TOKEN='...'
```

The token is sent only in the Mapillary API authorisation header and is never stored in route metadata, browser state, output sidecars, or logs. The frontend uses MapLibre GL JS with attributed OpenStreetMap tiles for route authoring; MapLibre is the production dependency added for the interactive map.

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
python -m desaparecidos run-stage1 --artwork estan-en-todas-partes --targets data/manifests/targets.csv --sources data/manifests/places.csv --output outputs/stage1 --seed 17 --max-contribution-per-source 1
python -m desaparecidos run-stage1 --artwork todos-somos-familiares --targets data/manifests/targets.csv --sources data/manifests/people.csv --output outputs/stage1 --seed 17 --max-contribution-per-source 1
python -m desaparecidos run-traversal --traversal route-ID --target-id person-ID --targets data/manifests/targets.csv --composition overlay --duration 60 --fps 24 --output-width 1920
python scripts/build_targets_manifest.py --source doc/fotos-desaparecidos --output data/manifests/local-targets.csv --processed-root data/processed/targets --aspect 3:4
python scripts/import_sitios_memoria.py --refresh-bios-only
```

The Sitios de Memoria importer and portrait override tooling remain available for corpus preparation. The importer selects a portrait only from a person page's `field-fotografia` container, recording `portrait_status` as `ok` or `missing` rather than importing work posters or materials as a face. Biography extraction is restricted to the first `field--name-body` inside the person `article`; navigation, page chrome, global blocks, and footer bodies are excluded. `--refresh-bios-only` updates only canonical biographies and their field provenance, preserving curated metadata and portrait decisions. Biography text is not currently used by video generation and requires editorial review plus a display-length policy before integration.

The importer writes the canonical person store at `data/persons/disappeared.json`, raw downloads under ignored `assets/targets/disappeared/raw/`, selected 3:4 derivatives under `assets/targets/disappeared/selected/`, and the derived `data/manifests/targets.csv`. Each person record carries a `field_sources` map noting which source (see the tracked `data/sources.json` registry) is authoritative for each field and for the portrait; `scripts/apply_portrait_overrides.py` swaps in a portrait from a better source (for example Parque de la Memoria for Argentine cases) and records that provenance.

## Manifests and Review

Tracked manifest templates live in `data/manifests/`.

- Target manifests describe disappeared persons' public images and source provenance.
- The canonical target corpus is `data/persons/disappeared.json`; target manifests are derived export files for generation compatibility.
- Place manifests describe place/surface images and reuse terms.
- People manifests describe contemporary public images of people for internal Stage 2 exploration. They are review-gated source-corpus material, not disappeared-person targets, and no identity matching is performed.
- Public availability is not treated as blanket permission. Source images of living people are privacy-sensitive; public release requires legal/ethical review, deletion or exclusion procedures, and output review so no living source person appears recognisably.
- `scripts/build_targets_manifest.py` remains available for ignored local manifests from `doc/fotos-desaparecidos/`. The newer target-admin workflow stores reviewed person metadata and selected portraits in the canonical corpus, then exports `targets.csv`.
- Rows must use `review_status=approved` before the Stage 1 pipeline can use the corresponding local file.
- The combined crawler fetches only page URLs entered or selected in the GUI, follows links within depth/page/image limits, honours `robots.txt` by default, defaults preset runs to same-domain traversal, and applies the total-image cap to unique candidates inspected across both classifications.
- `people` crawling now requires an actual detected face before a pending row is written. It stores only the largest face box for review and does not infer identity, category, demographic traits, or relation to a disappeared person.
- `places` crawling uses conservative local statistics to reject flat graphics, logos/posters, prominent faces, and random-noise-like textures before manual review. This is a heuristic photo gate, not a semantic scene recogniser.
- The crawler saves discovered images under ignored `data/raw/crawl/store/`, records cache/trail data in ignored `data/raw/crawl/cache.sqlite`, exports each run under ignored `data/raw/crawl/runs/<run_id>.jsonl`, and appends pending rows to ignored `data/manifests/crawled-*.csv`.
- Crawled rows keep the direct image URL in `source_url`, the page where it was found in `source_page`, and crawl metadata (`crawl_run_id`, `content_sha256`, `perceptual_hash`). People rows also keep the largest accepted face-region box for manual review.
- Exact SHA-256 and perceptual hashes prevent repeated image variants from being added to manifests. Cache classification is per manifest kind, so one URL can be evaluated separately as a place or people candidate without re-downloading.
- Stage 1 matching uses non-overlapping 24-pixel tiles by default. Each fragment is described by mean RGB, luminance contrast, and horizontal/vertical edge energy, then matched by deterministic L2 nearest-neighbour search. This technical modesty is intentional: it keeps seams, mismatches, and fragment boundaries visible rather than smoothing the output into a synthetic restoration.
- `reuse_limit` is enforced per extracted source fragment. `max_contribution_per_source` caps how many output tiles any single source image fills; people generation rejects unlimited contribution, and infeasible caps fail before generation.
- Video sidecars record the artwork, source kind/manifest, settings, source usage, source sequence, tile counts, process metadata, search-trail URLs/run ids, and available/selected/displayed/omitted candidate counts. Raw candidate images are not displayed.
- Output deletion in the GUI removes local sidecars and sibling still/video files from the selected output directory.

Downloaded and crawled files are written under `data/raw/`; processed target copies are written under `data/processed/`; generated stills, videos, and sidecars are written under `outputs/stage1/`. These directories are ignored.

## Verification

```bash
python -m compileall src tests
python -m pytest -q
npm --prefix frontend run build
npm --prefix frontend test
zsh -n start.sh
git diff --check
```

## Repository Notes

Agents and contributors must read [AGENTS.md](AGENTS.md) and keep [STATUS.md](STATUS.md) current after meaningful changes.
