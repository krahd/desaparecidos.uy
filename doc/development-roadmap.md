# desaparecidos.uy development roadmap

## Goal

Develop `desaparecidos.uy` into a serious, durable, extensible computational memorial whose three works are artistically complete, technically credible, suitable for public presentation, and capable of supporting future web, video, installation, interactive, and real-time iterations.

The roadmap is governed by `doc/artistic-computational-principles.md`. The artwork is primary. Technical and publication work must derive from it.

This is a completion goal, not a list of optional ideas. Items may be revised when artistic evidence changes, but they should not be silently abandoned.

## 1. Shared artistic and computational architecture

- [ ] Replace the implicit fixed-grid ontology with a general fragment-placement model.
- [ ] Preserve the existing grid renderer as one visual strategy.
- [ ] Add irregular non-overlapping placement.
- [ ] Add overlapping and layered placement with opacity and z-order.
- [ ] Support variable fragment sizes and masks.
- [ ] Support fragment scale, rotation, entrance time, exit time, and motion path.
- [ ] Persist complete placement histories for every generated output.
- [ ] Version the output-sidecar schema.
- [ ] Record enough input and transformation information to replay a video process and inspect how an image was constituted.
- [ ] Keep still, video, interactive, and real-time rendering paths conceptually aligned.
- [ ] Ensure each artwork may define its own visual grammar while sharing the underlying architecture.

## 2. Todos somos familiares

- [ ] Define the precise artistic relation between the disappeared person and contemporary source persons.
- [ ] Preserve target recognisability without presenting the result as restoration.
- [ ] Add target-side salience controls, beginning with eyes, mouth, silhouette, and configurable regions.
- [ ] Evaluate salience-weighted matching against uniform matching.
- [ ] Add source-side controls for fragment extent, contiguity, adjacency, repeated contribution, and reveal duration.
- [ ] Prevent accidental reconstitution of a contemporary source face from adjacent or repeated fragments.
- [ ] Review whether the full reviewed face-region reveal remains artistically necessary in every manifestation.
- [ ] Support transformations that retain useful local visual structure while reducing source-person recognisability.
- [ ] Create internal identifiability and accidental-reconstruction tests.
- [ ] Establish a public-release source policy grounded in the artwork, legal review, and final-output review.
- [ ] Keep all public claims narrower than the evidence; do not claim anonymity without an appropriate study.
- [ ] Produce a complete exhibition-quality video loop from reviewed or authorised material.

## 3. Están en todas partes

- [ ] Define source fields that express Uruguay as material, visual, institutional, and territorial present.
- [ ] Support self-captured, reviewed public, commissioned, collaborative, and institutional corpora.
- [ ] Preserve place and material legibility while allowing the disappeared person to become recognisable.
- [ ] Develop distinct treatments for streets, walls, buildings, landscapes, infrastructures, objects, and ordinary surfaces.
- [ ] Evaluate source concentration and spatial clustering in realised outputs.
- [ ] Test grid, irregular, overlap, and feature-aware visual grammars.
- [ ] Produce a complete exhibition-quality video loop.
- [ ] Prepare the mode for durable online presentation and later corpus expansion.

## 4. Seguimos buscando

- [ ] Preserve the strict rule that no fragment may be used before it is encountered.
- [ ] Persist the temporal availability history of every fragment used.
- [ ] Make the relation between route, search, found material, and portrait assembly perceptible.
- [ ] Support partial and incomplete searches without forcing a completed portrait.
- [ ] Support multiple traversal sources, including open street-level imagery, self-captured footage, commissioned footage, and future live input.
- [ ] Make route changes produce traceably different source histories and outputs.
- [ ] Support the face becoming recognisable and then dissolving or returning to search.
- [ ] Develop alternate, overlay, split, and future spatial compositions as artistic choices rather than interface options alone.
- [ ] Explore live and real-time traversal modes after the offline video process is stable.
- [ ] Produce a complete exhibition-quality loop and an installation-ready version.

## 5. Video, interaction, and real-time forms

- [ ] Treat generated videos as primary artworks, not software demonstrations.
- [ ] Make source appearance, selection, fragmentation, movement, assembly, recognition, instability, and dissolution available as compositional material.
- [ ] Remove interface-like or explanatory elements from exhibition outputs unless they are artistically necessary.
- [ ] Develop sound as a restrained temporal layer without sentimentality or simulated testimony.
- [ ] Support deterministic editions and variable/live manifestations.
- [ ] Define how names, dates, and minimal public information appear in each mode.
- [ ] Build web presentation around the memorial rather than around a technical dashboard.
- [ ] Support multi-channel installation synchronisation.
- [ ] Document display requirements, orientation, duration, codec, looping, and fallback behaviour.

