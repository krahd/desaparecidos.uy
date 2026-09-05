# Canonical artwork runtime

## Status

The `desaparecidos-artwork` command and `src/desaparecidos/artwork_runtime.py` are the canonical artwork-oriented rendering path. The earlier `desaparecidos run-stage1` command remains available for compatibility, local GUI work, and comparison, but it does not define the future visual ontology of the project.

The canonical runtime follows `doc/artistic-computational-principles.md`: the memorial propositions determine the artistic operations; the artistic operations determine the computational requirements; publications describe the resulting work.

## Shared architecture

Every generated image is assembled from matched fragments, but the final composition is not restricted to a photomosaic grid. For the first two works, the supported visual grammars are:

- `grid`: the original regular target grid, retained as a baseline and a valid visual strategy;
- `irregular`: deterministic scale, position and rotation variation without strongly layered fragments;
- `overlap`: deterministic scale, position, rotation, opacity and z-order variation that permits layered compositions.

Every output stores a versioned placement history. Each record identifies:

- the contributing source and fragment;
- the fragment rectangle within the source material;
- the target section to which it was matched;
- the final render geometry;
- its position within the output process;
- for traversal work, the frame after which the fragment became available.

The history schema is `desaparecidos.uy/placement-history/1.0`. The output sidecar schema is `desaparecidos.uy/output-sidecar/3.0`.

## Shared video form

All three memorials default to 1920×1080 landscape, 24 fps, grayscale only, with search on the left and reconstruction on the right. The shared compositor then shows the reconstructed image, Spanish person details and the memorial title or artist-supplied closing text. It never overlays the target portrait to manufacture completion. The artist interface is monochrome too.

`--contribution-seconds` (2.5), `--scan-seconds` (0.18, traversal only), `--final-hold-seconds` (4), `--details-hold-seconds` (3), `--text-hold-seconds` (2), `--fade-seconds` (1), `--closing-text`, `--hide-match-marks`, `--fps`, `--duration` and `--output-width` expose the presentation choices in both CLIs. Equivalent fields are available on the localhost artist screens/API. `--split-orientation stacked` is an optional override; the default is `side-by-side`. The deprecated colour flags are rejected.

Requested duration is a minimum: every encounter and closing phase is preserved, extending the video when required. A contribution appears one third of the way through its encounter; the remaining hold makes it inspectable. `video_presentation` records actual duration and phase allocations. Large fragment-work editions can therefore be much longer than their requested duration.

## Output accountability

Every canonical and compatibility output now carries the same minimum accountability record:

- the exact runtime Git commit and whether the working tree was dirty;
- SHA-256 hashes for the target, source and traversal manifests that governed the render;
- a target-provenance snapshot for every represented person;
- the refusal-policy identifier, schema, SHA-256 digest and applicable refusal identifiers;
- a versioned placement history and a computed temporal-causality record.

Development renders may record a dirty working tree. Publication rejects them: canonical evidence must have `working_tree_dirty=false` so the recorded commit identifies the exact runtime.

Target provenance keeps the target portrait's page URL, image URL, licence or permission basis, access date, manifest approval state and exact local-image SHA-256 digest. When the canonical target manifest is used, it also snapshots the canonical person store hash and field-level metadata source identifiers. Historical-identification review, portrait-rights review and output release remain separate records. Missing decisions are recorded as `not_recorded`; manifest approval is never promoted into historical or rights clearance. Every snapshot states that rights clearance does not imply endorsement by a source, archive, memorial organisation, relatives' organisation, rights holder or depicted person.

Human reviewers can record the two target decisions independently:

```bash
python scripts/record_target_review.py PERSON_ID historical-identification approved \
  --reviewer "REVIEWER" --reviewed-at "YYYY-MM-DD"
python scripts/record_target_review.py PERSON_ID rights approved \
  --reviewer "REVIEWER" --reviewed-at "YYYY-MM-DD"
```

The command records a supplied human decision; it does not inspect evidence or approve a target automatically. Re-export `targets.csv` after changing the canonical person store.

The complete field contract is documented in [output-sidecar-schema.md](output-sidecar-schema.md).

## Paradata of refusal

`config/refusal-paradata.json` is the artwork-specific `desaparecidos.uy/refusal-paradata/1.0` policy. It documents deliberately withheld technical relations, including generative facial completion, biometric identification, full-context contemporary-person reveal and anticipatory traversal assembly. It is not a general ethics ontology.

Validate and render it for curatorial use with:

```bash
python scripts/render_refusal_paradata.py --access public
python scripts/render_refusal_paradata.py --access restricted --output PRIVATE_PATH.md
```

