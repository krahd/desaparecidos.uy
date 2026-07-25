# desaparecidos.uy Project Status

Last updated: 2026-07-25 01:13 GMT-3

## Governing principle

`desaparecidos.uy` is first a computational memorial and artwork. Its technical architecture, constraints, evaluations, and papers must emerge from the memorial's artistic and political operations. The project must not acquire arbitrary requirements solely to satisfy a paper.

Durable design sources:

- `doc/artistic-computational-principles.md` — governing artistic, computational, research, and publication principles;
- `doc/development-roadmap.md` — completion goal and implementation sequence;
- `doc/desaparecidos-uy-project-description.md` — full project description and historical, political, artistic, ethical, and visual framework.

The current long-term goal is to complete the roadmap directly on `main`: develop the triptych into an exhibition-quality, durable online computational memorial supporting generated video, installation, interaction, real-time processes, and future artistic iterations, then derive the URUCON paper from the verified work.

## Project purpose

`desaparecidos.uy` is a local-first computational memorial artwork triptych about detained-disappeared persons connected to Uruguay:

- **Todos somos familiares** — the disappeared emerge from fragments of the living social body;
- **Están en todas partes** — the disappeared emerge from the material, visual, institutional, and territorial country;
- **Seguimos buscando** — traversal and continuing search become the temporal structure of the work.

The generated videos are primary manifestations of the memorial, not demonstrations of a software tool. The system is not an archive, forensic tool, biometric system, deepfake, resurrection medium, or identity-matching workflow.

## Current implementation state

The repository contains a localhost-only GUI, FastAPI backend, reusable Python pipeline, CLI entry points, canonical disappeared-person corpus, target administration, bounded crawler, source review gates, traversal workflow, still/MP4 generation, and JSON sidecars.

### Tracked target corpus

- canonical disappeared-person records: `data/persons/disappeared.json`;
- reviewed selected 3:4 target portraits: `assets/targets/disappeared/selected/`;
- first full imported corpus pass: 204 person records, 202 selected portrait derivatives, 321 total portrait candidates, and 118 review-only local alternate candidates;
- unresolved public-portrait gaps: `camuyrano-bottini-mario` and `gadea-hernandez-liborio`;
- reviewed source-backed metadata overrides: `data/persons/metadata-overrides.csv`;
- 197 source-scoped Sitios de Memoria biographies, seven explicit empty biography records, and no retained page-navigation boilerplate.

These counts describe project curation, not an authoritative historical total.

### Runtime and artwork modes

- five functional hash-routed GUI pages: Targets, Images, Todos somos familiares, Están en todas partes, and Seguimos buscando;
- artwork-aware still/video generation for people-derived and place-derived sources;
- deterministic, vectorised fragment matching using a six-dimensional colour/contrast/edge descriptor and L2 nearest-neighbour search;
- an active default contribution cap of one output tile per source row;
- people generation rejects unlimited source contribution;
- selectable `grid` and `match` process-video layouts;
- source-reveal process videos show approved place images or only reviewed people face regions before fragment transfer;
- rejected and non-contributing candidates are not shown as raw images in the active video path;
- sidecars record artwork/source identifiers, settings, source usage, source sequence, search trails, candidate counts, display policy, and video-process metadata;
- provider-neutral traversal storage with Mapillary discovery, manual/GeoJSON/GPX/autonomous authoring, bounded acquisition, manual or explicit CV-gated frame approval, and deterministic rendering;
- autonomous all-Uruguay traversal with population-weighted locality sampling, configurable rural share, coverage fallback, acquisition, CV-gated approval, and rendering;
- incremental found-fragment assembly for Seguimos buscando: no tile is matched against a frame the traversal has not reached.

## Current architectural limitation

The running system remains based on square fragments and target-tile placements. It supports one regular staging layout and one deterministic non-grid staging scatter, but does not yet provide the general placement architecture required for variable fragment size, masks, overlap, opacity, z-order, rotation, or persistent temporal movement histories.

Complete placement records currently exist in memory during Stage 1 assembly but are not persisted in output sidecars. Persistent placement and temporal histories are now an artwork-driven priority because they support video replay, overlap, interaction, live reorganisation, future regeneration, and visible computational process.

## Active development goal

Complete `doc/development-roadmap.md` in the following order:

1. reconcile current documentation with actual behaviour;
2. add versioned persistent placement histories;
3. generalise fragment placement while preserving the working grid renderer;
4. add irregular and overlapping visual grammars;
5. add target salience and source-recognisability controls for Todos somos familiares;
6. strengthen territorial source and composition strategies for Están en todas partes;
7. extend temporal histories and partial-search rendering for Seguimos buscando;
8. expand tests, CI, dependency reproducibility, API path safety, and network-fetch safety;
9. produce exhibition-quality loops and a durable online presentation;
10. rewrite and evaluate the URUCON paper from the resulting verified work.

## Current submission work

### Premio Nacional de Artes Visuales 2026

Work is under `doc/submissions/2026-premio-nacional-artes-visuales/` on `main`.

Target form:

