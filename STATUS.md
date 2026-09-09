# desaparecidos.uy Project Status

Last updated: 2026-09-09 02:28 GMT-6

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

All three works now use the same causal search/reconstruction logic in video: source encounters advance on the left, the reconstruction accumulates on the right, and only a structurally matched subregion from the current encounter can travel to its exact target rectangle. Regions are variable squares and rectangles, selected large-first and later overlapped or replaced by better refinements; normal output requires full coverage. **Todos somos familiares** shows only approved, current-hash face crops that pass landmark or independent face-and-eye confirmation, never surrounding contemporary photographs. **Están en todas partes** shows only approved images that pass the current place gate. **Seguimos buscando** advances through approved street-level traversal frames. Fragment streams are deterministic non-repeating shuffles: each eligible source appears at most once, and normal long-form generation fails when there are too few unique sources. Pending, rejected and gate-rejected imagery is excluded. Histories remain temporally causal and record the no-repeat policy explicitly.

All three works use the same monochrome video form: search at left and reconstruction at right fades to black, the assembled fragment image fades in/out, followed by person details, closing text and https://desaparecidos.uy, each fading through black. Catalogue names are displayed given names first without a comma. Defaults are 1920×1080 landscape at 24 fps, with a 600-second search and a 20-second closing sequence. Encounters advance at about three images per second and accepted crops travel for 0.75 seconds. Fragment works use an eight-encounter finding interval, distributing discoveries roughly every 2.6 seconds while retaining many non-contributing search encounters; traversal spacing remains separately configurable. The exact schedule is recorded under `search-video-presentation/3.0`. The artist interface, map, image/video previews and static memorial styles are monochrome; colour output requests are rejected.

Traversal reconstruction modes are `fixed`, `largest-first` and `refine` (default). Default traversal minimum/maximum region extents are 96/384 px; fragment video defaults are 48/384 px. The general structural threshold is 0.82, minimum structure 0.035 and improvement margin 0.04; the current fragment form uses 0.60, 0.001 and 0.005 respectively. Broad structural comparison uses 8×8 samples by default; fine comparison retains 16×16. Uncovered areas take precedence over refinements. At 95% coverage a separate 0.45 completion threshold may accept only remaining uncovered regions; refinements retain the ordinary threshold and margin. Complete fragment searches continue through the full nominal refinement budget rather than stopping when a similarity threshold is first crossed. Optional `tone_mode=match-region` applies one recorded brightness/contrast transform after structural acceptance; `source` preserves exposure and remains the traversal default. The artist screen includes a mixed-region traversal preset (96–384 px, threshold 0.60, minimum structure 0.001, refinement margin 0.02, exposure adjustment, six-encounter finding and playback spacing, and required complete coverage). These are heuristic artistic controls, not semantic recognition or probability estimates. `region_search` records every acceptance, refinement or skip, the active threshold and realised coverage, including explicit `finding-interval` decisions. Native source rectangles remain distinct from resized target rectangles. Structural histories retain exact placement geometry and require `contribution_policy: "single-current-frame"`; an explicitly marked empty search is valid, while unmarked or malformed empty histories remain invalid.

New outputs use `desaparecidos.uy/output-sidecar/3.0`. Canonical and compatibility outputs now contain:

- complete `desaparecidos.uy/placement-history/1.0` placement histories;
- exact input-manifest hashes, runtime Git commit and working-tree state;
- target source, licence, image-hash, metadata-source and review provenance;
- a reference to the exact `desaparecidos.uy/refusal-paradata/1.0` policy revision;
- a computed `desaparecidos.uy/temporal-causality-evaluator/1.0` result and evaluated-history hash.

`future_source_frames_used` is derived from the evaluator for **Seguimos buscando**. A violation or malformed placement history fails rendering before media finalisation. Exhibition manifests hash every segment video, sidecar and evaluation; publication binds them to the declared artwork and target, recomputes their evaluation, and validates provenance before copying any file.

The core conversational-memory state model added on 8 August remains intentionally separate from the image runtime. It models participant consent, utterance provenance, uncertainty, correction and withdrawal without adding an LLM provider, speech service or persistence backend. Real testimony must not be committed as a test fixture.

Public reuse is now explicitly scoped. Software source and associated technical documentation authored by Tomas Laurenzo are MIT-licensed; the `Seguimos buscando` public-performance protocol is CC BY 4.0. Historical portraits, canonical person records, third-party/source imagery, participant material and generated memorial outputs are excluded from those blanket grants unless item-level rights state otherwise. This licensing change does not change the implementation boundary: direct ingestion of self-captured participant sequences and a reviewed human-performed pilot remain unfinished.

## Active focus

Current revision: full reconstruction is mandatory for normal video output across the triptych. Missing regions take precedence over refinements; wider source crops and a dense analysis grid are searched at unchanged destination sizes and native resolution. The fragment works use 48–384 px regions, an eight-encounter cadence and one encounter per unique reviewed source. The ignored people manifest contains 2,001 quality-reviewed rows: 1,856 approved and 145 rejected; 1,849 approved rows are eligible at runtime because seven fail current file-hash verification. The ignored place manifest contains 1,928 quality-reviewed rows: 1,834 approved and 94 rejected, all approved rows currently eligible. The traversal work retains one contribution per frame and its 96–384 px default. Single-target Uruguay searches can acquire additional CV-approved batches. Resource/network limits save progress instead of emitting an incomplete ending.

The active focus is artistic review of the common long-search form. The current Elena **Todos somos familiares** and **Están en todas partes** editions each run exactly 620 seconds; the current Elena **Seguimos buscando** reference runs 624 seconds. Every existing video remains preserved. All editions remain internal review artefacts rather than publication evidence.

Publication/article evidence still requires explicit target historical-identification and portrait-rights decisions, a clean committed runtime, full output review and figures derived from the exact hash-bound outputs. The implementation and internal preview do not resolve those separate requirements.

## Architecture overview

The localhost administration surface and canonical render path share reviewed inputs. Output accountability remains beside the generated media and feeds evaluation and release rather than becoming a generic compliance system.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 980 390" role="img" aria-labelledby="architecture-title architecture-desc">
  <title id="architecture-title">desaparecidos.uy architecture</title>
  <desc id="architecture-desc">Reviewed target, source and traversal inputs enter the local and canonical runtimes. Generated media and versioned sidecars are evaluated before exhibition and publication.</desc>
  <rect x="0" y="0" width="100%" height="100%" fill="#fff"/>
  <defs>
    <marker id="architecture-arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="#333"/>
    </marker>
  </defs>
  <g fill="#f5f5f5" stroke="#333" stroke-width="2">
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
    <text x="430" y="149" font-size="12">shared video / structural search</text>
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

