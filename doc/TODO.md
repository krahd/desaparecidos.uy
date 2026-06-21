# TODO and resolved questions

1. Improve the Target administration page by linking it to the Review images panel. Selecting a person or image in either panel should select the corresponding item in the other panel.
2. Clarify the “Missing” label in Target administration because it can be confused with the person being disappeared.
3. Create a page for the third artwork. Its videos should traverse Uruguay through sequences of Street View or similar street-level imagery. This is currently for internal research and artistic use; the university's lawyers will review source and publication terms before anything is made public.

## Implemented answers

### Target administration and image review

Target administration and Review images now share selection through an exact canonical person/target ID or unique matching portrait provenance. Selecting a person highlights and scrolls to its review image. Clicking a review image or its checkbox highlights and scrolls to the corresponding person.

Legacy rows with a unique matching portrait source or local portrait path are linked even when their row IDs differ. Rows without unique evidence remain selectable in Review images without changing the person editor. Cross-panel selection clears any Target administration filter/query that excludes the selected person, preventing apparently blank administration results. The Target administration toolbar remains visible while the person list and editor scroll. Unsaved target edits require confirmation before switching records. Selecting or processing a portrait does not automatically rewrite `targets.csv`; target-manifest export remains explicit.

### “Incomplete” terminology

The visible label is now **Incomplete**, not “Missing”. It describes the curation record, not the person's disappeared status.

A record is incomplete when any required curation information is absent:

- full name;
- date of birth;
- place of birth;
- date of disappearance or date of death;
- place of disappearance or place of death;
- a known remains status; or
- a processed selected portrait.

The backend compatibility fields remain named `missing_fields` and `missing_count`, but those names are not displayed in the interface.

### Seguimos buscando

**Seguimos buscando** now has its own `#seguimos-buscando` page and artwork-filtered output gallery.

The implemented workflow supports:

- interactive route and region authoring with MapLibre;
- GeoJSON and GPX route import;
- autonomous route discovery from a selected region and requested duration;
- a provider-neutral traversal contract with Mapillary as the first adapter;
- bounded acquisition and local caching under ignored `data/raw/traversals/`;
- metadata preview before acquisition;
- contact-sheet review with mandatory per-frame approval;
- deterministic rendering from captured frame order and camera direction;
- direct jump cuts between disconnected sequences;
- single-target videos and artist-ordered multi-target loops;
- traversal overlay, alternating traversal/assembly, and split-screen composition modes; and
- output sidecars recording route geometry, provider attribution, approved frame IDs, sequence jumps, target order, settings, source usage, and `release_status=internal_unreviewed`.

Only approved street frames already encountered in the traversal can contribute fragments to the current portrait state. Mapillary access uses the backend-only `MAPILLARY_ACCESS_TOKEN`; it is never stored in browser state, traversal metadata, sidecars, or logs. Public release remains subject to university legal review.
