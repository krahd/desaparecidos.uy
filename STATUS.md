# desaparecidos.uy Project Status

Last updated: 2026-09-01 20:59 GMT-6

## Project purpose

`desaparecidos.uy` is a computational memorial artwork triptych about detained-disappeared persons connected to Uruguay:

- **Todos somos familiares** — documented portraits emerge from dispersed fragments of the contemporary social body;
- **Están en todas partes** — documented portraits emerge from Uruguay's places, surfaces, infrastructures, things and territories;
- **Seguimos buscando** — traversal and continuing search determine which visual material can participate and when.

Generated videos are primary manifestations of the memorial, not demonstrations of an image tool. The work is not a forensic reconstruction, restoration system, biometric identifier, deepfake, resurrection medium, replacement archive or source of organisational authority.

The governing hierarchy remains: memorial and political commitments; artistic operations; computational requirements; technical knowledge; then papers and submissions. No generative, recognition or aesthetic subsystem is justified merely to strengthen a manuscript.

## Current implementation state

The repository contains two maintained runtime surfaces:

- the localhost GUI, FastAPI backend and `desaparecidos` compatibility CLI for corpus administration, review, crawling, traversal acquisition and generation;
- the canonical `desaparecidos-artwork` runtime for artwork-oriented fragment placement, evaluation, exhibition rendering and publication evidence.

The canonical runtime supports grid, irregular and overlap grammars; deterministic scale, rotation, opacity and z-order; target salience; source contribution and adjacency controls; territorial balancing; and incremental traversal assembly. Grayscale is the default output and colour is an explicit recorded option.

New outputs use `desaparecidos.uy/output-sidecar/3.0`. Canonical and compatibility outputs now contain:

- complete `desaparecidos.uy/placement-history/1.0` placement histories;
- exact input-manifest hashes, runtime Git commit and working-tree state;
- target source, licence, image-hash, metadata-source and review provenance;
- a reference to the exact `desaparecidos.uy/refusal-paradata/1.0` policy revision;
- a computed `desaparecidos.uy/temporal-causality-evaluator/1.0` result and evaluated-history hash.

`future_source_frames_used` is derived from the evaluator for **Seguimos buscando**. A violation or malformed placement history fails rendering before media finalisation. Exhibition manifests hash every segment video, sidecar and evaluation; publication binds them to the declared artwork and target, recomputes their evaluation, and validates provenance before copying any file.

The core conversational-memory state model added on 8 August remains intentionally separate from the image runtime. It models participant consent, utterance provenance, uncertainty, correction and withdrawal without adding an LLM provider, speech service or persistence backend. Real testimony must not be committed as a test fixture.

## Active focus

The active technical focus is evidence integrity for an AI & Society paper improvement without allowing the paper to redefine the artwork. Implemented work is limited to documentary accountability already required by the memorial:

1. artwork-specific paradata of refusal;
2. complete target provenance snapshots;
3. computed temporal validity and release blocking;
4. reconciled schema, roadmap and release documentation.

The remaining article-evidence work is production and review, not a new image-system feature. It requires one carefully selected and explicitly rights-reviewed target for **Están en todas partes**, one approved **Seguimos buscando** traversal, a clean committed runtime revision, human review and figures derived from those exact hash-bound outputs.

## Architecture overview