Structural traversal decisions record accepted, refined and skipped regions. Temporal validation checks one contribution per current frame before output finalisation. Publication has a separate preflight so a corrupted history, stale evaluation or mismatched artifact cannot coexist with a nominal release decision.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1140 300" role="img" aria-labelledby="flow-title flow-desc">
  <title id="flow-title">Render, validation and publication flow</title>
  <desc id="flow-desc">A render builds placement histories, evaluates temporal causality, hashes valid artifacts, undergoes human review and passes publication preflight. Invalid histories stop without a final output.</desc>
  <rect x="0" y="0" width="100%" height="100%" fill="#fff"/>
  <defs>
    <marker id="flow-arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="#333"/>
    </marker>
  </defs>
  <g fill="#f5f5f5" stroke="#333" stroke-width="2">
    <rect x="20" y="55" width="150" height="75" rx="8"/>
    <rect x="205" y="55" width="160" height="75" rx="8"/>
    <rect x="400" y="55" width="160" height="75" rx="8"/>
    <rect x="595" y="55" width="160" height="75" rx="8"/>
    <rect x="790" y="55" width="160" height="75" rx="8"/>
    <rect x="985" y="55" width="135" height="75" rx="8"/>
    <rect x="205" y="205" width="160" height="65" rx="8" fill="#ededed"/>
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

The completion flow keeps missing regions in search. A complete portrait may be refined within the playback budget; unavailable material pauses the job without an incomplete ending. Automatic acquisition applies to single-target Uruguay traversals.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 340" role="img" aria-labelledby="completion-title completion-desc">
<title id="completion-title">Completion-first traversal</title>
<desc id="completion-desc">Search approved material until every region is covered. Add material when needed, or save progress and pause. Refine a complete portrait within the playback budget, then render the closing sequence.</desc>
<rect width="1000" height="340" fill="white"/>
<defs><marker id="completion-arrow" markerWidth="9" markerHeight="8" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#333"/></marker></defs>
<g fill="#f5f5f5" stroke="#333" stroke-width="2">
<rect x="20" y="45" width="160" height="85" rx="8"/>
<rect x="220" y="45" width="180" height="85" rx="8"/>
<rect x="440" y="45" width="150" height="85" rx="8"/>
<rect x="630" y="45" width="160" height="85" rx="8"/>
<rect x="830" y="45" width="150" height="85" rx="8"/>
<rect x="425" y="230" width="180" height="75" rx="8"/>
<rect x="770" y="230" width="210" height="75" rx="8"/>
</g>
<g fill="none" stroke="#333" stroke-width="2" marker-end="url(#completion-arrow)">
<path d="M180,88 H220"/><path d="M400,88 H440"/><path d="M590,88 H630"/><path d="M790,88 H830"/>
<path d="M515,130 V230"/><path d="M425,267 H100 V130"/><path d="M605,267 H770"/>
</g>
<g font-family="sans-serif" text-anchor="middle" fill="#111">
<text x="100" y="80" font-size="15">Approved material</text><text x="100" y="104" font-size="12">saved on disk</text>
<text x="310" y="80" font-size="15">Search missing regions</text><text x="310" y="104" font-size="12">native crop verification</text>
<text x="515" y="93" font-size="15">Full coverage?</text>
<text x="610" y="77" font-size="11">yes</text><text x="540" y="185" font-size="12">no</text>
<text x="710" y="80" font-size="15">Bounded refinement</text><text x="710" y="104" font-size="12">within playback budget</text>
<text x="905" y="80" font-size="15">Render</text><text x="905" y="104" font-size="12">face + closing sequence</text>
<text x="515" y="257" font-size="14">Add approved material</text><text x="515" y="280" font-size="12">acquisition / review</text>
<text x="260" y="250" font-size="12">new source frames</text>
<text x="688" y="249" font-size="10">unavailable / batch limit</text>
<text x="875" y="258" font-size="15">Save progress and pause</text><text x="875" y="282" font-size="12">resume from saved material</text>
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

- `DESAPARECIDOS_YUNET_MODEL` optionally identifies a local OpenCV YuNet face detector model for the stricter people-source quality pass and runtime gate. The current ignored local model is `data/raw/models/face_detection_yunet_2023mar.onnx`, SHA-256 `8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4`. Without the setting, the policy uses the bundled frontal-face cascade plus an independent eye cascade. Neither path performs identity matching.

- `MAPILLARY_ACCESS_TOKEN` is required only for live Mapillary discovery/acquisition. Do not commit it.
- `BACKEND_PORT` and `FRONTEND_PORT` optionally set preferred launcher ports; the launcher moves to free localhost ports when needed.
- `VITE_API_BASE` is set by `start.sh` for the local frontend.
- `config/exhibition-triptych.example.json` is the exhibition-plan template.
- `config/refusal-paradata.json` is the versioned refusal-policy source of truth.
- `web/publication.example.json` uses `desaparecidos.uy/web-publication/2.0` and requires reviewer/date/non-endorsement fields for each published work.
- Pillow is constrained to `>=12.3,<13` because the earlier permitted 12.2 release has known vulnerabilities; the frontend lockfile similarly pins audited transitive `nanoid` and `postcss` releases.

## Important files and directories

- `src/desaparecidos/artwork_runtime.py` — canonical renderer.
- `src/desaparecidos/structural_search.py` — abstaining multiscale correlation search and refinement.
- `src/desaparecidos/search_video.py` — shared four-phase compositor, exact encounter scheduler and presentation metadata.
- `frontend/src/VideoControls.tsx` — common artist presentation controls.
- `src/desaparecidos/refusal_paradata.py` — refusal validation, rendering and sidecar policy provenance.
- `src/desaparecidos/target_provenance.py` — target provenance snapshots and validation.
- `src/desaparecidos/evaluation.py` — artwork metrics and temporal-causality evaluator.
- `scripts/render_exhibition_triptych.py` — hash-bound three-channel render plan.
- `scripts/publish_static_memorial.py` — reviewed publication preflight and copy.
- `scripts/record_target_review.py` — explicit human historical-identification or portrait-rights decision recording.
- `data/persons/disappeared.json` — canonical person corpus.
- `assets/targets/disappeared/selected/` — reviewed selected target derivatives.
- `data/manifests/` — tracked templates/exports and ignored local review manifests.
- `data/raw/` and `outputs/` — ignored local source, traversal, cache and generated artifacts, except the explicitly selected MP4 listed under Recent changes.
- `doc/artistic-computational-principles.md` — governing artistic hierarchy.
- `doc/development-roadmap.md` — checked implementation state and remaining artistic work.
- `doc/artwork-runtime.md` and `doc/output-sidecar-schema.md` — runtime and evidence contracts.
- `doc/refusal-paradata.md` — generated public refusal record.
- `LICENSE`, `LICENSE-PROTOCOL.md` and `LICENSING.md` — explicit software/protocol licence grants and exclusions for historical, third-party, participant and generated material.

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

### Refusal-policy correspondence for the AI & Society R15 revision

