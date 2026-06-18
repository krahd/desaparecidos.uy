# desaparecidos.uy - Project Status

Last updated: 2026-06-17 20:31 GMT-3

## Project purpose

`desaparecidos.uy` is a computational memorial artwork series about the persistence of disappearance in Uruguay's present. Stage 1 focuses on **Estan en todas partes**, a place-based prototype that reconstructs public target portraits from fragments of Uruguayan places and surfaces.

## Current implementation state

The repository now contains the Stage 1 local software prototype: a Python pipeline with a vectorised fragment matcher and an optional per-source contribution cap, a FastAPI localhost backend, a React/Vite GUI, manifest templates, tests, a macOS launcher, a GUI-accessible synthetic demo fixture path, a bounded recursive cross-domain page-image crawler with OpenCV computer-vision gating and a persistent SQLite/content-addressed cache, generated-output deletion controls, and browser-playable H.264 process-video rendering when `ffmpeg` is available.

## Active focus

Review real target/place manifests and crawler-produced pending rows before introducing non-synthetic imagery into generation, while keeping raw imagery and generated outputs out of version control.

## Architecture overview

The project is organised as a localhost tool. The frontend calls a local API. The API validates manifests, performs bounded recursive image crawling seeded by user-supplied or preset URLs (link-following within depth/page/image caps, cross-domain optional, robots-aware, computer-vision filtered, cached to avoid re-downloads), updates row review status individually or in bulk, deletes selected generated outputs on request, and invokes reusable Python pipeline code. The pipeline reads approved local inputs and writes ignored outputs plus JSON sidecars. Video generation uses the same assembly trace as still generation: each used source image is introduced full-screen, sampled fragment regions are highlighted, and fragments animate into their actual positions in the reconstructed portrait.

### Architecture diagram

The current architecture is a local-only workflow with no public network service.

<svg width="760" height="250" viewBox="0 0 760 250" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="arch-title arch-desc">
  <title id="arch-title">Stage 1 local architecture</title>
  <desc id="arch-desc">React GUI talks to a localhost FastAPI backend, which uses the Python pipeline to read manifests and write generated outputs.</desc>
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="#555" />
    </marker>
  </defs>
  <rect x="30" y="50" width="150" height="70" rx="6" fill="#f7f7f5" stroke="#777" />
  <text x="105" y="82" text-anchor="middle" font-family="Arial, sans-serif" font-size="14">React GUI</text>
  <text x="105" y="102" text-anchor="middle" font-family="Arial, sans-serif" font-size="12">localhost:5173</text>
  <rect x="300" y="50" width="170" height="70" rx="6" fill="#f7f7f5" stroke="#777" />
  <text x="385" y="80" text-anchor="middle" font-family="Arial, sans-serif" font-size="14">FastAPI backend</text>
  <text x="385" y="101" text-anchor="middle" font-family="Arial, sans-serif" font-size="12">localhost:8765</text>
  <rect x="570" y="50" width="150" height="70" rx="6" fill="#f7f7f5" stroke="#777" />
  <text x="645" y="82" text-anchor="middle" font-family="Arial, sans-serif" font-size="14">Python pipeline</text>
  <text x="645" y="102" text-anchor="middle" font-family="Arial, sans-serif" font-size="12">Stage 1</text>
  <rect x="170" y="165" width="160" height="55" rx="6" fill="#fff" stroke="#999" />
  <text x="250" y="188" text-anchor="middle" font-family="Arial, sans-serif" font-size="13">Manifests</text>
  <text x="250" y="206" text-anchor="middle" font-family="Arial, sans-serif" font-size="11">data/manifests</text>
  <rect x="430" y="165" width="170" height="55" rx="6" fill="#fff" stroke="#999" />
  <text x="515" y="188" text-anchor="middle" font-family="Arial, sans-serif" font-size="13">Ignored outputs</text>
  <text x="515" y="206" text-anchor="middle" font-family="Arial, sans-serif" font-size="11">outputs/stage1</text>
  <line x1="180" y1="85" x2="292" y2="85" stroke="#555" stroke-width="2" marker-end="url(#arrow)" />
  <line x1="470" y1="85" x2="562" y2="85" stroke="#555" stroke-width="2" marker-end="url(#arrow)" />
  <line x1="250" y1="165" x2="330" y2="122" stroke="#777" stroke-width="2" marker-end="url(#arrow)" />
  <line x1="610" y1="122" x2="545" y2="165" stroke="#777" stroke-width="2" marker-end="url(#arrow)" />