The localhost administration surface and canonical render path share reviewed inputs. Output accountability remains beside the generated media and feeds evaluation and release rather than becoming a generic compliance system.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 980 390" role="img" aria-labelledby="architecture-title architecture-desc">
  <title id="architecture-title">desaparecidos.uy architecture</title>
  <desc id="architecture-desc">Reviewed target, source and traversal inputs enter the local and canonical runtimes. Generated media and versioned sidecars are evaluated before exhibition and publication.</desc>
  <defs>
    <marker id="architecture-arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="#333"/>
    </marker>
  </defs>
  <g fill="#f7f5ef" stroke="#333" stroke-width="2">
    <rect x="20" y="55" width="220" height="100" rx="8"/>
    <rect x="300" y="55" width="260" height="100" rx="8"/>
    <rect x="620" y="40" width="330" height="130" rx="8"/>
    <rect x="20" y="260" width="220" height="85" rx="8"/>
    <rect x="300" y="235" width="260" height="135" rx="8"/>
    <rect x="620" y="250" width="330" height="105" rx="8"/>
  </g>
  <g fill="none" stroke="#333" stroke-width="2" marker-end="url(#architecture-arrow)">
    <line x1="240" y1="105" x2="300" y2="105"/>
    <line x1="560" y1="105" x2="620" y2="105"/>
    <line x1="430" y1="155" x2="430" y2="235"/>
    <line x1="240" y1="302" x2="300" y2="302"/>
    <line x1="560" y1="302" x2="620" y2="302"/>
    <line x1="785" y1="170" x2="785" y2="250"/>
  </g>
  <g font-family="sans-serif" fill="#111" text-anchor="middle">
    <text x="130" y="82" font-size="16" font-weight="bold">Reviewed inputs</text>
    <text x="130" y="108" font-size="13">person store + target manifest</text>
    <text x="130" y="128" font-size="13">place / people manifests</text>
    <text x="130" y="148" font-size="13">approved traversal manifest</text>
    <text x="430" y="82" font-size="16" font-weight="bold">Local runtimes</text>
    <text x="430" y="108" font-size="13">GUI + API + compatibility CLI</text>
    <text x="430" y="130" font-size="13">canonical artwork renderer</text>
    <text x="785" y="72" font-size="16" font-weight="bold">Generated manifestation</text>
    <text x="785" y="99" font-size="13">still / H.264 process video</text>
    <text x="785" y="121" font-size="13">placement histories</text>
    <text x="785" y="143" font-size="13">output-sidecar/3.0</text>
    <text x="130" y="290" font-size="16" font-weight="bold">Constitutive policy</text>
    <text x="130" y="316" font-size="13">refusal-paradata/1.0</text>
    <text x="130" y="336" font-size="13">public / restricted rendering</text>
    <text x="430" y="265" font-size="16" font-weight="bold">Sidecar accountability</text>
    <text x="430" y="291" font-size="13">runtime + manifest hashes</text>
    <text x="430" y="313" font-size="13">target + refusal provenance</text>
    <text x="430" y="335" font-size="13">computed causal validity</text>
    <text x="430" y="357" font-size="13">explicit release state</text>
    <text x="785" y="280" font-size="16" font-weight="bold">Evaluation and release</text>
    <text x="785" y="306" font-size="13">artwork evaluation</text>
    <text x="785" y="328" font-size="13">exhibition-triptych/3.0</text>
    <text x="785" y="348" font-size="13">reviewed publication preflight</text>
  </g>
</svg>

## Output and release flow