- Expanded the versioned refusal record to explicitly document synthetic ageing, facial animation and generated speech, alongside the existing representational boundaries. Added anticipatory fragment assembly for the current causal video form of **Todos somos familiares** and **Están en todas partes**; the traversal record retains its stable identity and scope.
- Archived the previous policy byte-for-byte at `config/refusal-paradata/memorial-refusals-2026-01.json`. New outputs reference `memorial-refusals-2026-02`; historical output records retain their original policy identity and must be checked against that archived revision.
- Clarified that a technically available alternative need not already have an enabled code path for the artist to record why it is withheld. This documents constitutive decisions without adding image-generation, animation, speech or identity-matching behaviour.
- R15 now follows the latest committed implementation and the 8 September Elena **Seguimos buscando** edition. The author supplied the matching MP4 and sidecar: full decoding and all 263 source/encounter correspondences passed independent checks, and new manuscript figures were extracted. Individual Mapillary credits still require the matching traversal manifest; the earlier Abeledo attribution is not reused. Historical runtime and release-review flags remain unchanged.
- Validation for this policy/documentation change: four focused refusal-policy tests passed; the sidecar test requiring a runtime Git checkout was deselected in the partial validation workspace. After integration, two stale sidecar assertions were aligned with `memorial-refusals-2026-02`; their focused tests and the full 235-test Python suite pass. Earlier full-suite results below belong to their dated implementation changes.

### 9 September 2026 — repository-boundary cleanup

- Removed the misplaced `doc/writings/` academic-writing material and `doc/submissions/` Premio Nacional application package from `main`, and removed the requested AI & SOCIETY manuscript from `paper/ai-society-open-forum`. Added explicit ignore rules so those owner-repository packages are not reintroduced on the cleaned branches.
- Preserved the project-native historical source archive by moving `doc/writings/references/DDHH/` and the five consolidated historical volumes to the policy-defined `doc/DDHH/` path. Updated all active corpus provenance references and tests to the new path without changing source bytes.
- Verified the Desaparecidos grant/final-report package in `krahd/grant-applications`, the Premio Nacional owner package in `krahd/professional-opportunities`, the AI & SOCIETY workspace in `krahd/research`, and the project/ownership record in `krahd/tom-work-admin`. Exact misplaced files absent from their canonical owner repositories were recovered there before deletion.
- The cleanup uses ordinary commits and does not rewrite Git history. Historical commits retain the earlier blobs unless a separate history-purge operation is explicitly authorised.

### 8 September 2026 — expanded candidates and higher-fidelity Elena fragment editions

- Expanded the ignored people corpus through bounded, same-domain, robots-aware Wikimedia Commons category crawls. Per-host image throttling and bounded 429/503 backoff prevent the image requests from overwhelming page-level pacing. Exact and perceptual deduplication remain active. The artist authorised approval for these internal tests only after the current quality pass.
- Raised the people gate to CV policy 4. It requires a landmark-bearing YuNet detection when `DESAPARECIDOS_YUNET_MODEL` points to the ignored local model, or independent frontal-face and eye detections as fallback. The quality pass stores the verified face rectangle; runtime checks the recorded SHA-256 before revealing that crop. It performs no identity matching. The resulting ignored people manifest has 1,856 approved and 145 rejected rows; 1,849 are runtime-eligible.
- Expanded the place corpus by re-gating and deduplicating approved Uruguay traversal frames, then acquiring an additional bounded all-Uruguay Mapillary route. The new route covers urban and rural samples including Montevideo, Las Piedras, Barros Blancos, Pando, Ciudad de la Costa, Maldonado, Trinidad, Colonia, Salto and Rivera. The resulting ignored place manifest has 1,834 approved and 94 rejected rows; all approved rows pass the runtime gate.
- Fragment search now refuses to cycle sources. Each eligible manifest row appears no more than once; a 600-second complete search at the default cadence requires 1,819 unique eligible rows. Sidecars record the requirement, unique-stream policy and a repeated-source count. The refinement pass uses the complete nominal encounter budget, an eight-encounter finding interval and a 0.005 improvement margin, producing 228 spatially overlapping placements in each new edition.
- Rendered the new Elena **Todos somos familiares** internal edition at `outputs/stage1/todos-somos-familiares-quinteros-almeida-elena-candida-61-20260908223931.mp4`, with matching still, sidecar and evaluation. Its 1,819 unique face encounters contain 228 contributions and 1,591 non-contributions, with zero repeats and 100% coverage. Independent low-level luminance correlation is 0.981. SHA-256: `213fa63fa87105e40b48c6db2a14795df60cd50c5cb3595a74ed27b2066cc442`.
- Rendered the new Elena **Están en todas partes** internal edition at `outputs/stage1/estan-en-todas-partes-quinteros-almeida-elena-candida-67-20260908225654.mp4`, with matching still, sidecar and evaluation. Its 1,819 unique place encounters contain 228 contributions and 1,591 non-contributions, with zero repeats and 100% coverage. Independent low-level luminance correlation is 0.977. SHA-256: `c2ca46368711cf114b7dd8880be1ae27f7b557e74b22cd711302d23ba24a47ed`.
- Both new videos are separate 1920×1080 H.264/yuv420p files at 24 fps, 14,880 frames and exactly 620 seconds. Causal evaluation reports no violations or future-source use. Earlier videos and intermediate renders were not overwritten or deleted.

### 8 September 2026 — long structural search across the triptych

- Replaced the fixed-tile fragment-video path in both maintained runtimes with the same causal structural-region search used by **Seguimos buscando**. One encounter can transfer only its corresponding source subregion; 96–768 px square and rectangular regions accumulate at exact target positions, overlap, and support later refinement. Normal fragment-video generation now fails rather than emitting an incomplete portrait.
- Standardised new video defaults on a metaphorical long search: 600 search seconds, about three encounters per second, a 30-encounter finding interval, 0.75-second transfers and the common 20-second closing form. GUI, API and CLI defaults were aligned; single-target outputs are normally 620 seconds. The continuous scheduler now consumes the full search budget and reserves time for the final transfer.
- Tightened **Todos somos familiares** to a face-and-eye-confirmed stream. Of 113 approved reviewed people crops, 30 pass the conservative runtime gate; the excluded 83 are listed in the sidecar and never displayed. Deterministic shuffled cycles create the long search, with at most three separated contributions per underlying source. No identity matching is performed.
- Added `desaparecidos.uy/fragment-search/2.0`: every event records its underlying manifest source, structural decision, exact rectangles, similarity, coverage and exclusion/display policy. Placement histories retain event IDs for causality while participation evaluation can use `manifest_source_id` for accurate source counts.
- Rendered a new Elena **Todos somos familiares** edition at `outputs/stage1/todos-somos-familiares-quinteros-almeida-elena-candida-37-20260908150433.mp4`, with matching still, sidecar and evaluation. It is 1920×1080 H.264/yuv420p, 24 fps, 14,880 frames and exactly 620 seconds. Its 1,778 displayed encounters contain 60 contributions and 1,718 non-contributions; 60 variable overlapping/refining regions reach 100% coverage. Final-image luminance correlation with the reference portrait is 0.960. SHA-256: `662b9816a9c7f5614a1156e0d1db0ad623daf804aa32a0d6b51bc62dc439d504`.
- Rendered a new Elena **Están en todas partes** edition at `outputs/stage1/estan-en-todas-partes-quinteros-almeida-elena-candida-41-20260908150902.mp4`, with matching still, sidecar and evaluation. It has the same Full HD/24 fps/14,880-frame/620-second format. Its 1,818 displayed encounters contain 60 contributions and 1,758 non-contributions; 60 variable overlapping/refining regions reach 100% coverage. Final-image luminance correlation is 0.934. SHA-256: `f677da0c93f13ea781e9ee59eeeb16b32d1c5aa5672be9dfece9b28477f74148`.
- Both videos passed full decode and causal evaluation with zero future-source violations. Representative early, middle, late and final frames were inspected. Earlier drafts and all pre-existing videos remain untouched.