</svg>

### Flow chart

The Stage 1 flow requires manual review before generation.

<svg width="760" height="180" viewBox="0 0 760 180" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="flow-title flow-desc">
  <title id="flow-title">Stage 1 data flow</title>
  <desc id="flow-desc">Manifest rows are validated, reviewed, assembled into outputs, and then inspected before publication.</desc>
  <defs>
    <marker id="flow-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="#555" />
    </marker>
  </defs>
  <rect x="25" y="55" width="120" height="60" rx="6" fill="#f7f7f5" stroke="#777" />
  <text x="85" y="82" text-anchor="middle" font-family="Arial, sans-serif" font-size="13">Manifests</text>
  <text x="85" y="101" text-anchor="middle" font-family="Arial, sans-serif" font-size="11">targets / places</text>
  <rect x="185" y="55" width="120" height="60" rx="6" fill="#f7f7f5" stroke="#777" />
  <text x="245" y="82" text-anchor="middle" font-family="Arial, sans-serif" font-size="13">Validate</text>
  <text x="245" y="101" text-anchor="middle" font-family="Arial, sans-serif" font-size="11">fields and paths</text>
  <rect x="345" y="55" width="120" height="60" rx="6" fill="#f7f7f5" stroke="#777" />
  <text x="405" y="82" text-anchor="middle" font-family="Arial, sans-serif" font-size="13">Review gate</text>
  <text x="405" y="101" text-anchor="middle" font-family="Arial, sans-serif" font-size="11">approved only</text>
  <rect x="505" y="55" width="120" height="60" rx="6" fill="#f7f7f5" stroke="#777" />
  <text x="565" y="82" text-anchor="middle" font-family="Arial, sans-serif" font-size="13">Generate</text>
  <text x="565" y="101" text-anchor="middle" font-family="Arial, sans-serif" font-size="11">still / video</text>
  <rect x="665" y="55" width="70" height="60" rx="6" fill="#f7f7f5" stroke="#777" />
  <text x="700" y="82" text-anchor="middle" font-family="Arial, sans-serif" font-size="13">Inspect</text>
  <text x="700" y="101" text-anchor="middle" font-family="Arial, sans-serif" font-size="11">outputs</text>
  <line x1="145" y1="85" x2="177" y2="85" stroke="#555" stroke-width="2" marker-end="url(#flow-arrow)" />
  <line x1="305" y1="85" x2="337" y2="85" stroke="#555" stroke-width="2" marker-end="url(#flow-arrow)" />
  <line x1="465" y1="85" x2="497" y2="85" stroke="#555" stroke-width="2" marker-end="url(#flow-arrow)" />
  <line x1="625" y1="85" x2="657" y2="85" stroke="#555" stroke-width="2" marker-end="url(#flow-arrow)" />
</svg>

### Crawler ingestion flow

Seed pages are crawled with bounded link-following, computer-vision filtered, cached so identical images are not re-downloaded, and written as pending rows that still pass through the manual review gate before any generation.

