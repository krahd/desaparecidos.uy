# Output sidecar schema

## Version

Current schema: `desaparecidos.uy/output-sidecar/3.0`.

Version 3 makes documentary and integrity fields mandatory across the canonical artwork runtime and compatibility output paths. It supersedes `desaparecidos.uy/output-sidecar/2.0` for new exhibition or publication evidence.

## Required accountability records

Every output contains:

- `refusal_policy`
  - `schema`: `desaparecidos.uy/refusal-paradata/1.0`;
  - `policy_id`: stable policy identifier;
  - `sha256`: digest of the exact policy file used;
  - `applicable_refusal_ids`: policy records whose scope includes the artwork;
- `runtime_provenance`
  - `git_commit`: runtime commit;
  - `working_tree_dirty`: working-tree state at render time, including untracked files;
  - `input_manifests`: role, path and SHA-256 for each target, source or traversal manifest;
- `target_provenance`: one immutable snapshot per target ID;
- `placement_history` or `placement_histories` using `desaparecidos.uy/placement-history/1.0`;
- `temporal_causality` using `desaparecidos.uy/temporal-causality-evaluator/1.0`.

All three works' videos contain `video_presentation` using `desaparecidos.uy/search-video-presentation/3.0`. It records the 16:9 canvas, grayscale palette, Spanish default labels, search layout, artist closing text, requested/actual duration, duration policy and exact frame allocation per phase and target. The common sequence is search/reconstruction fading to black, reconstructed image fading in/out, person details, closing text, and https://desaparecidos.uy fading in/out to final black. Website hold uses the text hold duration. Existing version 1.0 and 2.0 sidecars remain historical records.

Continuous playback records `playback_mode`, realised `encounter_seconds`, `transfer_seconds` and `placement_timing_by_target` (placement index, source encounter index, launch frame and landing frame relative to the target segment). Its `duration_policy` is `encounter-paced`: the requested duration does not slow the traversal, and the search phase includes the final transfer landing. `hold` retains minimum-duration pauses. The timing record describes delayed deposition; causal histories continue to bind each crop to the frame at which it was found.

Structural traversal outputs use `assembly_policy: "single-current-frame-structural-region"`. `region_search[target_id]` contains pixel coverage and one decision per encountered frame: `place`, `refine` or `skip`, reason, best tested similarity, and (when accepted) source/target rectangles, accepted score and placement index. `source_rect` records native source dimensions separately from resized target dimensions. The settings record `structure_scale` (`broad`/`fine`) and `tone_mode` (`source`/`match-region`). Accepted exposure-adjusted crops also record `tone_transform` with gain, offset and clipped fraction; matching precedes this transform. Histories retain replacements in chronological order. `contribution_policy: "single-current-frame"` requires each source to contribute at its own encounter, at most once, in strictly increasing encounter order. An empty search requires `empty_reason: "no-accepted-structural-regions"`, zero declared placements and a valid source sequence; ordinary empty or malformed histories are still rejected.


## Target provenance

Each target snapshot records:

- target ID and name;
- target-manifest path and manifest review state;
- target source page and direct image URL;
- licence or permission basis and access date;
- local target-image path and SHA-256;
- canonical person-store hash, record review state, metadata source IDs, field-source map and source references when the canonical manifest is used;
- separate historical-identification review state, reviewer and date;
- separate rights-review state, reviewer and date;
- current output-release decision, reviewer and date;
- `rights_clearance_is_not_organisational_endorsement: true` and the complete non-endorsement statement.

`target_manifest_review_status=approved` means only that the target row may participate in generation. It does not mean that historical identification, rights, organisational endorsement or public release has been approved. Missing independent decisions are recorded as `not_recorded`.

At the publication boundary, target provenance is stricter: canonical metadata source IDs must be recorded, and both historical-identification and rights review must be `approved` with a reviewer and date. The separate publication configuration must then record the output-release decision and reviewer.

Licence or permission text that still says it must be verified is an unresolved record, not a permission basis, and publication rejects it even when the other review states are approved.

`scripts/record_target_review.py` writes either human review to the canonical person record. It requires a reviewer for approved or rejected decisions and never derives a decision from a manifest or licence string.

## Temporal causality

The evaluator canonicalises and hashes the complete target-to-history mapping. It validates the placement-history schema, target binding, declared count, unique placement identifiers, source sequence and encounter indices. It records history and placement counts, violations, target-level reasons and the derived `future_source_frames_used` value. Rendering fails before media finalisation when the history is malformed or any placement uses a source before encounter, references an unknown source, or has an invalid encounter index.

Publication recomputes the evaluation. It rejects missing or stale evaluator records, changed history hashes, any violation and a top-level `future_source_frames_used` value that disagrees with the computed result.

## Release records

New exhibition manifests use `desaparecidos.uy/exhibition-triptych/3.0` and hash every segment video, sidecar and evaluation. New static publication configurations use `desaparecidos.uy/web-publication/2.0`; published works require an explicit decision, non-placeholder reviewer, ISO-8601 decision date and non-endorsement acknowledgement. Publication binds every segment to its artwork and target, recomputes its evaluation, verifies loop and segment media hashes, and requires `runtime_provenance.working_tree_dirty=false`, so the recorded commit identifies the complete runtime rather than only its last committed portion. The resulting audit uses `desaparecidos.uy/web-publication-audit/2.0`.

Traversal `region_search[target_id]` also records `reconstruction_similarity`, `encounter_count` and `stop_reason` (`quality-target-reached` or `approved-frames-exhausted`). Accepted decisions carry the current coverage and reconstruction similarity; spacing skips use `contribution-spacing` and have no tested similarity. `search_similarity` and `contribution_interval` are recorded settings. Similarity is the lower of whole-image structural correlation and `1 - MAE / 255`. The target segment and history contain only reached encounters when quality stops the search early; the input manifest and `approved_frame_ids` retain the available source pool.