### 8 September 2026 — superseded fixed-tile fragment-search draft

- Changed both maintained fragment render paths so **Todos somos familiares** and **Están en todas partes** show an actual approved-source search on the left while reconstruction accumulates on the right. The chronological stream now retains selected approved images that contribute nothing; contributing sources launch their matched fragments at their own encounter. Several fragments from one source arrive together. The 0.16-second default scan cadence continues while 0.75-second transfers may overlap later scans.
- Added `desaparecidos.uy/fragment-search/1.0` sidecar records with every displayed source, `scan`/`contribute` decision, contribution count and aggregate encounter counts. Placement histories use the same source sequence and encounter indexes. The candidate cap bounds the initial scan pool but cannot omit a source that contributes to the final reconstruction.
- Recorded the artist-directed display exception explicitly: only approved manifest sources may enter these videos. **Todos somos familiares** displays the approved reviewed face region and never its surrounding photograph; **Están en todas partes** displays approved place images. Pending and rejected candidates remain excluded.
- Rendered a new separate Elena **Todos somos familiares** edition at `outputs/stage1/todos-somos-familiares-quinteros-almeida-elena-candida-37-20260908112647.mp4`, with matching still, sidecar and evaluation. It is 1920×1080 H.264/yuv420p at 24 fps, 1,043 frames and 43.458333 seconds. Its 113 encounters contain 77 contributing and 36 non-contributing face regions; 300 fragments complete the image. Full decoding and causal evaluation passed. SHA-256: `5672929347c1faec535d54446ee9cd2012deb346aa99fd9cf2fe4739cf09af12`.
- Rendered a new separate Elena **Están en todas partes** edition at `outputs/stage1/estan-en-todas-partes-quinteros-almeida-elena-candida-41-20260908112726.mp4`, with matching still, sidecar and evaluation. It is 1920×1080 H.264/yuv420p at 24 fps, 1,595 frames and 66.458008 seconds. Its territorially balanced 251 encounters contain 157 contributing and 94 non-contributing place images; 300 fragments complete the image. Full decoding and causal evaluation passed. SHA-256: `c3cc2e401874e7e59d6d4c89c8f67b03b2ce15c5f3d201bc75c46aabc297dde4`.
- Both outputs remain internal review artifacts. Their low-level luminance correlations are 0.407 for the people-source mosaic and 0.852 for the place-source mosaic; these metrics do not determine memorial adequacy or verify identity. Representative contributing, non-contributing, late-search and final-image frames were visually inspected. No existing video was replaced.

### 8 September 2026 — longer Elena Quinteros reconstruction

- Compared deterministic 600- and 900-second search studies using the approved mixed-region settings. Their reconstruction similarities were 0.965 and 0.969, with independent low-level luminance correlations of 0.984 and 0.988 respectively. The 600-second search was selected because the additional five minutes produced a substantially smaller gain.
- Rendered a new, separate Elena edition at `outputs/stage1/seguimos-buscando-route-20260905033506-2702c8a4-29-20260908075903.mp4`, with matching still, sidecar and evaluation. It contains 263 accepted findings across 1,818 encounters, a minimum gap of six and mean gap of 6.92 encounters, complete coverage and 0.965 reconstruction similarity. The seven realised sizes are 96×96, 96×192, 192×96, 192×192, 192×384, 384×192 and 384×384.
- The new MP4 is 1920×1080 H.264/yuv420p at 24 fps, exactly 14,976 frames and 624 seconds. Full decoding passed; causal evaluation reports no violations or future source use, and low-level luminance correlation is 0.984. SHA-256: `a50897983613dfeb70c2a835c40be5412a4642fa32cd77dc30a7666dc64cc818`. It remains `internal_unreviewed`; existing videos were not changed, and the Abeledo reference hash remains unchanged.

### 7 September 2026 — mixed-region traversal pacing

- Added `finding_interval` across the structural matcher, CLI, FastAPI request model and artist interface. The control enforces a minimum number of chronological traversal encounters between accepted findings while retaining every intervening frame in the search animation. Playback spacing remains an independent control. The default finding interval is one for compatibility.
- Replaced the GUI's fixed broad-portrait preset with **Use mixed-region traversal settings**: 96–384 px exact-position rectangles, broad structural comparison, per-region tone matching, 0.60 acceptance, 0.96 bounded quality goal and six-encounter finding/playback intervals.
- Added one autonomous Uruguay continuation route, `route-20260908043539-3fc4fa17`: 503 discovered frames across 12 regions, 481 CV-accepted and 22 pending; 327 deduplicated approved frames joined the main traversal, which now contains 2,778 frame records. A 0.62 spaced study remained at 99.8% coverage and correctly produced no output; the 0.60 candidate completed.
- Rendered a new separate Elena edition at `outputs/stage1/seguimos-buscando-route-20260905033506-2702c8a4-29-20260908050931.mp4`, with matching still, sidecar and evaluation. It contains 113 findings across 909 encounters, a minimum gap of six and mean gap of 8.07 encounters, 100% coverage and 0.953 reconstruction similarity. The seven realised sizes are 96×96, 96×192, 192×96, 192×192, 192×384, 384×192 and 384×384.
- The MP4 is 1920×1080 H.264/yuv420p at 24 fps, exactly 7,776 frames and 324 seconds. Full decoding passed; causal evaluation reports no violations or future source use, and low-level luminance correlation is 0.967. SHA-256: `b03823922f05717f74ccffa3b236194970bf11c527965c8ecf43b5e3d487ccd0`. It remains `internal_unreviewed`; existing videos were not changed.

### 7 September 2026 — denser Elena Quinteros reconstruction

- The first Elena **Seguimos buscando** attempt was artistically rejected because 30 variable regions, including regions up to 768 px, produced a technically complete image that did not preserve the recognisable portrait. That output remains a separate ignored internal artifact; it was not used as the basis of the new edition.
- Rendered a new, separate edition at `outputs/stage1/seguimos-buscando-route-20260905033506-2702c8a4-17-20260907220724.mp4`, with matching still, sidecar and evaluation. It uses a fixed 96 px grid, 540 distinct causal traversal frames, broad structural matching, per-region tone matching and complete coverage. Search pacing was recalibrated to retain the Abeledo reference duration without changing the reference file.
- The MP4 is 1920×1080 H.264/yuv420p at 24 fps, 7,792 frames and 324.666667 seconds. Reconstruction similarity is 0.969; independent low-level evaluation reports luminance correlation 0.990 and explicitly does not perform face recognition or identity verification. It remains `internal_unreviewed`. SHA-256: `5db470610de765d969dd3614ee5608b8fede272136e6eb5af273577687c4ed86`.