The tracked public rendering is [refusal-paradata.md](refusal-paradata.md). `public` rendering omits restricted records; `restricted` rendering includes both access levels. The policy file remains the source of truth, and every output records its exact SHA-256 digest.

## Todos somos familiares

The runtime separates two requirements:

1. the documented target portrait must remain sufficiently perceptible to sustain the memorial encounter;
2. a contemporary source person must not become the represented subject of the result.

The current controls are deliberately limited and auditable:

- portrait-oriented target-section ordering prioritises explicit eye, mouth, central-structure and upper-silhouette regions;
- a positive per-source contribution cap is mandatory;
- the renderer can prohibit neighbouring target sections from using the same source;
- generated videos reveal the accumulating fragments rather than the raw contemporary source image;
- the sidecar records all controls and states that anonymity is not guaranteed;
- every people-derived result remains `internal_unreviewed` until complete human, legal and contextual review.

These controls reduce structural opportunities for source-person reconstitution. They do not constitute biometric anonymisation and must never be described as such.

Example internal render:

```bash
desaparecidos-artwork render \
  --artwork todos-somos-familiares \
  --targets data/manifests/targets.csv \
  --sources data/manifests/people.csv \
  --target-id PERSON_ID \
  --output outputs/artwork/people \
  --grammar irregular \
  --salience portrait \
  --source-cap 1 \
  --avoid-source-adjacency \
  --video
```

## Están en todas partes

Place sources may be ordered across explicit reviewed territorial groups before an optional source limit is applied. The ordering uses declared `department` or `region` fields when present, then recognises Uruguay department names in the existing `location_label`. Material without a defensible territorial label remains `unlocated`.

This mechanism does not claim national coverage. It prevents a large reviewed group from exhausting a bounded source selection before smaller reviewed groups can participate. The sidecar records available groups, realised usage and the absence of any coverage claim.

Example render:

```bash
desaparecidos-artwork render \
  --artwork estan-en-todas-partes \
  --targets data/manifests/targets.csv \
  --sources data/manifests/places.csv \
  --target-id PERSON_ID \
  --output outputs/artwork/places \
  --grammar overlap \
  --salience portrait \
  --source-cap 1 \
  --territorial-balance \
  --video
```

## Seguimos buscando

The search runtime retains the existing traversal acquisition and review system. It assembles each target strictly from the frames encountered within its assigned traversal segment. A placement may not use a source frame that the traversal has not yet reached.

The default `refine` method searches square and rectangular regions from `--fragment-size 96` through `--max-region-size 384`, selecting the largest qualifying rectangle on a bounded multiscale lattice. `--reconstruction-mode largest-first` preserves accepted regions; `fixed` uses only the minimum square size. Each source frame can supply at most one region, only at its own encounter. There is no found-fragment pool, per-frame filling quota or forced completion. The target persists across the coherent walks within a traversal. Empty areas stay black.

Matching compares normalised grayscale organisation and signed directional gradients. Flat regions are ineligible. The controls are `--structure-threshold 0.72`, `--min-structure 0.035` and `--refinement-margin 0.04`. Scores express this heuristic correlation, not semantic identification or calibrated confidence. Later replacements must improve both the current rectangle's measured structure and the recorded quality of every covered area by the margin. Refinement can replace a whole earlier region or a smaller part. Histories retain all contributions in encounter order, including superseded material; `source_usage` counts historical contributions.

Structural matches retain their exact target rectangles. The canonical search runtime therefore uses the `grid` placement grammar even for variable rectangles, and rejects jitter/rotation grammars that would move a match away from its correlated region. Search defaults to split composition, with overlay and alternating overrides available in the artist screen and CLI.

Before any media is finalised, the renderer evaluates every placement history. A violation raises an error, so an invalid traversal output is not written. Its sidecar records:

- the route and provider attribution;
- approved frame identifiers;
- the frames assigned to each target;
- the causal frame index for every placement;
- the visual grammar and composition mode;
- `video_presentation` version 2.0, including the canvas, grayscale palette, text, requested/actual duration and exact phase lengths;
- `region_search` decisions and coverage, including scores for unsuccessful searches;
- `contribution_policy: "single-current-frame"`, checked by the causal evaluator;
- explicit `empty_reason: "no-accepted-structural-regions"` for zero-placement searches; unmarked empty histories remain invalid;
- evaluator schema `desaparecidos.uy/temporal-causality-evaluator/1.0`;
- evaluated-history SHA-256, placement and violation counts;
- `future_source_frames_used`, derived from that evaluation rather than written as an assertion.