Temporal validation precedes output finalisation. Publication has a separate preflight so a corrupted history, stale evaluation or mismatched artifact cannot coexist with a nominal release decision.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1140 300" role="img" aria-labelledby="flow-title flow-desc">
  <title id="flow-title">Render, validation and publication flow</title>
  <desc id="flow-desc">A render builds placement histories, evaluates temporal causality, hashes valid artifacts, undergoes human review and passes publication preflight. Invalid histories stop without a final output.</desc>
  <defs>
    <marker id="flow-arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="#333"/>
    </marker>
  </defs>
  <g fill="#f7f5ef" stroke="#333" stroke-width="2">
    <rect x="20" y="55" width="150" height="75" rx="8"/>
    <rect x="205" y="55" width="160" height="75" rx="8"/>
    <rect x="400" y="55" width="160" height="75" rx="8"/>
    <rect x="595" y="55" width="160" height="75" rx="8"/>
    <rect x="790" y="55" width="160" height="75" rx="8"/>
    <rect x="985" y="55" width="135" height="75" rx="8"/>
    <rect x="205" y="205" width="160" height="65" rx="8" fill="#f4e8e5"/>
  </g>
  <g fill="none" stroke="#333" stroke-width="2" marker-end="url(#flow-arrow)">
    <line x1="170" y1="92" x2="205" y2="92"/>
    <line x1="365" y1="92" x2="400" y2="92"/>
    <line x1="560" y1="92" x2="595" y2="92"/>
    <line x1="755" y1="92" x2="790" y2="92"/>
    <line x1="950" y1="92" x2="985" y2="92"/>
    <line x1="285" y1="130" x2="285" y2="205"/>
  </g>
  <g font-family="sans-serif" fill="#111" text-anchor="middle">
    <text x="95" y="83" font-size="15" font-weight="bold">Assemble</text>
    <text x="95" y="106" font-size="12">placement histories</text>
    <text x="285" y="79" font-size="15" font-weight="bold">Compute</text>
    <text x="285" y="101" font-size="12">causal evaluation</text>
    <text x="285" y="119" font-size="12">+ history hash</text>
    <text x="480" y="79" font-size="15" font-weight="bold">Finalise</text>
    <text x="480" y="101" font-size="12">media + sidecar</text>
    <text x="480" y="119" font-size="12">artifact hashes</text>
    <text x="675" y="79" font-size="15" font-weight="bold">Human review</text>
    <text x="675" y="101" font-size="12">history, rights, context</text>
    <text x="675" y="119" font-size="12">full-duration output</text>
    <text x="870" y="79" font-size="15" font-weight="bold">Preflight</text>
    <text x="870" y="101" font-size="12">recompute + verify</text>
    <text x="870" y="119" font-size="12">release record</text>
    <text x="1052" y="83" font-size="15" font-weight="bold">Publish</text>
    <text x="1052" y="106" font-size="12">reviewed derivative</text>
    <text x="285" y="233" font-size="15" font-weight="bold">Fail render</text>
    <text x="285" y="255" font-size="12">no finalised output</text>
    <text x="382" y="82" font-size="12">valid</text>
    <text x="304" y="172" font-size="12">invalid</text>
  </g>
</svg>

## Setup and run instructions

Local GUI:

```bash
./start.sh
```

Canonical rendering and evaluation:

```bash
desaparecidos-artwork render --help
desaparecidos-artwork search --help
python scripts/evaluate_artwork_output.py --help
```

Policy documentation, exhibition and static publication:

```bash
python scripts/render_refusal_paradata.py --access public
python scripts/render_exhibition_triptych.py --help
python scripts/publish_static_memorial.py --help
```

`start.sh` binds the API and GUI to localhost. FFmpeg with `libx264` is required for browser-playable canonical MP4 output.

## Configuration and environment variables

- `MAPILLARY_ACCESS_TOKEN` is required only for live Mapillary discovery/acquisition. Do not commit it.
- `BACKEND_PORT` and `FRONTEND_PORT` optionally set preferred launcher ports; the launcher moves to free localhost ports when needed.
- `VITE_API_BASE` is set by `start.sh` for the local frontend.
- `config/exhibition-triptych.example.json` is the exhibition-plan template.
- `config/refusal-paradata.json` is the versioned refusal-policy source of truth.
- `web/publication.example.json` uses `desaparecidos.uy/web-publication/2.0` and requires reviewer/date/non-endorsement fields for each published work.
- Pillow is constrained to `>=12.3,<13` because the earlier permitted 12.2 release has known vulnerabilities; the frontend lockfile similarly pins audited transitive `nanoid` and `postcss` releases.

## Important files and directories

- `src/desaparecidos/artwork_runtime.py` — canonical renderer.
- `src/desaparecidos/refusal_paradata.py` — refusal validation, rendering and sidecar policy provenance.
- `src/desaparecidos/target_provenance.py` — target provenance snapshots and validation.
- `src/desaparecidos/evaluation.py` — artwork metrics and temporal-causality evaluator.
- `scripts/render_exhibition_triptych.py` — hash-bound three-channel render plan.
- `scripts/publish_static_memorial.py` — reviewed publication preflight and copy.
- `scripts/record_target_review.py` — explicit human historical-identification or portrait-rights decision recording.
- `data/persons/disappeared.json` — canonical person corpus.
- `assets/targets/disappeared/selected/` — reviewed selected target derivatives.
- `data/manifests/` — tracked templates/exports and ignored local review manifests.
- `data/raw/` and `outputs/` — ignored local source, traversal, cache and generated artifacts.
- `doc/artistic-computational-principles.md` — governing artistic hierarchy.
- `doc/development-roadmap.md` — checked implementation state and remaining artistic work.
- `doc/artwork-runtime.md` and `doc/output-sidecar-schema.md` — runtime and evidence contracts.
- `doc/refusal-paradata.md` — generated public refusal record.

