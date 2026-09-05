# desaparecidos.uy Project Status

Last updated: 2026-09-04 21:04 GMT-6

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

The first two works support grid, irregular and overlap grammars, target salience, contribution/adjacency controls and territorial balancing. **Seguimos buscando** now searches variable rectangular regions using normalised grayscale organisation and signed directional gradients. Each approved traversal frame can contribute at most one region at its own encounter. Weak or structureless candidates are skipped; larger qualifying regions are preferred, and better later candidates may replace whole regions or smaller parts. Multiple coherent walks in a saved traversal accumulate into one portrait in single-target mode. Partial and entirely empty searches are supported without forced completion.

All three works use the same monochrome video form: search at left and reconstruction at right fades to black, the assembled fragment image fades in/out, followed by person details, closing text and https://desaparecidos.uy, each fading through black. Catalogue names are displayed given names first without a comma. Defaults are 1920×1080 landscape at 24 fps. The GUI/API/CLI expose playback mode, transfer and scan durations, image/details/text holds, fades, match marks and closing text. Continuous playback now follows encounter timing: at the traversal defaults the city advances at three source frames per second and crops travel for 0.75 seconds while it advances. Arrival remains causal and the final crop lands before the closing phases. The optional hold mode retains minimum-duration pauses. The artist interface, map, image/video previews and static memorial styles are monochrome; colour output requests are rejected. `search-video-presentation/3.0` records exact phase counts and actual duration.

Traversal reconstruction modes are `fixed`, `largest-first` and `refine` (default). Default minimum/maximum region extents are 96/384 px, structural threshold 0.82, minimum structure 0.035 and improvement margin 0.04. Broad structural comparison uses 8×8 samples by default; fine comparison retains 16×16. Uncovered areas take precedence over refinements. Optional `tone_mode=match-region` applies one recorded brightness/contrast transform after structural acceptance; `source` preserves exposure and remains the default. The artist screen includes a broad-portrait preset (192–768 px, threshold 0.82, minimum structure 0.008, refinement margin 0.02, exposure adjustment, six-encounter contribution spacing and a 0.95 reconstruction goal). These are heuristic artistic controls, not semantic recognition or probability estimates. `region_search` records every acceptance, refinement or skip and realised coverage. Native source rectangles remain distinct from resized target rectangles. Structural histories retain exact placement geometry and require `contribution_policy: "single-current-frame"`; an explicitly marked empty search is valid, while unmarked or malformed empty histories remain invalid.

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

Current revision: stricter matching and six-encounter spacing limit early contribution bursts; traversal cadence is now 0.33 seconds. Search continues until full coverage and a 0.95 similarity goal, or exhausts approved material. Similarity is the minimum of global structural correlation and `1 - grayscale MAE / 255`; it is not a calibrated fidelity measure. Region-size settings do not change during search. The 192–768 px preset is preserved with a stricter 0.82 acceptance threshold. A fresh 322.33-second full-HD study against the existing 895-frame traversal passed encoding/decoding and closing-card inspection, but exhausted its sources at 55.4% coverage and 0.516 overall similarity. It does not fulfil the desired complete, more accurate portrait. A 0.72 acceptance calibration reached 83.8% coverage and 0.792 similarity, also incomplete. More approved material or further matching work is required before a replacement edition is ready.

The active focus is the artist-directed structural search and common video form. The complete video has been explicitly selected by the artist for inclusion in the repository. The artist-directed low-fps traversal and a complete internal face reconstruction are implemented and rendered. The new 167.17-second video has 100% canvas coverage, using 192 contributions from 895 unique approved frames across 24 city walks. Artistic review of the full edition and browser interaction remain the next checks; this internal render does not establish public-release readiness.

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
- Preserved the Premio Nacional de Artes Visuales application text materials on `main`.

## Tests and verification status

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

- The user explicitly approved the prepared `tom-work-admin` summary after the initial automatic-review rejection. The summary has now been applied and checked against the approved text; administration synchronisation is complete.
- Spacing deliberately skips matching on intervening encounters; stricter thresholds may leave fewer matches in a finite source pool. Full coverage alone does not satisfy the new quality goal. Additional approved material may be needed.

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
- Structural search uses a finite multiscale lattice and two source scales, not exhaustive semantic matching. The 895-frame internal edition reaches 100% coverage with its recorded broad-portrait settings. This is one artistic result, not a guarantee of completion or fidelity for another portrait or traversal.
- Continuous-video duration follows encounter count and cadence. The optional pause mode can make videos substantially longer than requested; metadata records the actual length in either mode.
- Browser interaction remains unverified in this session because no browser was connected.

## Pending tasks and next steps

Review the new stricter render with the artist and test controls in a connected browser; if the quality target is unmet, extend the approved traversal material. Additional walks or alternative structural settings remain artistic choices, rather than a missing prerequisite for the current full-coverage study.

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

- `README.md`, `doc/artwork-runtime.md`, `doc/output-sidecar-schema.md`, `doc/refusal-paradata.md`, `doc/development-roadmap.md`, `web/publication.example.json` and this status report reflect the 3.0 sidecar, presentation schema 2.0, structural search, common monochrome video form and current release contracts.
- `doc/seguimos-buscando-public-performance.md`, `LICENSE`, `LICENSE-PROTOCOL.md` and `LICENSING.md` reflect the current prototype and public-reuse boundaries.
- `doc/STATUS.md` remains a pointer to this canonical report.
- The URUCON paper package remains in the external academic-writing repository and retains its previously recorded evidence revision. The current work supports a separate AI & Society improvement and does not silently rewrite that artifact.
- The required local `krahd/tom-work-admin/projects/desaparecidos-uy.md` summary now also records the stricter-search revision, verification and incomplete calibration outcomes. The user explicitly approved this separate-repository update; the applied paragraph matches the prepared summary exactly. Existing changes were preserved; registry lifecycle state and deadline did not change.

Last updated: 2026-09-04 21:04 GMT-6