Example render:

```bash
desaparecidos-artwork search \
  --traversal TRAVERSAL_ID \
  --targets data/manifests/targets.csv \
  --target-id PERSON_ID \
  --target-mode single \
  --composition split \
  --grammar grid \
  --reconstruction-mode refine \
  --fragment-size 96 \
  --max-region-size 384 \
  --duration 60 \
  --output-width 1920 \
  --output outputs/artwork/search
```

## Artwork-derived evaluation

Run:

```bash
python scripts/evaluate_artwork_output.py \
  outputs/artwork/OUTPUT.json \
  --target-manifest data/manifests/targets.csv
```

The `desaparecidos.uy/artwork-evaluation/2.0` report includes:

- realised source participation, maximum source share, HHI and effective source count;
- same-source adjacency and largest connected same-source target region;
- overlap, rotation and opacity measures for the visual grammar;
- temporal-causality checks;
- optional low-level luminance and gradient comparison with the target image.

The report explicitly does not determine memorial adequacy, identity, consent or anonymity.

## Exhibition triptych

Copy `config/exhibition-triptych.example.json`, insert reviewed target and traversal identifiers, and run:

```bash
python scripts/render_exhibition_triptych.py \
  config/exhibition-triptych.json \
  --allow-internal-people-render
```

The acknowledgement permits a controlled internal render only. It does not mark `Todos somos familiares` as publishable. The command produces:

- one concatenated H.264 loop for each work;
- target-level segment videos and sidecars;
- an evaluation report for every segment;
- `desaparecidos.uy/exhibition-triptych/3.0` as `exhibition-manifest.json`, with exact video, segment-sidecar and evaluation hashes, settings and review requirements.

The triptych is not publication-ready until the required reviews listed in its manifest are complete.

## Static web publication

The `web/` directory is a minimal static memorial presentation. It contains no analytics, tracking, backend dependency or source corpus. It reads `publication.json` and displays only works explicitly marked `publish: true`.

After completing the required review, copy `web/publication.example.json`, set each selected work's `approved-for-publication` decision, reviewer and decision date, and run:

```bash
python scripts/publish_static_memorial.py \
  outputs/exhibition-triptych/exhibition-manifest.json \
  web/publication.json \
  outputs/publication \
  --acknowledge-review
```

The publisher performs a complete preflight before copying anything. It verifies every selected loop and segment video, sidecar and evaluation against the exhibition-manifest digests; binds each segment to the declared artwork and target; recomputes both temporal and structural evaluation records; validates target and refusal provenance; verifies the recorded history hash; rejects unresolved licence/permission notes and placeholder release metadata; and confirms the explicit release reviewer, ISO-8601 date and non-endorsement acknowledgement. It emits a self-contained static directory, `desaparecidos.uy/web-publication/2.0` configuration and `desaparecidos.uy/web-publication-audit/2.0` audit. Reusing a destination removes media for works that are no longer approved, preventing stale unpublished files from remaining in the static tree.

`--acknowledge-review` is a deliberate release gate. It records an operator decision; it does not perform or replace the review.

The tracked example publishes no work by default. Set `publish: true` only after replacing the decision fields with completed human-review records.

## Canonical article evidence

Article figures and supplementary media must be derivatives of exact canonical outputs, not independently assembled illustrations. The production sequence is:

1. select a target with explicit historical-identification and portrait-rights review;
2. render one **Están en todas partes** output and one approved **Seguimos buscando** traversal;
3. retain their media, sidecars, evaluations and exhibition-manifest hashes outside version control;
4. complete human and release review;
5. derive figures and the supplementary MP4 from those exact files, retaining derivative hashes alongside the manuscript package.

This repository does not currently contain a target with the newly explicit historical-identification and rights-review states recorded in the generation input. Existing `approved` target rows therefore must not be described as rights-cleared canonical paper evidence until those distinct reviews are completed.

## Reproducibility and verification

- Python production dependencies have bounded compatible ranges; OpenCV remains exactly pinned because its NumPy compatibility is sensitive.
- The frontend uses its committed `package-lock.json` and `npm ci`.
- CI runs Python tests on Python 3.11 and 3.12, imports the local API, records resolved Python environments, runs frontend tests and production build, and checks the launcher syntax.
- Generated media, reviewed source corpora and local traversal caches remain outside version control.

No test or render should be reported as successful unless its command was actually executed and its result recorded.

The exhibition example uses shared `video_options` and separate `traversal_reconstruction` settings. `traversal_fragment_size` controls traversal extent independently of the first two works. Durations can extend independently; multi-channel synchronisation remains future work.
