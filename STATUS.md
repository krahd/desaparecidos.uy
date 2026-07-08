# desaparecidos.uy Project Status

Last updated: 2026-07-08 14:25 GMT-3

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

A dedicated branch exists for the 62.º Premio Nacional de Artes Visuales 2026 submission:

- branch: `submission-premio-nacional-2026`;
- target format: one composite work/triptych, three offline-generated videos in loop, three vertical screens, non-interactive installation;
- submission folder: `doc/submissions/2026-premio-nacional-artes-visuales/`.

Files added/updated for this submission pass:

- `doc/submissions/2026-premio-nacional-artes-visuales/application-texts.md`: first Spanish application text package aligned with the bases fields and character limits;
- `doc/submissions/2026-premio-nacional-artes-visuales/code-audit.md`: static code/documentation audit for the proposed offline three-screen installation.

## Active focus

Prepare the Premio Nacional submission package as an offline audiovisual triptych rather than a live software demo. This requires:

1. finalising Spanish application texts;
2. exporting one looped video per artwork mode;
3. selecting stills and a montage diagram for a PDF under 20 MB;
4. confirming source rights and image-rights risk for all final visual inputs;
5. ensuring the **Todos somos familiares** exhibition loop does not expose recognisable living source faces without authorisation;
6. generating stable external video links if needed by the online form.

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

No tests, builds, smoke tests, linters, type-checkers, or render commands were run during the Premio Nacional documentation pass in this session. The code audit was static only, based on repository inspection through GitHub.

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
