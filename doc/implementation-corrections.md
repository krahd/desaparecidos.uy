# Current implementation corrections

## Purpose

This note reconciles implementation descriptions that predate the canonical artwork runtime. It is normative for current technical behaviour. Conceptual and historical passages in `doc/desaparecidos-uy-project-description.md` remain valid unless contradicted here.

## Fragment extraction and source contribution

`max_fragments_per_source = 240` is an extraction ceiling: it limits how many candidate fragments may be extracted from one reviewed source image. It is not an output contribution quota.

The legacy Stage 1 path uses a default output contribution cap of one placement per source row. People-derived generation requires a positive cap. Place-derived generation may be configured as unlimited for experiments, although exhibition plans should state and justify their chosen policy.

The canonical `desaparecidos-artwork` runtime also defaults to one placement per source row. It requires a positive people-source cap and records the realised source usage in every sidecar.

The older statement that zero or unset contribution values are normalised to 240 output tiles is stale and must not be used to describe either current path.

## Placement model

The legacy GUI path retains regular target-tile assembly and its existing `grid` and `match` process-video staging layouts.

The canonical artwork runtime supports three final visual grammars:

- `grid`;
- `irregular`;
- `overlap`.

Irregular and overlapping outputs remain matched to explicit target sections, but their final position, scale, rotation, opacity and z-order are represented separately. Every canonical output persists a versioned placement history.

## Video reveal policy

The legacy process-video path may reveal approved place sources or the reviewed face region of a people source before fragment transfer.

The canonical artwork runtime uses a different default for people-derived work: it renders fragment emergence without revealing the raw contemporary source image. This is a source-person non-representation control, not an anonymity guarantee.

## Target salience

The canonical runtime can process target sections uniformly or according to an explicit portrait-oriented salience order. The salience model is hand-defined and target-side only. It does not identify, classify or infer attributes of source persons and is not described as facial-recognition technology.

## Territorial treatment

The canonical place runtime can balance a bounded source selection across reviewed territorial labels. Explicit `department` and `region` values take precedence; recognised Uruguay department names in `location_label` are secondary; unresolved material remains `unlocated`. This does not constitute or imply national coverage.

## Traversal causality

Both traversal paths preserve the rule that a fragment cannot participate before its source frame has been encountered. The canonical runtime additionally persists the encounter index for every placement and evaluates the resulting history for future-source violations.

## Evaluation

The canonical evaluation reports source participation, concentration, adjacency, visual grammar and temporal causality. Optional target comparison uses low-level luminance and gradient measures. These diagnostics do not measure memorial adequacy, establish identity, prove consent or guarantee anonymity.

## Publication status

Generated media remain internal or review-required until the relevant historical, source-rights, contextual, recognisability and full-duration review is complete. The static publisher requires an explicit operator acknowledgement and verifies media hashes, but it does not perform or replace those reviews.