### 6 September 2026 — Elena Cándida Quinteros Almeida internal video

- The artist approved `portrait-01` for Elena Cándida Quinteros Almeida. The canonical person record and derived target-manifest row are now approved for generation; target approval remains distinct from the still-pending historical-identification and rights reviews required for any public release.
- Rendered a new, separate internal **Seguimos buscando** video using the 5:24 Abeledo edition as its reference: `outputs/stage1/seguimos-buscando-route-20260905033506-2702c8a4-17-20260907014447.mp4`, with matching still, sidecar and ignored evaluation record. It retains the reference traversal, Full HD format, 24 fps cadence, 192–768 px regions, broad structural matching, exposure adjustment, six-encounter spacing, 300-second soft search budget and required complete coverage. No existing video was replaced.
- The reference's 0.72 threshold reached 97.7% coverage for Elena and remained there after two complete acquisition batches. A third bounded batch was retained and the final pass used the project's previously validated 0.60 complete-search threshold. The cumulative traversal now retains three new reversible continuation routes and 2,451 frames; the finished video reaches 100% coverage at encounter 958 with 30 causal contributions and whole-image similarity 0.931.
- The MP4 is 1920×1080 H.264/yuv420p at 24 fps, 7,789 frames and 324.541667 seconds. It remains `internal_unreviewed`; temporal causality is valid with no future sources used. SHA-256: `4dbd0a2fa3ab61b24c0112aab7107fc2cd9bd743cc955e79e123e680a0034c3c`. The incorrect 720 px **Todos somos familiares** render and its evaluation were removed; they can be regenerated from the recorded workflow if needed.

Final review edition: [`seguimos-buscando-route-20260905033506-2702c8a4-17-20260905034203-paced.mp4`](outputs/stage1/seguimos-buscando-route-20260905033506-2702c8a4-17-20260905034203-paced.mp4), with matching PNG and JSON. It retains 192–768 px regions, uses the 0.72 completion preset and reaches full coverage at encounter 220 before bounded refinement. Whole-image similarity rises from 0.900 at first completion to 0.932 (the earlier 167-second edition measured 0.926); mean accepted-region score is 0.835. The final 5:24 timing includes contribution spacing in the soft search budget and preserves the refined image pixel for pixel. The sidecar records the parent reconstruction hash under `retimed_from`; input hashes and causal history remain valid. Verification evidence is in ignored `outputs/stage1/structural-review/completed-verification.json`; video SHA-256 is `8372bbe407efedd519d4a762a96cfb77ef8d81ec8ccbf9345b30481f54895533`. This is an internal review artifact, not a publication-cleared output.

### 4 September 2026 — required completion and continuing acquisition

- Normal traversal rendering now requires full coverage. Source exhaustion triggers bounded additional Uruguay acquisition for single-target runs; failure saves `completion_search` and pauses without producing a final incomplete video.
- Added wider source scales and uncovered-region priority. Retained 192–768 px preset extents and real source pixels. Compared 0.82 against 0.72; the artist completion preset now uses 0.72, above the original study's 0.60, while the general default remains 0.82. Removed matching skips for contribution spacing.
- Moved spacing to playback and added a soft 300-second search budget; all encounters remain causal, with unmatched encounters accelerated as needed.
- Added CLI/API/GUI completion controls and explicit `--allow-incomplete` study mode. Full coverage takes precedence over duration. Refinement after coverage is bounded by the nominal playback budget, avoiding indefinite polishing.


### 4 September 2026 — stricter and spaced traversal search

- Added `contribution_interval` and `search_similarity` across both runtimes, CLI/API and artist controls, with spacing/quality/exhaustion evidence in sidecars and causal early stopping.
- Raised default acceptance to 0.82, retained region extents, and slowed traversal cadence to three encounters per second. The stricter portrait preset retains 192–768 px regions and an eight-second final-image hold.
- Added search-to-black and reconstruction fade-in, given-name-first card formatting, and website fade-in/hold/fade-out through the shared compositor; presentation schema is now 3.0.
- The 0.82 study records 52 contributions (19/19/9/5 by temporal quarter), versus the previous 192 (125/42/10/15); mean accepted score rises from 0.762 to 0.885, but coverage drops. The 0.72 study records 105 contributions (36/34/17/18), mean score 0.822. Region extents remain 192–768 px in both. The previous complete image scores 0.926 under the new whole-image metric; the current default goal is therefore 0.95. Calibration studies used a 0.90 goal and never reached it.
- The ignored 5:22 video and sidecar are `outputs/stage1/seguimos-buscando-route-20260905005030-cf1bfd70-17-20260905025502.*`; sampled closing frames are under `outputs/stage1/structural-review/stricter-closing-contact.png`. The earlier artist-selected video remains unchanged.
- Minimum spacing prevents early bursts but cannot guarantee uniform contributions when matching opportunities vary. Finite traversal exhaustion remains possible; the renderer does not acquire extra material automatically.


### 4 September 2026 — selected video tracked in Git

- The artist explicitly requested repository inclusion of the complete video, overriding the general generated-output exclusion for this MP4 only: [`seguimos-buscando-route-20260905005030-cf1bfd70-17-20260905005312.mp4`](outputs/stage1/seguimos-buscando-route-20260905005030-cf1bfd70-17-20260905005312.mp4).
- The selected file is the exact previously verified render: 37,878,902 bytes, SHA-256 `088e14bed54b1d2703d94e8f68af8d6245e3d9a28bd10b3e57847f6d381fe266`; `ffprobe` rechecked 4,012 H.264 frames at 1920×1080 and 167.166667 seconds. No rendering or source-code change was required.
- Generation settings, traversal/target provenance and the original `internal_unreviewed` review marker remain as recorded below and in the local JSON sidecar. Repository inclusion is artist-authorised; it does not alter the item-level licensing recorded in `LICENSING.md`. Source imagery, other outputs and the full local review sidecar remain ignored.

### 4 September 2026 — continuous traversal and complete portrait render

- Added continuous playback with independent source cadence and travelling regions; retained pause-on-contribution as an artist option.
- Sidecars record exact per-placement launch and landing frames and actual duration.
- First Git sync completed: project `f997de0`, administration `81c5af8`. Remote licensing and public-performance documentation were preserved.
- Acquired two bounded city-walk sets: 487/540 frames downloaded, 439/519 CV-approved, zero download errors. Combined 24 walks into 895 approved frames after omitting 63 repeated provider IDs or exact image hashes. Parent manifest hashes and original frame IDs remain in the ignored combined route manifest.
- Added broad/fine structural comparison and optional exposure adjustment after acceptance; the latter records gain, offset and clipped fraction and never copies target pixels. Matching prioritises uncovered regions before refinement. The artist screen includes the settings used for the complete portrait as a preset.
- Rendered `outputs/stage1/seguimos-buscando-route-20260905005030-cf1bfd70-17-20260905005312.mp4` with matching PNG and JSON sidecar: 100% coverage, 34 placements into empty areas, 158 refinements/overlapping improvements, 703 skipped frames. A refinement may also cover new pixels; every source contributes at most once.
- This internal study uses 192–768 px regions, broad structure, threshold 0.60, minimum structure 0.008, refinement margin 0.02 and region exposure adjustment. The source advances at six frames per second, transfers last 0.75 seconds, and the final image holds for eight seconds. Total: 4,012 encoded frames, 1920×1080 H.264 at 24 fps, 167.166667 seconds, 37,878,902 bytes.
- Media hashes and sampled-frame verification are retained under ignored `outputs/stage1/structural-review/complete-verification.json`; the sidecar retains input-manifest hashes. The output was rendered before the final source commit and remains `internal_unreviewed`; no target rights or historical-identification review state changed.