## 6. Accountability and source stewardship

- [ ] Preserve source and target provenance appropriate to artistic, curatorial, historical, and ethical review.
- [ ] Record exact source material used by each output where this supports replay, revision, or exclusion.
- [ ] Record reviewed source regions and the transformations applied to them.
- [ ] Add input-integrity checks where altered inputs would compromise replay or curatorial accountability.
- [ ] Support exclusion and regeneration where a source should no longer participate.
- [ ] Do not construct a general-purpose compliance ontology unless the artwork actually needs it.
- [ ] Keep technical review, legal clearance, consent, curatorial approval, and public-display decisions conceptually distinct where relevant.
- [ ] Establish removal and contact procedures before public release.
- [ ] Continue consultation with relevant people, organisations, institutions, and specialists without presenting the artwork as an official archive.

## 7. Evaluation derived from the artwork

- [ ] Measure realised source participation rather than database size alone.
- [ ] Measure maximum source share, concentration, adjacency, and clustering.
- [ ] Distinguish manifest rows, underlying assets, contributors, and collections only where those distinctions matter to the artwork or interpretation.
- [ ] Evaluate whole-image and salient-feature recognisability.
- [ ] Evaluate source-person recognisability under different fragment and video policies.
- [ ] Verify temporal causality in traversal outputs.
- [ ] Compare visual grammars without treating a generic fidelity metric as the sole criterion.
- [ ] Use human studies only when the question, ethics, and sample design are defensible.
- [ ] Keep quantitative findings separate from claims about memorial legitimacy, historical adequacy, or artistic success.

## 8. Software quality and durability

- [ ] Maintain localhost-first development while preparing a separate, deliberately designed public deployment architecture.
- [ ] Apply project-root path safety consistently to all API filesystem parameters.
- [ ] Reject unsafe private, loopback, link-local, reserved, and metadata-service network targets in crawler and downloader requests.
- [ ] Recheck network destinations after redirects.
- [ ] Expand CI to include Python compilation, the complete Python test suite, frontend tests, frontend production build, launcher syntax, benchmark verification, and whitespace checks.
- [ ] Pin or lock production dependencies sufficiently for repeatable builds.
- [ ] Add schema migration tests for durable person, manifest, traversal, and sidecar data.
- [ ] Add complete output-generation smoke tests, including video where the environment permits.
- [ ] Keep `README.md`, `STATUS.md`, and design documentation aligned with the actual implementation.
- [ ] Remove stale terminology such as the obsolete 240-tile contribution-cap description.

## 9. URUCON paper derived from the work

- [ ] Reframe the paper around computational re-enactment in a digital memorial.
- [ ] Present the triptych as three political propositions translated into three computational operations.
- [ ] Describe source-participation limits, recognisability, temporal causality, and visible process as consequences of the artwork.
- [ ] Use fragment-based image synthesis rather than treating the project as fundamentally a photomosaic.
- [ ] Present a system/design case study rather than claim a novel descriptor or generic optimisation method.
- [ ] Select only implemented or immediately verifiable features for the submitted paper.
- [ ] Distinguish current implementation, planned artwork development, and speculative extensions.
- [ ] Construct an evaluation that supports the artwork-derived research questions.
- [ ] Correct the current proxy-corpus description and rerun affected results where retained.
- [ ] Review repetition-constrained mosaics, multimedia provenance, creative computation, digital memorials, and temporally causal generative systems.
- [ ] Place the manuscript in the official IEEE template early and maintain the five-page limit throughout revision.
- [ ] Freeze an exact tested project revision and paper artifact before submission.
- [ ] Conduct another adversarial technical, conceptual, ethical, bibliographic, and page-level audit before submission.

## 10. Immediate execution order

1. Persist the artwork-first principles and paper direction.
2. Reconcile current documentation with the actual one-tile default source cap and current video behaviour.
3. Introduce versioned persistent placement histories because they support animation, overlap, interaction, and replay.
4. Generalise the placement model without removing the working grid path.
5. Implement the first irregular and overlapping render strategies.
6. Add target salience and source-recognisability controls for **Todos somos familiares**.
7. Strengthen territorial source and composition strategies for **Están en todas partes**.
8. Extend temporal histories and partial-search rendering for **Seguimos buscando**.
9. Expand tests and CI around the changed architecture.
10. Rewrite and evaluate the URUCON paper from the resulting artwork and verified implementation.

## Completion criterion

The roadmap is complete when the triptych functions as a coherent computational memorial across exhibition-quality video and durable online forms; its source and transformation processes are sufficiently accountable for responsible presentation and revision; the software supports future artistic iterations; and the URUCON paper accurately communicates a non-trivial computing contribution that emerged from the work rather than dictating it.