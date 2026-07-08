# desaparecidos.uy Project Status

Last updated: 2026-07-08 16:05 GMT-3

## Project purpose

`desaparecidos.uy` is a local-first computational memorial artwork triptych about detained-disappeared persons connected to Uruguay: **Todos somos familiares**, **Están en todas partes**, and **Seguimos buscando**. All three artworks now have separate functional workspaces. The system is not an archive, forensic tool, biometric system, deepfake, resurrection medium, or identity-matching workflow.

## Current implementation state

The repository contains a localhost-only GUI, FastAPI backend, reusable Python pipeline, CLI entry points, canonical disappeared-person corpus, target administration, bounded crawler, source review gates, traversal workflow, still/MP4 generation, and JSON sidecars.

Current tracked/corpus state:

- canonical disappeared-person target records in `data/persons/disappeared.json`;
- reviewed selected 3:4 target portrait derivatives under `assets/targets/disappeared/selected/`;
- first full imported corpus pass: 204 person records, 202 selected portrait derivatives, 321 total portrait candidates, 118 review-only local alternate portrait candidates, and two unresolved public-portrait gaps (`camuyrano-bottini-mario`, `gadea-hernandez-liborio`);
- reviewed source-backed metadata overrides in `data/persons/metadata-overrides.csv`;
- 197 source-scoped Sitios de Memoria biographies in the canonical person store, with seven explicit empty biography records and no retained page-navigation boilerplate.

Current artwork/runtime state:

- five functional hash-routed GUI pages: Targets, Images, Todos somos familiares, Están en todas partes, and Seguimos buscando;
- artwork-aware still/video generation for **Todos somos familiares** from approved people/face-region rows and **Están en todas partes** from approved place rows;
- provider-neutral traversal storage with Mapillary adapter, manual/GeoJSON/GPX/autonomous route authoring, bounded local frame acquisition, manual or explicit CV-gated frame approval, and deterministic **Seguimos buscando** rendering;
- autonomous all-Uruguay flow: population-weighted locality sampling with configurable rural share, coverage fallback, frame acquisition, CV-gated auto-approval, and rendering;
- incremental found-fragment assembly for **Seguimos buscando**: no tile is matched against a frame the traversal has not reached;
- deterministic, vectorised fragment matching using a six-dimensional colour/contrast/edge descriptor and L2 nearest-neighbour search;
- selectable `grid` and `match` process-video layouts;
- source-reveal process videos that briefly show contributing approved place images, or only reviewed face regions for people sources, before fading non-contributing pixels and transferring selected fragments;
- rejected and non-contributing candidates are not shown as raw images in the active video path;
- sidecars record artwork/source identifiers, settings, source usage, source sequence, search trail URLs/run ids, truthful candidate counts, privacy/display policy, and video process metadata.

## Current submission work

Current Premio Nacional work is happening on `main` directly, under:

- `doc/submissions/2026-premio-nacional-artes-visuales/`.

Target format:

- one composite work/triptych;
- three offline-generated videos in loop;
- three vertical screens;
- non-interactive installation.

Files added/updated for this submission pass:

- `doc/submissions/2026-premio-nacional-artes-visuales/Desaparecidos_PNAV_2026.docx`: live DOCX application folder, now including a visual-register section with generated stills, a three-screen montage, and a typo fix in the artwork description;
- `doc/submissions/2026-premio-nacional-artes-visuales/Desaparecidos_PNAV_2026_con_imagenes.docx`: explicit copy of the same DOCX with embedded visual-register images, added after the live filename was overwritten by a 36 KB image-less copy during local editing;
- `doc/submissions/2026-premio-nacional-artes-visuales/Desaparecidos_PNAV_2026.pdf`: Pandoc/XeLaTeX PDF export of the updated DOCX, 6 pages and about 700 KB;
- `doc/submissions/2026-premio-nacional-artes-visuales/visual-documentation/`: PNAV visual documentation stills, contact sheet, process sheet, installation mock-up, generated preview source manifests, render sidecars, and metadata;
- `doc/submissions/2026-premio-nacional-artes-visuales/code-audit.md`: static code/documentation audit for the proposed offline three-screen installation;
- `doc/submissions/2026-premio-nacional-artes-visuales/Desaparecidos-declaracion-jurada-titular.docx`: local declaration file for the administrative upload.
- `doc/submissions/2026-premio-nacional-artes-visuales/Desaparecidos_PNAV_2026_con_imagenes.docx` (2026-07-08 ~16:30 visual pass) and `stills/`: replaced the two text-contaminated example stills with new 1920×2568 vertical renders — Todos somos familiares from a curated ≥120 px face-region subset of `crawled-people.csv` (minor, graphics, and UI false positives excluded; ignored manifest `data/manifests/local-people-doc.csv`) and Están en todas partes from the 13 approved live Mapillary traversal frames (ignored manifest `data/manifests/local-places-traversal-doc.csv`); added the missing Seguimos buscando mid-assembly example (real Artigas/Paysandú walk) and a three-vertical-screen installation visualization; fixed the "reconstrución" typo; rewrote the visual-section intro truthfully; corrected alt texts; stripped the orphaned contaminated media from the package (8.8 → 6.3 MB). Final videos: decided vertical orientation is already satisfied — all render canvases are portrait 3:4.