### 4 September 2026 — structural traversal and common monochrome form

- Replaced proportional tile filling and the found-fragment pool with one structurally qualified region per current frame, preserving skipped encounters and incomplete results.
- Added variable square/rectangular extents, largest-first selection and optional later refinement, with source rectangles, decisions and coverage in sidecars.
- Made all three production render paths share the 1920×1080 search-left/reconstruction-right sequence and complete image/details/text closing phases; removed colour output choices.
- Added artist controls and matching API/CLI settings, plus shared exhibition presentation options and separate traversal region settings.
- Preserved all search encounters and minimum holds by extending short requests; cached repeated held images rather than resizing them for every encoded frame.
- Extended causal validation to enforce one contribution per current frame and accept only explicitly marked empty structural searches.
- An initial threshold of 0.82 rejected all 13 local frames. Comparison at 0.65 and visual review of corresponding source/target regions informed the 0.72 starting threshold. This small local exercise is not general calibration.
- A 60-second, 1920×1080, 24 fps internal preview accepts eight of 13 approved frames, skips five and covers 11.1% of the portrait. The incomplete result, matching contours, closing cards and representative video frames were visually inspected. Sources, candidates, portraits and their review states were not changed.

### 4 September 2026 — complete Seguimos buscando video form

- Added one shared search-video compositor for the canonical runtime, compatibility CLI and localhost API/GUI path.
- Made split-screen 16:9 presentation the default, with traversal/search at left, incremental reconstruction at right and restrained source-to-destination marks.
- Added the complete Spanish closing sequence: completed fragment reconstruction, fade to black, name/date/detail card, fade, **Seguimos Buscando** card and final fade.
- Made **Seguimos buscando** grayscale-only while retaining overlay and alternating CLI/API overrides for deliberate use.
- Added Spanish date formatting, scalable fonts, explicit phase allocation and `search-video-presentation/1.0` sidecar metadata.
- Generated a 60-second, 1920×1080, 24 fps H.264 internal review render for `abeledo-sotuyo-horacio-adolfo` from 13 approved local traversal frames. The output remains ignored, `internal_unreviewed`, generated from a dirty worktree and unsuitable for publication evidence.

### 4 September 2026 — public reuse licensing and ZKM prototype boundary

- Added an MIT licence for software source and associated technical documentation authored by Tomas Laurenzo.
- Licensed the `Seguimos buscando` public-performance protocol under CC BY 4.0 while explicitly excluding historical portraits, canonical person records, third-party/source imagery, participant material and generated memorial outputs from blanket relicensing.
- Updated the public-performance document so the planned memorial and human-walk activation are consistently described as prototype behaviour rather than already deployed operation.
- The ZKM / Arte Útil submission text now leads with the implemented traversal invariant and explicitly states that participant-sequence ingestion, activation records and a reviewed human-performed pilot remain in development.
- No runtime behaviour or dependencies changed; no runtime tests were required for this documentation/licensing-only update.

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
- The Premio Nacional de Artes Visuales application materials are preserved in their canonical `krahd/professional-opportunities` package rather than in this project repository.

## Tests and verification status

Repository-boundary cleanup: `.venv/bin/python -m pytest -q` passed all 235 tests with the existing Starlette/httpx warning; `.venv/bin/python -m compileall -q src tests scripts`, `git diff --check`, frontend Vitest (eight tests), and the TypeScript/Vite build passed with the existing large-chunk advisory. Active provenance paths contain no reference to the removed `doc/writings/references/DDHH` location, both mandatory `STATUS.md` timestamps match, and the referenced files exist under `doc/DDHH/`. SHA-256 verification confirmed all 15 recovered PNAV files and both recovered AI & SOCIETY files are byte-identical to their source Git blobs.

Expanded-candidate/no-repeat/high-fidelity fragment revision: `.venv/bin/python -m pytest -q` passed with 235 tests and the existing Starlette/httpx warning; the focused CV, crawler, source-quality, structural and artwork-runtime subset passed 51 tests. `.venv/bin/python -m compileall -q src tests scripts`, `git diff --check`, frontend Vitest (eight tests) and the TypeScript/Vite build passed; the existing large-chunk advisory remains. Both new MP4s passed full `ffmpeg` decoding and `ffprobe` verification as 1920×1080 H.264/yuv420p at 24 fps, 14,880 frames and exactly 620 seconds. Sidecar invariants confirm 1,819 distinct displayed source IDs, 228 distinct contributing source IDs, zero repeats and 100% coverage in each work. Independent causal evaluations report no violations or future-source use; low-level luminance correlations are 0.981 for Todos and 0.977 for Están. The final stills and middle/late encoded frames were visually inspected against Elena's target portrait for portrait progression, face-crop-only people display, place-only source display and preservation of the irregular overlapping assembly.

Long structural-search revision: `.venv/bin/python -m pytest -q` passed with 227 tests and one existing Starlette/httpx warning. `.venv/bin/python -m compileall -q src tests scripts` passed. Frontend Vitest passed eight tests; the TypeScript/Vite build passed with the existing large-chunk advisory. Both new Full HD MP4s passed `ffprobe`, complete `ffmpeg -v error -i <video> -f null -` decoding and independent causal evaluation. Each is 14,880 frames / 620 seconds with 60 placements, complete coverage and zero future-source violations. Early, middle, late and final encoded frames were visually inspected.

Latest Elena Quinteros internal **Seguimos buscando** render: `ffprobe` confirmed 1920×1080 H.264/yuv420p at 24 fps, 14,976 frames and exactly 624 seconds; a full `ffmpeg -v error -i <video> -f null -` decode passed. The generated evaluation recomputed causal provenance successfully (263 placements; no violations or future source frames), reports low-level luminance correlation 0.984, and retains its explicit non-identification limits. Encoded frames at 60.00, 60.34, 300, 590, 605 and 623.5 seconds were visually inspected: the left traversal advances between findings, mixed rectangles travel to exact portrait positions, the completed profile is materially clearer and the closing sequence is intact. The Abeledo reference SHA-256 remains `8372bbe407efedd519d4a762a96cfb77ef8d81ec8ccbf9345b30481f54895533`. Focused structural/API/runtime/video tests passed (56); the full Python suite passed (224 tests, one existing Starlette/httpx warning); `.venv/bin/python -m compileall -q src tests scripts` passed; frontend tests passed (eight); `npm --prefix frontend run build` passed with the existing large-chunk advisory. Full-duration artistic review remains pending.