## Current capabilities

- Canonical target store administration and target-manifest export.
- Review-gated target, place and internal people-source ingestion.
- Bounded crawler, exact/perceptual dedupe and local CV gates without identity inference.
- Deterministic fragment matching and grid/free/irregular/overlap placement.
- Place-source territorial balancing with explicit `unlocated` material.
- Provider-neutral traversal records with current Mapillary acquisition.
- Manual or reversible CV-based traversal-frame approval under the recorded artist decision.
- Incremental traversal rendering with enforced temporal causality.
- Artwork-derived evaluation without claims of identity, anonymity or memorial adequacy.
- Versioned refusal, target, runtime, manifest and release provenance.
- Hash-bound exhibition and static-publication tooling.
- Consent/provenance/correction/withdrawal state model for future conversational-memory work.

## Target corpus

- canonical person records: 204;
- selected portrait derivatives: 202;
- unresolved public-portrait gaps: `camuyrano-bottini-mario` and `gadea-hernandez-liborio`.

These are project-curation counts, not an authoritative historical total. The target corpus was not modified by the 1 September audit work.

## Recent changes

### 1 September 2026 — integrity and dependency audit

- Made placement-history validation strict about schema, target binding, declared counts, unique placement IDs, source sequences and the complete recorded evaluator result.
- Required artwork-specific input-manifest roles and explicit target IDs for sequence provenance.
- Prevented unresolved licence/permission notes, placeholder release records and malformed review dates from crossing publication gates; returning a review to `pending` now clears reviewer/date fields.
- Bound publication segments to their artwork, target, segment-video hash and complete recomputed evaluation; stale media for newly unpublished works is removed from reused destinations.
- Made the tracked publication example release nothing by default.
- Removed avoidable Pydantic deprecation access in the generation API.
- Raised Pillow to `>=12.3,<13` and updated transitive `nanoid` and `postcss` lockfile versions after vulnerability audits.

### 1 September 2026 — evidence integrity

- Added `memorial-refusals-2026-01` under `desaparecidos.uy/refusal-paradata/1.0`, a validator and public/restricted curatorial renderer.
- Added target source/licence/access/image-hash and metadata/review/release snapshots without conflating manifest approval, rights, historical identification or endorsement.
- Added `desaparecidos.uy/output-sidecar/3.0`, exact input-manifest hashes and runtime commit provenance to all output paths.
- Made temporal causality computed, hash-bound and render-blocking; corrupted histories now block publication.
- Added exhibition/publication schema 3.0/2.0 artifact verification, a clean-runtime gate and explicit release reviewer records.
- Reconciled the roadmap and canonical runtime/release documentation.
- Updated the mandatory `krahd/tom-work-admin` project record with the evidence milestone and next production action.

### 8–22 August 2026

- Added the auditable conversational-memory core model and synthetic tests for consent, provenance, correction and withdrawal.
- Added mandatory cross-repository administration guidance in `WORK-ADMIN.md`.
- Preserved the Premio Nacional de Artes Visuales application text materials on `main`.

## Tests and verification status

Focused local verification on 1 September 2026:

- focused policy, evaluation, runtime, traversal, pipeline, person, publication and API tests — 91 passed with one dependency warning.
- Python 3.11, 3.12 and 3.14 compilation of `src`, `tests` and `scripts` — passed.
- `.venv/bin/python -m pytest -q` — 190 passed with one Starlette/httpx compatibility warning.
- `npm --prefix frontend test` — eight tests passed.
- `npm --prefix frontend run build` — passed with the existing large-chunk advisory.
- `npm --prefix frontend audit --audit-level=moderate` — zero known vulnerabilities after lockfile remediation.
- isolated `pip-audit` of the installed project environment — no known third-party vulnerabilities after upgrading Pillow; the local unpublished `desaparecidos-uy` package is not a PyPI audit target.
- `.venv/bin/python -m pip check`, `bash -n start.sh`, `git diff --check`, refusal-policy public rendering and JSON parsing — passed.