- one composite work/triptych;
- three offline-generated videos in loop;
- three vertical screens;
- non-interactive installation.

Current package includes:

- `Desaparecidos_PNAV_2026.docx`;
- `Desaparecidos_PNAV_2026_con_imagenes.docx`;
- `Desaparecidos_PNAV_2026.pdf`;
- `visual-documentation/` with stills, contact/process sheets, installation mock-up, preview manifests, sidecars, and metadata;
- `code-audit.md`;
- `Desaparecidos-declaracion-jurada-titular.docx`.

Remaining PNAV tasks:

1. finalise Spanish application texts;
2. complete administrative placeholders;
3. export one final loop per artwork mode;
4. replace preview stills if stronger reviewed material becomes available;
5. confirm rights and image-risk conditions for final inputs;
6. ensure Todos somos familiares does not expose recognisable living source faces without appropriate authorisation and review;
7. create stable external video links if required.

## Academic writing boundary

Academic manuscript drafting belongs in `krahd/academic-writing`, not in this repository.

Canonical moved folders:

- `my_papers_2026/2026 - AI Society - Against Restoration/`;
- `my_papers_2026/2026 - AI Society - Incomplete Reconstruction/`;
- `my_papers_2026/2026 - Urucon - Desaparecidos.uy/`.

The URUCON package now records an artwork-derived paper direction centred on computational re-enactment rather than treating provenance and quotas as the primary purpose of the artwork.

## Technical and ethical invariants

- Keep GUI/API localhost-only unless deployment is deliberately redesigned.
- Do not commit raw source imagery, rejected candidates, generated outputs, fragments, downloads, database dumps, credentials, or generated sensitive data.
- Require `review_status=approved` before ordinary source participation.
- Historical target images are referential portraits, not material for enhancement, resurrection, deepfake, or forensic claims.
- Contemporary people images belong in `people` manifests and must not be treated as disappeared-person targets.
- Do not add identity seeking, face/name matching, demographic inference, or biometric identification for contemporary people.
- Public availability is not sufficient consent for arbitrary processing.
- Exclude minors, private contexts, and sensitive contexts unless explicit permission and a defensible artistic reason exist.
- Final public people-derived outputs require end-to-end review; no unsupported anonymity claim is permitted.
- Provenance, source controls, and exclusion mechanisms should be developed where they sustain the memorial, its public accountability, or future iterations, not as a paper-driven general compliance ontology.
- Maintain the strict temporal-causality rule for Seguimos buscando.

## Documentation requiring reconciliation

`doc/desaparecidos-uy-project-description.md` still contains stale language describing a legacy 240-tile source contribution cap. The current implementation source of truth is:

- `DEFAULT_MAX_CONTRIBUTION_PER_SOURCE = 1` in `src/desaparecidos/pipeline.py`;
- place generation permits explicit `0` as unlimited;
- people generation rejects `0` and requires a positive cap;
- `max_fragments_per_source = 240` is an extraction ceiling, not an output contribution cap;
- rejected and non-contributing candidates are not shown as raw images in the active video path.

This documentation reconciliation is the first roadmap task.

## Setup and verification

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

Recommended complete verification:

```bash
.venv/bin/python -m compileall src tests scripts
.venv/bin/python -m pytest -q
npm --prefix frontend test
npm --prefix frontend run build
zsh -n start.sh
git diff --check
```

## Verification status

- Public GitHub Actions production verification at commit `741db2183d05ce0f26caee1fea59646824e043a6`: 144 Python tests passed with one Starlette/httpx deprecation warning.
- The independent benchmark job in that workflow reproduced its committed aggregate values.
- Current CI does not yet run frontend tests/build, launcher syntax, compileall, or the complete documented verification sequence.
- The documentation changes adding the principles and roadmap have not altered runtime behaviour.
- No local test execution was possible for the present documentation-only pass.

## Important files

- `README.md`: user-facing overview and workflow.
- `AGENTS.md`: repository rules and safety invariants.
- `STATUS.md`: current project state.
- `doc/artistic-computational-principles.md`: governing design hierarchy.
- `doc/development-roadmap.md`: completion goal.
- `doc/desaparecidos-uy-project-description.md`: full project statement.
- `src/desaparecidos/pipeline.py`: Stage 1 assembly, sidecars, still/video rendering.
- `src/desaparecidos/traversals.py`: traversal model, acquisition, review, and rendering.
- `src/desaparecidos/api.py`: FastAPI routes.
- `src/desaparecidos/cli.py`: command-line entry points.
- `frontend/`: React/Vite localhost GUI.
- `data/persons/disappeared.json`: canonical target-person store.
- `assets/targets/disappeared/selected/`: reviewed selected target derivatives.
- `data/sources.json`: source registry.
- `data/raw/`, `data/processed/`, `outputs/stage1/`: ignored runtime/generated data.
- `doc/submissions/2026-premio-nacional-artes-visuales/`: PNAV submission materials.
- `doc/writings/README.md`: academic-writing boundary.

Last updated: 2026-07-25 01:13 GMT-3