Completion revision: `.venv/bin/python -m pytest -q` — 224 passed; `.venv/bin/python -m compileall -q src tests scripts` — passed; frontend tests (eight) and build passed. Focused completion tests cover pausing without final video, bounded acquisition and duplicate/manual-review preservation, accelerated encounter playback, full-coverage stopping and native-resolution score verification. Final verification passed: 1920×1080 H.264 at 24 fps, 7,780 encoded frames, 324.166667 seconds, full ffmpeg decode, recomputed causality and sidecar provenance, 14 monochrome phase samples and a black final frame. The final still and encoded closing contact sheet were visually inspected. The updated inline completion-flow SVG was rendered with rsvg-convert and visually inspected. Browser interaction and full-duration artistic review remain separate checks.

Current stricter-search revision: `.venv/bin/python -m pytest -q` — 216 passed; focused structural/API checks — 37 passed; `.venv/bin/python -m compileall -q src tests scripts` — passed; `npm --prefix frontend test` — eight passed; `npm --prefix frontend run build` — passed. Existing Starlette/httpx and frontend chunk-size advisories remain. Full-HD 24 fps H.264 study: ffprobe confirms 7,736 frames and 322.333333 seconds; full ffmpeg decode passed; the final still and all closing phases were visually inspected. Browser interaction remains unverified. This study is an incomplete calibration, not an improved final portrait.

Verification of continuous traversal and the complete internal render on 4 September 2026:

- `.venv/bin/python -m pytest -q` — 210 passed; coverage includes continuous source movement during transfer, delayed deposition, final landing, uncovered-area priority, broad/fine exposure adjustment and API option forwarding.
- `.venv/bin/python -m compileall -q src tests scripts` — passed.
- `npm --prefix frontend test` — eight passed; `npm --prefix frontend run build` — passed. Existing Starlette/httpx and large-chunk advisories remain.
- Both CLI help surfaces expose playback, structure-scale and tone-mode options.
- Real H.264 render: `ffprobe` confirms 1920×1080, 24 fps, 4,012 frames and 167.166667 seconds. Full `ffmpeg -v error -i <video> -f null -` decode passed. Eight sampled encoded frames have identical RGB channels; transfer, accumulation, final face and closing-card contact sheets were visually inspected.
- Temporal-causality validation recomputed successfully from the final sidecar: no future source frames used. Canvas coverage is 1.0; all 192 contributions bind to distinct current encounters. Generated files remain ignored except the artist-selected MP4 now tracked in Git.
- Administration repository: validation and tracking audit passed (existing registry warnings); 102 unit tests passed in an isolated temporary PyYAML/jsonschema environment. The system Python lacked these development dependencies, so neither project's production dependencies were changed.
- Browser interaction remains unverified: no browser was available in the connected runtime.

Earlier verification of the structural-search change on 4 September 2026:

- `.venv/bin/python -m pytest -q` — 205 tests passed with the existing Starlette/httpx warning.
- Targeted API, video and structural tests — 35 passed, including custom artist options reaching both traversal endpoints and both fragment works.
- `.venv/bin/python -m compileall -q src tests scripts` — passed.
- `npm --prefix frontend test` — eight tests passed; `npm --prefix frontend run build` — passed with the existing chunk-size advisory.
- Canonical and compatibility H.264 smoke renders for both fragment works — passed; encoded durations match the shared timeline metadata.
- Inline status SVG diagrams — rendered with `rsvg-convert` and visually inspected.
- Real local H.264 preview — `ffprobe` confirmed 1920×1080, 24 fps, 1,440 frames, yuv420p and exactly 60 seconds; eight sampled frames had identical RGB channels. Source/target comparisons and the full timeline contact sheet were visually inspected.
- Browser GUI inspection could not run: the browser runtime reported no available connection and an empty browser list. UI verification is limited to transport tests, TypeScript compilation and the build.

Earlier local verification on 4 September 2026 (before structural search):


- `.venv/bin/python -m compileall -q src tests` — passed.
- `.venv/bin/python -m pytest -q` — 192 passed with the existing Starlette/httpx compatibility warning.
- `npm --prefix frontend test` — eight tests passed.
- `npm --prefix frontend run build` — passed with the existing large-chunk advisory.
- Short end-to-end H.264 smoke render — passed at 320×180, 18 seconds and 4 fps; the complete timeline was visually inspected.
- Full internal review render — passed at 1920×1080, 60 seconds and 24 fps. `ffprobe` confirmed H.264/yuv420p and exact duration; ten representative frames were pixel-wise grayscale; the contact sheet and closing cards were visually inspected; the sidecar records 8,560 temporally valid placements and zero causality violations.

Focused local verification on 1 September 2026:

- focused policy, evaluation, runtime, traversal, pipeline, person, publication and API tests — 91 passed with one dependency warning.
- Python 3.11, 3.12 and 3.14 compilation of `src`, `tests` and `scripts` — passed.
- `.venv/bin/python -m pytest -q` — 190 passed with one Starlette/httpx compatibility warning.
- `npm --prefix frontend test` — eight tests passed.
- `npm --prefix frontend run build` — passed with the existing large-chunk advisory.
- `npm --prefix frontend audit --audit-level=moderate` — zero known vulnerabilities after lockfile remediation.
- isolated `pip-audit` of the installed project environment — no known third-party vulnerabilities after upgrading Pillow; the local unpublished `desaparecidos-uy` package is not a PyPI audit target.
- `.venv/bin/python -m pip check`, `bash -n start.sh`, `git diff --check`, refusal-policy public rendering and JSON parsing — passed.

No final exhibition media, article figures or publication-cleared supplementary video have been produced. The complete portrait study is now selected for repository inclusion; its generation-time review marker remains unchanged.

Last recorded CI evidence remains GitHub Actions run `30145676564` from 25 July 2026: Python 3.11/3.12, frontend tests/build and launcher syntax passed. That run predates the current changes.

## Known issues, risks and limitations

- The current portrait is complete and its media checks passed. Other portraits may still pause at acquisition limits or network failure; missing source structure is never manufactured. Resume the saved traversal after a pause.
- Automatic continuation currently covers single-target Uruguay routes; drawn geometry and target sequences pause for explicitly extended approved material. Each continuation invocation is capped at eight acquisition batches by default.

- The user explicitly approved the prepared `tom-work-admin` summary after the initial automatic-review rejection. The summary has now been applied and checked against the approved text; administration synchronisation is complete.
- Finding spacing and playback spacing are now separate controls. A finding interval greater than one deliberately skips structural acceptance during intervening encounters while preserving those frames in chronological playback; this can require more Uruguay material before completion.
- The late completion threshold deliberately trades local structural strictness for the final uncovered 5% only. It never authorises weaker refinements and is recorded per decision, but its 0.45 default remains an artistic heuristic requiring output review.