<svg width="900" height="170" viewBox="0 0 900 170" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="crawl-title crawl-desc">
  <title id="crawl-title">Crawler ingestion flow</title>
  <desc id="crawl-desc">Seed pages are crawled with link-following under caps and robots, computer-vision filtered, cached to avoid re-downloads, and written as pending rows for the review gate.</desc>
  <defs>
    <marker id="crawl-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="#555" />
    </marker>
  </defs>
  <rect x="15" y="55" width="150" height="64" rx="6" fill="#f7f7f5" stroke="#777" />
  <text x="90" y="82" text-anchor="middle" font-family="Arial, sans-serif" font-size="13">Seed pages</text>
  <text x="90" y="101" text-anchor="middle" font-family="Arial, sans-serif" font-size="11">user / preset</text>
  <rect x="192" y="55" width="150" height="64" rx="6" fill="#f7f7f5" stroke="#777" />
  <text x="267" y="82" text-anchor="middle" font-family="Arial, sans-serif" font-size="13">Crawl + follow</text>
  <text x="267" y="101" text-anchor="middle" font-family="Arial, sans-serif" font-size="11">caps &#183; robots</text>
  <rect x="369" y="55" width="150" height="64" rx="6" fill="#f7f7f5" stroke="#777" />
  <text x="444" y="82" text-anchor="middle" font-family="Arial, sans-serif" font-size="13">CV filter</text>
  <text x="444" y="101" text-anchor="middle" font-family="Arial, sans-serif" font-size="11">face / scene</text>
  <rect x="546" y="55" width="150" height="64" rx="6" fill="#f7f7f5" stroke="#777" />
  <text x="621" y="82" text-anchor="middle" font-family="Arial, sans-serif" font-size="13">Cache</text>
  <text x="621" y="101" text-anchor="middle" font-family="Arial, sans-serif" font-size="11">dedupe &#183; sqlite</text>
  <rect x="723" y="55" width="150" height="64" rx="6" fill="#f7f7f5" stroke="#777" />
  <text x="798" y="82" text-anchor="middle" font-family="Arial, sans-serif" font-size="13">Pending rows</text>
  <text x="798" y="101" text-anchor="middle" font-family="Arial, sans-serif" font-size="11">to review gate</text>
  <line x1="166" y1="87" x2="190" y2="87" stroke="#555" stroke-width="2" marker-end="url(#crawl-arrow)" />
  <line x1="343" y1="87" x2="367" y2="87" stroke="#555" stroke-width="2" marker-end="url(#crawl-arrow)" />
  <line x1="520" y1="87" x2="544" y2="87" stroke="#555" stroke-width="2" marker-end="url(#crawl-arrow)" />
  <line x1="697" y1="87" x2="721" y2="87" stroke="#555" stroke-width="2" marker-end="url(#crawl-arrow)" />
</svg>

## Setup and run instructions

Use the macOS launcher for the GUI:

```bash
./Start\ desaparecidos.command
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

## Configuration and environment variables

- No secrets are required.
- The backend must bind to `127.0.0.1` by default.
- Raw downloads belong under ignored `data/raw/`.
- Crawler downloads and cache belong under ignored `data/raw/crawl/` (`store/` content-addressed files plus `cache.sqlite`).
- Generated outputs belong under ignored `outputs/stage1/`.
- `opencv-python-headless` is a runtime dependency for crawler computer-vision gating; it ships the Haar cascade, so no model download is needed.
- Browser-playable video generation requires `ffmpeg` with H.264/libx264 support.

## Important files and directories

- `README.md`: project overview and setup.
- `AGENTS.md`: repository instructions for AI coding agents.
- `CLAUDE.md`: compatibility pointer for Claude Code.
- `src/desaparecidos/`: Python pipeline and API.
- `src/desaparecidos/cv.py`: OpenCV face/scene gating for crawled images.
- `src/desaparecidos/cache.py`: SQLite + content-addressed crawl cache.
- `frontend/`: local GUI.
- `data/manifests/`: tracked manifest templates.
- `data/manifests/demo-*.csv`: ignored synthetic demo manifests generated on demand.
- `data/manifests/crawled-*.csv`: ignored crawler-produced review manifests.
- `data/manifests/local-*.csv`: ignored locally generated manifests (e.g. portraits imported from `doc/fotos-desaparecidos`).
- `scripts/build_targets_manifest.py`: builds a pending targets manifest from a local directory of portrait images.
- `data/demo/`: ignored synthetic demo images generated on demand.
- `doc/`: long-form project source documents.
- GitHub: private repository at `https://github.com/krahd/desaparecidos.uy`.