No final exhibition media, article figures or supplementary video have been rendered or visually reviewed in this change.

Last recorded CI evidence remains GitHub Actions run `30145676564` from 25 July 2026: Python 3.11/3.12, frontend tests/build and launcher syntax passed. That run predates the current changes.

## Known issues, risks and limitations

- No target currently records the newly explicit historical-identification and rights-review states required for canonical article evidence. Existing `review_status=approved` values are generation gates, not rights clearance.
- The current approved canonical target row uses a permission note that still requires verification; it is not sufficient to claim an explicitly licensed paper artifact.
- A local approved traversal exists, but pairing it with a target and creating a paper artifact remains an artistic selection and human-review task.
- Rendering from the current uncommitted worktree records the prior Git commit with `working_tree_dirty=true`; the publication preflight rejects such outputs, so canonical evidence must be rendered from a clean committed revision.
- `Todos somos familiares` remains internal pending source policy, legal/contextual review and complete output review.
- Structural source-fragment metrics do not establish anonymity or source-person non-recognisability.
- Mapillary coverage and terms, route selection and CV acceptance shape traversal material; public use still requires review.
- Public removal/contact procedures and institutional/legal review are not yet complete.
- FastAPI's current test-client shim emits one Starlette/httpx compatibility deprecation warning; it does not affect the passing runtime tests but requires a future dependency-compatible migration.
- The frontend production build retains a non-blocking large-chunk advisory.
- Variable fragment masks, live input, real-time rendering, sound and multi-channel synchronisation remain future artistic development, not paper-driven backlog.

## Pending tasks and next steps

1. Review and explicitly record historical-identification and portrait-rights decisions for a carefully selected target; record reviewer and date.
2. Commit and verify the evidence-integrity implementation so sidecars can cite a clean runtime revision.
3. Render one canonical **Están en todas partes** output and one approved **Seguimos buscando** traversal from that revision.
4. Generate evaluations and an exhibition manifest; complete full-duration, historical, rights, contextual and recognisability review.
5. Derive AI & Society figures and the supplementary MP4 only from those exact artifacts; retain derivative hashes in the manuscript repository.
6. Update the canonical manuscript repository with the resulting evidence state; the required `krahd/tom-work-admin` project record is already current.

## Longer-term steps

- Complete exhibition-quality loops and installation playback testing.
- Establish removal/contact procedures and complete appropriate legal and institutional review.
- Continue corpus consultation and source stewardship without presenting the project as an official archive.
- Develop unchecked roadmap items only when supported by the artwork: partial searches, broader traversal sources, sound, installation synchronisation and future live forms.

## Decisions and rationale

- Refusal paradata is artwork-specific. It records constitutive non-actions but does not create a general compliance ontology.
- Target approval, historical identification, portrait rights, public release and organisational endorsement remain distinct because one cannot evidence another.
- Rights clearance is permission for a stated use, never an implication that an archive, memorial organisation, relatives' organisation, rights holder or depicted person endorses the artwork.
- Temporal causality is an executable integrity property of **Seguimos buscando**, not a descriptive Boolean.
- Canonical figures and supplementary media must remain traceable to exact media, sidecars, evaluations, runtime commit, policy hash and input hashes.
- Sensitive source imagery, traversal caches and generated evidence stay outside version control.

## Documentation alignment notes

- `README.md`, `doc/artwork-runtime.md`, `doc/output-sidecar-schema.md`, `doc/refusal-paradata.md`, `doc/development-roadmap.md`, `web/publication.example.json` and this status report reflect the 3.0 sidecar and current release contracts.
- `doc/STATUS.md` remains a pointer to this canonical report.
- The URUCON paper package remains in the external academic-writing repository and retains its previously recorded evidence revision. The current work supports a separate AI & Society improvement and does not silently rewrite that artifact.
- The required `krahd/tom-work-admin/projects/desaparecidos-uy.md` cross-repository record was updated in the same work session; registry lifecycle state and deadline did not change.

Last updated: 2026-09-01 20:59 GMT-6