- No target currently records the newly explicit historical-identification and rights-review states required for canonical article evidence. Existing `review_status=approved` values are generation gates, not rights clearance.
- The current approved canonical target row uses a permission note that still requires verification; it is not sufficient to claim an explicitly licensed paper artifact.
- A complete internal Abeledo video and its approved combined traversal exist, but the target lacks the independent historical-identification and rights decisions required for public or paper evidence. The render was produced before the final commit and remains `internal_unreviewed`.
- The internal renders record the prior Git commit with `working_tree_dirty=true`; publication preflight rejects such outputs, so future canonical evidence must be rendered from a clean committed revision.
- `Todos somos familiares` remains internal pending source policy, legal/contextual review and complete output review.
- Structural source-fragment metrics do not establish anonymity or source-person non-recognisability.
- Mapillary coverage and terms, route selection and CV acceptance shape traversal material; public use still requires review.
- Direct ingestion of self-captured participant sequences, public activation records and a reviewed human-performed `Seguimos buscando` pilot are not yet implemented/completed.
- Public removal/contact procedures and institutional/legal review are not yet complete.
- FastAPI's current test-client shim emits one Starlette/httpx compatibility deprecation warning; it does not affect the passing runtime tests but requires a future dependency-compatible migration.
- The frontend production build retains a non-blocking large-chunk advisory.
- Arbitrary fragment masks, live input, real-time rendering, sound and multi-channel synchronisation remain future artistic development. Variable rectangular traversal regions are implemented.
- Structural search uses bounded multiscale and dense crop candidates with native-resolution verification, not exhaustive semantic matching. The 895-frame internal edition reaches 100% coverage with its recorded broad-portrait settings. This is one artistic result, not a guarantee of completion or fidelity for another portrait or traversal.
- Continuous-video duration follows encounter count and cadence. The optional pause mode can make videos substantially longer than requested; metadata records the actual length in either mode.
- Browser interaction remains unverified in this session because no browser was connected.
- A live-tip audit still finds misplaced `doc/writings/` and/or `doc/submissions/` paths on eight legacy remote branches: `agent/mosaic-mode-trigger`, `automation/paper-artwork-figures-20260731`, `backup/summer-publication-plan-2026-06-22`, `feature/conversational-memory-v2`, `import-full-disappeared-corpus`, `submission-premio-nacional-2026`, `urucon-ci-verification` and `verification/artwork-runtime-20260725`. Exact owner-repository copies have been preserved, but deleting whole document trees from all eight remote branch tips requires separate explicit approval. Historical commits would still retain the blobs after ordinary cleanup commits.

## Pending tasks and next steps

Review the current long Elena edition for each of the three memorials, concentrating on face-crop acceptability, search/finding rhythm, region scale and final likeness. Test all three long-search defaults in a connected browser. Additional source material, walks or alternative matching settings remain artistic choices rather than missing prerequisites for these complete internal studies.

1. Review and explicitly record historical-identification and portrait-rights decisions for a carefully selected target; record reviewer and date.
2. Use a clean committed runtime revision for any canonical evidence render.
3. Render one canonical **Están en todas partes** output and re-render the approved **Seguimos buscando** traversal from that clean revision.
4. Generate evaluations and an exhibition manifest; complete full-duration, historical, rights, contextual and recognisability review.
5. Derive AI & Society figures and the supplementary MP4 only from those exact artifacts; retain derivative hashes in the manuscript repository.
6. Update the canonical manuscript repository with the resulting evidence state; the required `krahd/tom-work-admin` project record is already current.

For the ZKM / Arte Útil submission, the remaining project-level evidence improvement is a complete human-performed activation using self-captured encounter material. Until that exists, the submission must retain Prototype certification and prospective wording for the human-walk path.

## Longer-term steps

- Complete exhibition-quality loops and installation playback testing.
- Establish removal/contact procedures and complete appropriate legal and institutional review.
- Continue corpus consultation and source stewardship without presenting the project as an official archive.
- Develop unchecked roadmap items only when supported by the artwork: broader traversal sources, arbitrary masks, sound, installation synchronisation and future live forms.

## Decisions and rationale

- Artist direction on 4 September 2026 also requests steady low-fps traversal, readable travelling regions and one complete face. A successful full-coverage edition does not remove abstention or promise every traversal will complete a portrait.
- Artist direction on 8 September 2026 approves CV-accepted crawl candidates for internal testing, requests more face and place candidates where needed, and prioritises closer target resemblance while retaining a long, fast search with discoveries distributed through it. Category-invalid graphics and crawl-domain drift remain excluded despite that internal approval.
- Artist direction on 4 September 2026: monochrome throughout; landscape search-left/reconstruction-right; at most one structural contribution per traversal frame; skip inadequate structure; prefer large regions and allow better later replacements; share search → reconstructed image → details → text across the triptych.
- A partial reconstruction expresses the material found. No completion quota, target overlay or earlier-source fallback may conceal a failed search. Approved unmatched traversal frames remain visible as continuing search; this does not permit revealing rejected imagery or unreviewed contemporary contexts.

- Refusal paradata is artwork-specific. It records constitutive non-actions but does not create a general compliance ontology.
- Target approval, historical identification, portrait rights, public release and organisational endorsement remain distinct because one cannot evidence another.
- Rights clearance is permission for a stated use, never an implication that an archive, memorial organisation, relatives' organisation, rights holder or depicted person endorses the artwork.
- Temporal causality is an executable integrity property of **Seguimos buscando**, not a descriptive Boolean.
- Canonical figures and supplementary media must remain traceable to exact media, sidecars, evaluations, runtime commit, policy hash and input hashes.
- Sensitive source imagery, traversal caches and generated evidence stay outside version control, except the one MP4 explicitly selected by the artist for repository inclusion.
- Open licensing applies by layer: software under MIT and the public-performance protocol under CC BY 4.0; source portraits, canonical person records, third-party/participant material and generated outputs retain their own rights conditions.

## Documentation alignment notes

- `AGENTS.md`, `README.md`, `doc/artwork-runtime.md`, `doc/output-sidecar-schema.md`, `doc/refusal-paradata.md`, `doc/development-roadmap.md`, `web/publication.example.json` and this status report reflect the approved-source fragment search, 3.0 sidecar, presentation schema 3.0, structural search, common monochrome video form and current release contracts. The project-native historical sources now reside at `doc/DDHH/`; manuscripts and opportunity packages remain in their owner repositories.
- `doc/seguimos-buscando-public-performance.md`, `LICENSE`, `LICENSE-PROTOCOL.md` and `LICENSING.md` reflect the current prototype and public-reuse boundaries.
- `doc/STATUS.md` remains a pointer to this canonical report.
- The URUCON paper package remains in the external academic-writing repository and retains its previously recorded evidence revision. The current work supports a separate AI & Society improvement and does not silently rewrite that artifact.
- The required local `krahd/tom-work-admin/projects/desaparecidos-uy.md` summary now records the complete 5:24 edition, completion-first workflow and 224-test verification, preserving the earlier calibration record. The separate-repository update follows the user's existing approval. Existing changes were preserved; registry lifecycle state and deadline did not change.

Last updated: 2026-09-09 02:28 GMT-6