## Recent changes

- Initial project documentation, Stage 1 pipeline, local GUI, manifest templates, tests, and launcher were created.
- Private GitHub repository `krahd/desaparecidos.uy` was created and `main` was pushed.
- GUI demo fixtures were added so users can recover from empty template manifests without running CLI commands.
- Local API CORS was widened to localhost/127.0.0.1 on any port so alternate Vite ports remain usable.
- 2026-06-17 11:18 GMT-3 follow-up: demo fixtures now use local-only `local://demo/...` provenance identifiers, generate a portrait-like synthetic target plus four synthetic place surfaces, and resolve manifest-relative preview paths in the GUI.
- Stage 1 reuse accounting now applies `reuse_limit` per extracted fragment rather than per source image. Sidecars report fragment count and maximum observed fragment reuse.
- 2026-06-17 15:40 GMT-3 follow-up: diagnosed GUI `501 Unsupported method ('POST')` responses as requests hitting `python -m http.server` on port `8765` instead of FastAPI. The launcher now selects free backend/frontend ports and passes the selected API URL into Vite.
- 2026-06-17 16:11 GMT-3 follow-up: made the workflow rail clickable, added GUI review/approve/reject controls, added a large still/video output viewer, selected new outputs after generation, and added a constrained crawler that saves candidates as pending rows.
- 2026-06-17 16:43 GMT-3 follow-up: added generated-output selection and delete controls, added a backend output deletion endpoint, switched video rendering to H.264 MP4 via `ffmpeg`, set explicit `video/mp4` responses, removed the unused OpenCV dependency, and added crawler starting-page presets for CdF, MUME, Sitios de Memoria, and Wikimedia Commons Montevideo categories.
- 2026-06-17 17:05 GMT-3 follow-up: replaced the simple random reveal video with a source-first process video. The renderer records tile placements during assembly, shows each used source image full-screen, highlights sampled source fragments, animates fragments into their actual portrait positions, and records source sequence/process metadata in sidecars.
- 2026-06-17 17:34 GMT-3 follow-up: added a bulk review control. New `set_review_status_bulk` rewrites the manifest once for a set of rows or all rows; `set_review_status` now delegates to it. New `POST /api/review-bulk` endpoint and `updateReviewStatusBulk` client power an "Approve all" button in the Review images panel. Added `scripts/build_targets_manifest.py`, which scans a portrait directory (default `doc/fotos-desaparecidos`) and writes a pending targets manifest to an ignored `data/manifests/local-*.csv` path; ran it to produce `data/manifests/local-targets.csv` with 152 pending rows. Added the `data/manifests/local-*.csv` ignore pattern.
- 2026-06-17 18:28 GMT-3 follow-up: clarified that `doc/fotos-desaparecidos/` is intentionally tracked curated source material (AGENTS.md 5.2/5.3 updated). Untracked the redundant `doc/fotos-desaparecidos.zip` archive (`git rm --cached`, local file kept) and added a `.gitignore` rule for it; the removal is staged, not committed.
- 2026-06-17 18:39 GMT-3 follow-up: switched the GUI to a dark theme (black background, white foreground) in `frontend/src/styles.css` via the `:root` palette plus new `--surface`/`--on-accent` variables and `color-scheme: dark`; `npm --prefix frontend run build` passed.
- 2026-06-17 18:52 GMT-3 follow-up: made all surface backgrounds pure black (`--panel`, `--panel-strong`, `--surface`, preview placeholder, media viewer) so panels no longer read as grey; layout separation relies on `--line` borders. Changed the GUI default Targets manifest path to `data/manifests/local-targets.csv` so the imported portraits load without retyping the path (still requires clicking Validate, and the file must have been generated by `scripts/build_targets_manifest.py`). `npm --prefix frontend run build` passed.
- 2026-06-17 20:31 GMT-3 follow-up: large feature/audit pass. (1) Review thumbnails now keep the source aspect ratio (fixed a collapsing `aspect-ratio`/`height:100%` cycle) and clicking a target thumbnail sets the working portrait (place thumbnails open the viewer). (2) Removed the redundant GUI Download section (the `/api/download` endpoint and CLI remain). (3) Added a vectorised nearest-fragment matcher and a `max_contribution_per_source` cap (GUI "Max tiles per source" slider, `0` = unlimited) plumbed through `Stage1Settings`, `/api/generate`, and `generateStage1`; matcher output is unchanged at the default. (4) Rewrote the crawler as a bounded recursive BFS (depth/page/image caps, cross-domain optional, per-host delay, `robots.txt`) with new `cv.py` (OpenCV Haar faces for targets, texture/aspect/resolution heuristics for places) and `cache.py` (SQLite index + content-addressed store) so images are classified/downloaded once; new crawler params on `/api/crawl` and GUI controls (depth, max pages, total images, cross-domain, CV filter); the crawl summary reports pages/seen/added/CV-rejected/from-cache. (5) Added `opencv-python-headless` to dependencies. (6) Relaxed AGENTS.md/CLAUDE.md crawler-persistence wording.