## Active focus

Prepare the Premio Nacional submission package as an offline audiovisual triptych rather than a live software demo. This requires:

1. finalising Spanish application texts;
2. completing missing administrative placeholders: exact birth day/month, document number, address, date, local responsible person if used;
3. exporting one looped video per artwork mode;
4. replacing preview stills with final exhibition-video stills if better reviewed source inputs are available;
5. confirming source rights and image-rights risk for all final visual inputs;
6. ensuring the **Todos somos familiares** exhibition loop does not expose recognisable living source faces without authorisation;
7. generating stable external video links if needed by the online form.

## Technical and ethical constraints

- Keep GUI/API localhost-only unless explicitly changed.
- Do not commit raw source imagery, rejected candidates, generated outputs, fragments, downloaded files, database dumps, local environment files, credentials, or generated sensitive data.
- Require `review_status=approved` before source images participate in ordinary generation.
- Historical target images are referential portraits, not material for enhancement, resurrection, deepfake, or forensic reconstruction claims.
- `targets` are disappeared-person portraits only. Contemporary public images of people belong in `people` manifests and must not be treated as disappeared-person targets.
- Do not add identity-seeking behaviour, face/name matching, or biometric identification for contemporary people images.
- Public availability is not sufficient consent for arbitrary processing. Exclude minors, private contexts, and sensitive contexts unless explicit permission exists.
- For Premio Nacional exhibition, generated videos should use reviewed or authorised visual inputs and must be checked end-to-end before submission.

## Known documentation issue

Some older writing files still contain stale method language about a 240-tile default cap or raw rejected/non-contributing candidate display. The current implementation source of truth is:

- `DEFAULT_MAX_CONTRIBUTION_PER_SOURCE = 1` in `src/desaparecidos/pipeline.py`;
- place generation permits explicit `0` as unlimited;
- people generation rejects `0` and requires a positive contribution cap;
- rejected/non-contributing candidates are not shown as raw images in the active video path.

The Premio submission texts use the corrected language. Remaining older writing files should be corrected before they are reused for publication or public documentation.

## Setup and verification commands

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

Recommended verification:

```bash
.venv/bin/python -m compileall src tests scripts
.venv/bin/python -m pytest -q
npm --prefix frontend run build
zsh -n start.sh
git diff --check
```

## Verification status

Application texts were previously audited against the official opportunity page and the local bases PDF.

PNAV visual documentation pass on 2026-07-08:

- generated two Stage 1 preview stills with `.venv/bin/python -m desaparecidos run-stage1`, using the approved `abeledo-sotuyo-horacio-adolfo` target and local synthetic non-sensitive PNAV source manifests;
- extracted a **Seguimos buscando** process frame from the existing traversal MP4 with `ffmpeg`;
- generated individual stills, a three-channel contact sheet, a process sheet, and an installation mock-up under `doc/submissions/2026-premio-nacional-artes-visuales/visual-documentation/`;
- patched `Desaparecidos_PNAV_2026.docx` to insert the visual register and fix `Ddesaparecidos.uy`;
- validated the DOCX with `unzip -t`, XML parsing, image-relationship checks, and `textutil -convert html`;
- exported `Desaparecidos_PNAV_2026.pdf` with `pandoc --pdf-engine=xelatex`;
- checked the PDF with `pdfinfo` and rendered pages with `pdftoppm`; the PDF renders to 6 pages and is about 700 KB, below the 20 MB submission limit.

No code tests, full frontend builds, or full video-export smoke tests were run during this visual-documentation pass.

## Important files and directories

- `README.md`: current user-facing overview.
- `AGENTS.md`: repository instructions and safety invariants.
- `STATUS.md`: current project status.
- `src/desaparecidos/pipeline.py`: Stage 1 assembly, sidecars, still/video rendering, URL ticker, outro.
- `src/desaparecidos/traversals.py`: provider-neutral route model, Mapillary adapter, acquisition/review store, and third-artwork renderer.
- `src/desaparecidos/api.py`: FastAPI routes.
- `src/desaparecidos/cli.py`: CLI entry points.
- `frontend/`: React/Vite localhost GUI.
- `data/persons/disappeared.json`: canonical target-person metadata/provenance store.
- `assets/targets/disappeared/selected/`: reviewed selected 3:4 target portrait derivatives.
- `data/sources.json`: source registry.
- `data/raw/`, `data/processed/`, `outputs/stage1/`: ignored runtime/generated data.
- `doc/submissions/2026-premio-nacional-artes-visuales/`: Premio Nacional submission materials.

Last updated: 2026-07-08 16:05 GMT-3
