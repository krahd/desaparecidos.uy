# Canonical artwork runtime

## Status

The `desaparecidos-artwork` command and `src/desaparecidos/artwork_runtime.py` are the canonical artwork-oriented rendering path. The earlier `desaparecidos run-stage1` command remains available for compatibility, local GUI work, and comparison, but it does not define the future visual ontology of the project.

The canonical runtime follows `doc/artistic-computational-principles.md`: the memorial propositions determine the artistic operations; the artistic operations determine the computational requirements; publications describe the resulting work.

## Shared architecture

Every generated image is assembled from matched fragments, but the final composition is not restricted to a photomosaic grid. The supported visual grammars are:

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

The history schema is `desaparecidos.uy/placement-history/1.0`. The output sidecar schema is `desaparecidos.uy/output-sidecar/2.0`.

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

The renderer supports the same grid, irregular and overlap grammars as the other works. Its sidecar records:

- the route and provider attribution;
- approved frame identifiers;
- the frames assigned to each target;
- the causal frame index for every placement;
- the visual grammar and composition mode;
- `future_source_frames_used: false`.

Example render:

```bash
desaparecidos-artwork search \
  --traversal TRAVERSAL_ID \
  --targets data/manifests/targets.csv \
  --target-id PERSON_ID \
  --target-mode single \
  --composition overlay \
  --grammar overlap \
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

The report includes:

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
- `exhibition-manifest.json` with exact file hashes, settings and review requirements.

The triptych is not publication-ready until the required reviews listed in its manifest are complete.

## Static web publication

The `web/` directory is a minimal static memorial presentation. It contains no analytics, tracking, backend dependency or source corpus. It reads `publication.json` and displays only works explicitly marked `publish: true`.

After completing the required review, copy `web/publication.example.json`, set the publication decisions, and run:

```bash
python scripts/publish_static_memorial.py \
  outputs/exhibition-triptych/exhibition-manifest.json \
  web/publication.json \
  outputs/publication \
  --acknowledge-review
```

The publisher verifies every selected video against the SHA-256 digest in the exhibition manifest before copying it. It emits a self-contained static directory and `publication-audit.json`.

`--acknowledge-review` is a deliberate release gate. It records an operator decision; it does not perform or replace the review.

## Reproducibility and verification

- Python production dependencies have bounded compatible ranges; OpenCV remains exactly pinned because its NumPy compatibility is sensitive.
- The frontend uses its committed `package-lock.json` and `npm ci`.
- CI runs Python tests on Python 3.11 and 3.12, imports the local API, records resolved Python environments, runs frontend tests and production build, and checks the launcher syntax.
- Generated media, reviewed source corpora and local traversal caches remain outside version control.

No test or render should be reported as successful unless its command was actually executed and its result recorded.