## Tests and verification status

Verification run on 2026-06-17:

- `python3 -m compileall src tests scripts`: passed before dependency installation.
- `.venv/bin/python -m compileall src tests scripts`: passed.
- `.venv/bin/python -m pytest -q`: passed, 21 tests; one upstream `fastapi.testclient` deprecation warning from Starlette.
- `npm --prefix frontend run build`: passed.
- Synthetic fixture generation with `scripts/create_synthetic_fixtures.py`: passed.
- CLI Stage 1 smoke run against synthetic fixtures: passed and wrote ignored output files under `outputs/stage1/`.
- Local backend health check at `http://127.0.0.1:8765/api/health`: passed.
- Vite GUI load at `http://127.0.0.1:5173`: passed.
- API validation and generation calls matching the GUI workflow: passed against synthetic manifests.
- Desktop and mobile-width Safari screenshots were inspected for visible layout overlap and text fit.
- 2026-06-17 follow-up: `.venv/bin/python -m compileall src tests scripts`, `.venv/bin/python -m pytest -q`, and `npm --prefix frontend run build` passed after adding the demo-fixture GUI path.
- 2026-06-17 follow-up: patched API `/api/demo-fixtures`, `/api/validate`, and `/api/generate` were smoke-tested on isolated verification ports.
- 2026-06-17 11:18 GMT-3 follow-up: `.venv/bin/python -m compileall src tests scripts`, `.venv/bin/python -m pytest -q`, `npm --prefix frontend run build`, CLI demo validation, 720px still generation, and a small MP4 generation smoke run passed after the fragment reuse and demo fixture patch.
- 2026-06-17 15:40 GMT-3 follow-up: `.venv/bin/python -m compileall src tests scripts`, `.venv/bin/python -m pytest -q`, `npm --prefix frontend run build`, and `zsh -n "Start desaparecidos.command"` passed. A launcher smoke run with `python -m http.server` still occupying port `8765` selected backend `8766` and frontend `5177`; POST checks to `/api/demo-fixtures` and `/api/validate` returned `200 OK`.
- 2026-06-17 16:15 GMT-3 follow-up: `.venv/bin/python -m compileall src tests scripts`, `.venv/bin/python -m pytest -q`, `npm --prefix frontend run build`, and `git diff --check` passed after adding crawler/review/output-viewer UI and backend routes. A launcher smoke run selected backend `8766` and frontend `5178`; API smoke calls for `/api/demo-fixtures`, `/api/crawl` against a local page, `/api/generate` still, `/api/generate` video, and `/api/outputs` returned successful responses. Browser interaction automation is still unavailable in this environment.
- 2026-06-17 16:43 GMT-3 follow-up: `.venv/bin/python -m compileall src tests scripts`, `.venv/bin/python -m pytest -q`, `npm --prefix frontend run build`, `zsh -n "Start desaparecidos.command"`, and `git diff --check` passed after adding output deletion controls, crawler presets, and H.264 video rendering. A fresh demo video smoke render to `/private/tmp/desaparecidos-video-smoke-20260617` produced an MP4 whose video stream probed as `codec_name=h264` and `pix_fmt=yuv420p`, with `video_codec: h264` in the sidecar.
- 2026-06-17 17:05 GMT-3 follow-up: `.venv/bin/python -m compileall src tests scripts`, `.venv/bin/python -m pytest -q`, `npm --prefix frontend run build`, and `git diff --check` passed with 23 tests after adding assembly-trace process video rendering. A fresh demo process-video smoke render to `/private/tmp/desaparecidos-process-video-smoke-20260617` produced a 16 second H.264/yuv420p MP4 with 192 frames; extracted frames were visually checked for full-source introduction, fragment motion, and final reconstruction.
- 2026-06-17 17:34 GMT-3 follow-up: `python -m compileall src tests scripts`, `python -m pytest -q` (27 tests, +4 for bulk review), and `npm --prefix frontend run build` passed after adding bulk review and the targets-manifest builder. `scripts/build_targets_manifest.py` wrote 152 pending rows to `data/manifests/local-targets.csv`; `validate_manifest(require_files=True)` reported `ok` with no errors and confirmed `git check-ignore` keeps the manifest untracked. GUI browser interaction was not automated in this environment.
- 2026-06-17 18:28 GMT-3 follow-up: no code changed (docs/tracking only), so the test/build suite was not re-run. Verified `git ls-files '*.zip'` is now empty, `git ls-files doc/fotos-desaparecidos/` still lists 188 loose files, the local `doc/fotos-desaparecidos.zip` remains on disk, and `git check-ignore` matches the new `.gitignore` rule.
- 2026-06-17 20:31 GMT-3 follow-up: `.venv/bin/python -m compileall src tests scripts`, `.venv/bin/python -m pytest -q` (44 tests, +17 for matcher cap, crawler recursion/robots/CV/cache, `cv.py`, and `cache.py`), and `npm --prefix frontend run build` passed. CV validated on real data: 6/6 sampled `doc/fotos-desaparecidos` portraits accepted as targets and rejected as places; flat/low-resolution images rejected for places; pure noise yields no faces. Matcher checked deterministic and ~3 ms on a small synthetic case. Crawler cache verified to download a rejected image once across two runs (`from_cache` hit on the second). Live browser screenshot verification of the review thumbnails and click-to-select is still pending in this environment.

