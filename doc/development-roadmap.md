# desaparecidos.uy development roadmap

## Goal

Develop `desaparecidos.uy` into a serious, durable, extensible computational memorial whose three works are artistically complete, technically credible, suitable for public presentation, and capable of supporting future web, video, installation, interactive, and real-time iterations.

The roadmap is governed by `doc/artistic-computational-principles.md`. The artwork is primary. Technical and publication work must derive from it.

This is a completion goal, not a list of optional ideas. Items may be revised when artistic evidence changes, but they should not be silently abandoned.

## 1. Shared artistic and computational architecture

- [x] Replace the implicit fixed-grid ontology with a general fragment-placement model.
- [x] Preserve the existing grid renderer as one visual strategy.
- [x] Add irregular non-overlapping placement.
- [x] Add overlapping and layered placement with opacity and z-order.
- [x] Support variable rectangular regions for traversal search.
- [ ] Support arbitrary fragment masks and variable regions across the remaining grammars.
- [ ] Support fragment scale, rotation, entrance time, exit time, and motion path.
- [x] Persist complete placement histories for every generated output.
- [x] Version the output-sidecar schema.
- [x] Record enough input and transformation information to replay a video process and inspect how an image was constituted.
- [ ] Keep still, video, interactive, and real-time rendering paths conceptually aligned.
- [x] Ensure each artwork may define its own visual grammar while sharing the underlying architecture.

## 2. Todos somos familiares

- [x] Define the precise artistic relation between the disappeared person and contemporary source persons.
- [x] Preserve target recognisability without presenting the result as restoration.
- [x] Add target-side salience controls, beginning with eyes, mouth, silhouette, and configurable regions.
- [ ] Evaluate salience-weighted matching against uniform matching.
- [ ] Add source-side controls for fragment extent, contiguity, adjacency, repeated contribution, and reveal duration.
- [ ] Prevent accidental reconstitution of a contemporary source face from adjacent or repeated fragments.
- [x] Review whether the full reviewed face-region reveal remains artistically necessary in every manifestation.
- [ ] Support transformations that retain useful local visual structure while reducing source-person recognisability.
- [ ] Create internal identifiability and accidental-reconstruction tests.
- [ ] Establish a public-release source policy grounded in the artwork, legal review, and final-output review.
- [x] Keep all public claims narrower than the evidence; do not claim anonymity without an appropriate study.
- [ ] Produce a complete exhibition-quality video loop from reviewed or authorised material.

## 3. Están en todas partes

- [ ] Define source fields that express Uruguay as material, visual, institutional, and territorial present.
- [x] Support self-captured, reviewed public, commissioned, collaborative, and institutional corpora.
- [ ] Preserve place and material legibility while allowing the disappeared person to become recognisable.
- [ ] Develop distinct treatments for streets, walls, buildings, landscapes, infrastructures, objects, and ordinary surfaces.
- [x] Evaluate source concentration and spatial clustering in realised outputs.
- [x] Test grid, irregular, overlap, and feature-aware visual grammars.
- [ ] Produce a complete exhibition-quality video loop.
- [x] Prepare the mode for durable online presentation and later corpus expansion.

## 4. Seguimos buscando

- [x] Preserve the strict rule that no fragment may be used before it is encountered.
- [x] Persist the temporal availability history of every fragment used.
- [x] Make the relation between route, search, found material, and portrait assembly perceptible.
- [x] Support partial and incomplete searches without forcing a completed portrait.
- [x] Limit each traversal frame to one structural contribution, with optional later refinement.
- [ ] Support multiple traversal sources, including open street-level imagery, self-captured footage, commissioned footage, and future live input.
- [x] Make route changes produce traceably different source histories and outputs.
- [x] Support the face becoming recognisable and then dissolving or returning to search.
- [x] Develop alternate, overlay, split, and future spatial compositions as artistic choices rather than interface options alone.
- [ ] Explore live and real-time traversal modes after the offline video process is stable.
- [ ] Produce a complete exhibition-quality loop and an installation-ready version.

## 5. Video, interaction, and real-time forms

- [x] Treat generated videos as primary artworks, not software demonstrations.
- [ ] Make source appearance, selection, fragmentation, movement, assembly, recognition, instability, and dissolution available as compositional material.
- [x] Remove interface-like or explanatory elements from exhibition outputs unless they are artistically necessary.
- [ ] Develop sound as a restrained temporal layer without sentimentality or simulated testimony.
- [ ] Support deterministic editions and variable/live manifestations.
- [x] Share the monochrome search → reconstruction → details → text video form, with artist timing controls.
- [x] Define how names, dates, and minimal public information appear in each mode.
- [x] Build web presentation around the memorial rather than around a technical dashboard.
- [ ] Support multi-channel installation synchronisation.
- [ ] Document display requirements, orientation, duration, codec, looping, and fallback behaviour.

