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