## Known issues, risks, and limitations

- The `doc/fotos-desaparecidos/` portrait collection (188 tracked files) is intentionally tracked as the curated source material of the work, not transient crawler/download output; it is an explicit exception to the raw-imagery rule (see AGENTS.md 5.3). The redundant `doc/fotos-desaparecidos.zip` archive (~348 MB) was untracked (`git rm --cached`) and added to `.gitignore`; it is no longer in the index or HEAD, while the local file is kept on disk. The lone `195FPMFUDD.psd` (~11 MB) remains tracked and could be revisited later if archive size becomes a concern.
- `data/manifests/local-targets.csv` contains 152 real disappeared-person names. It is kept untracked via the `data/manifests/local-*.csv` ignore rule and all rows are `pending`; provenance, identity, licence, and naming are unverified and require manual review before approval.
- Public release requires provenance, legal, privacy, and historical-source review.
- The Stage 1 crawler is seeded by user-supplied or preset pages and may follow links recursively (cross-domain optional). It is bounded by depth/page/image caps, a per-host delay, and `robots.txt`, does not identify people, and writes pending rows that require explicit approval before generation. Operators should keep caps modest and respect target sites' terms; cross-domain following can wander, so prefer same-domain for unfamiliar seeds.
- Crawler computer-vision gating uses an OpenCV Haar frontal-face cascade plus lightweight place heuristics. Haar is fast and offline but not perfect: it can miss profile/occluded faces and occasionally false-positive, and the place heuristics are threshold-based. CV gates which images become pending rows; it never approves them, so manual review remains the authority. A stronger DNN detector is a possible later upgrade.
- Crawled images and `cache.sqlite` are persisted on disk under ignored `data/raw/crawl/`. This is intentional (so the crawler does not re-download) but means the local cache can grow; it is not committed and the policy may be revisited.
- MP4 generation depends on `ffmpeg` with H.264/libx264 support. Newly generated videos should be browser-playable; older videos created with the previous `mp4v` path should be regenerated.
- `npm install` reported two high-severity audit findings in the frontend dependency tree. No forced audit fix was applied because it may introduce breaking dependency changes.
- Local server binding required sandbox escalation during verification.
- The GitHub remote is `origin` at `https://github.com/krahd/desaparecidos.uy.git`.