## 6. Accountability and source stewardship

- [x] Preserve source and target provenance appropriate to artistic, curatorial, historical, and ethical review.
- [x] Record exact source material used by each output where this supports replay, revision, or exclusion.
- [x] Record reviewed source regions and the transformations applied to them.
- [x] Add input-integrity checks where altered inputs would compromise replay or curatorial accountability.
- [x] Support exclusion and regeneration where a source should no longer participate.
- [x] Do not construct a general-purpose compliance ontology unless the artwork actually needs it.
- [x] Keep technical review, legal clearance, consent, curatorial approval, and public-display decisions conceptually distinct where relevant.
- [ ] Establish removal and contact procedures before public release.
- [ ] Continue consultation with relevant people, organisations, institutions, and specialists without presenting the artwork as an official archive.

## 7. Evaluation derived from the artwork

- [x] Measure realised source participation rather than database size alone.
- [x] Measure maximum source share, concentration, adjacency, and clustering.
- [x] Distinguish manifest rows, underlying assets, contributors, and collections only where those distinctions matter to the artwork or interpretation.
- [ ] Evaluate whole-image and salient-feature recognisability.
- [ ] Evaluate source-person recognisability under different fragment and video policies.
- [x] Verify temporal causality in traversal outputs.
- [ ] Compare visual grammars without treating a generic fidelity metric as the sole criterion.
- [ ] Use human studies only when the question, ethics, and sample design are defensible.
- [x] Keep quantitative findings separate from claims about memorial legitimacy, historical adequacy, or artistic success.

## 8. Software quality and durability

- [x] Maintain localhost-first development while preparing a separate, deliberately designed public deployment architecture.
- [ ] Apply project-root path safety consistently to all API filesystem parameters.
- [x] Reject unsafe private, loopback, link-local, reserved, and metadata-service network targets in crawler and downloader requests.
- [x] Recheck network destinations after redirects.
- [x] Expand CI to include Python compilation, the complete Python test suite, frontend tests, frontend production build, launcher syntax, benchmark verification, and whitespace checks.
- [x] Pin or lock production dependencies sufficiently for repeatable builds.
- [ ] Add schema migration tests for durable person, manifest, traversal, and sidecar data.
- [ ] Add complete output-generation smoke tests, including video where the environment permits.
- [x] Keep `README.md`, `STATUS.md`, and design documentation aligned with the actual implementation.
- [x] Remove stale terminology such as the obsolete 240-tile contribution-cap description.

## 9. URUCON paper derived from the work

- [x] Reframe the paper around computational re-enactment in a digital memorial.
- [x] Present the triptych as three political propositions translated into three computational operations.
- [x] Describe source-participation limits, recognisability, temporal causality, and visible process as consequences of the artwork.
- [x] Use fragment-based image synthesis rather than treating the project as fundamentally a photomosaic.
- [x] Present a system/design case study rather than claim a novel descriptor or generic optimisation method.
- [x] Select only implemented or immediately verifiable features for the submitted paper.
- [x] Distinguish current implementation, planned artwork development, and speculative extensions.
- [x] Construct an evaluation that supports the artwork-derived research questions.
- [x] Correct the current proxy-corpus description and rerun affected results where retained.
- [x] Review repetition-constrained mosaics, multimedia provenance, creative computation, digital memorials, and temporally causal generative systems.
- [x] Place the manuscript in the official IEEE template early and maintain the five-page limit throughout revision.
- [x] Freeze an exact tested project revision and paper artifact before submission.
- [x] Conduct another adversarial technical, conceptual, ethical, bibliographic, and page-level audit before submission.

## 10. Current execution order

The former immediate implementation sequence is complete except for the unchecked artistic-development items above. Current work must remain evidence-led and artwork-led:

1. Curatorially select one target whose historical identification and portrait rights are explicitly reviewed for article evidence.
2. Render one sidecar-bound **Están en todas partes** output and one approved **Seguimos buscando** traversal from the canonical runtime.
3. Complete full-duration, historical, rights, contextual and output review; record the release decision and reviewer without treating clearance as organisational endorsement.
4. Derive manuscript figures and supplementary video only from those exact hash-bound outputs.
5. Continue the unchecked exhibition, source-policy, removal-procedure and artistic-development work on its own merits; do not add generative, recognition or aesthetic systems merely to supply paper claims.

## Completion criterion

The roadmap is complete when the triptych functions as a coherent computational memorial across exhibition-quality video and durable online forms; its source and transformation processes are sufficiently accountable for responsible presentation and revision; the software supports future artistic iterations; and the URUCON paper accurately communicates a non-trivial computing contribution that emerged from the work rather than dictating it.