## Recurring tasks

- Keep `STATUS.md` updated after meaningful implementation or verification changes.
- Keep raw imagery and generated outputs untracked; the crawler cache under `data/raw/crawl/` is intentionally persisted on disk but stays ignored.
- Review provenance and `review_status` before generation.

## Pending tasks

- No repository setup tasks are pending.

## Next steps

1. Restart the local launcher so the backend loads the new `/api/crawl`, `/api/review-bulk`, and contribution-cap parameters and the rebuilt frontend. The Targets path already defaults to `data/manifests/local-targets.csv`.
2. Do a live browser pass to confirm the review thumbnails, click-to-set-target, and the "Max tiles per source" slider behave as expected, then run a real bounded crawl and confirm the second run reports cache hits.
3. Review real target/place manifests and crawler-produced pending rows before approving any non-synthetic imagery. Use "Approve all" only after per-row review, since it approves every row in the active manifest.
4. Decide whether to address the frontend npm audit findings before broader use.

## Longer-term steps

1. Expand visual method documentation.
2. Add public website pages after Stage 1 output review.
3. Prepare legal and privacy review materials before any public release.

## Decisions and rationale

- Stage 1 uses place/surface imagery first because it is visually strong and has lower privacy risk than face-fragment processing.
- The GUI is localhost-only so the artist/developer can operate the pipeline without exposing data or outputs.
- Manifests remain the boundary for generation; crawler output is only a pending manifest-building aid.
- The crawler was allowed to follow links recursively (cross-domain) at the user's request, reversing the earlier non-recursive invariant, but kept bounded by caps, a per-host delay, and `robots.txt` so it stays a constrained tool rather than an open-ended scraper.
- Computer-vision gating filters candidates (faces for targets, textured non-face scenes for places) to reduce manual review load, but never auto-approves; the manual review gate stays authoritative.
- Crawled images are cached on disk (content-addressed + SQLite) so repeated crawls do not re-download; persistence is intentional for now and revisitable.
- The per-source contribution cap exists so a reconstruction can be spread across many source images (each contributing few tiles), supporting the "everywhere" concept; it defaults to unlimited to preserve prior output.
- The matcher was vectorised for speed while keeping identical output at the default settings.

## Documentation alignment notes

- The root README summarises the long project description in `doc/desaparecidos-uy-project-description.md`.
- `AGENTS.md` requires `STATUS.md` to stay current.

---

Last updated: 2026-06-17 20:31 GMT-3
