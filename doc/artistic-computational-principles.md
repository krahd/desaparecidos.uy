# Artistic and computational principles

## Status

This document is a durable design constraint for `desaparecidos.uy`. It governs artistic, technical, research, and publication decisions.

## Primary hierarchy

The project must preserve this order:

1. the computational memorial and its political commitments;
2. the artistic operations through which those commitments become perceptible;
3. the computational system required to realise those operations;
4. the technical knowledge discovered while building the system;
5. papers, submissions, documentation, and other accounts derived from the work.

The artwork must never acquire arbitrary requirements merely to satisfy a paper. A paper may formalise, analyse, evaluate, and communicate the computational knowledge that emerges from the artwork. It must not become the hidden specification of the artwork.

`desaparecidos.uy` is simultaneously:

- a computational memorial;
- a sociopolitical commentary and political statement;
- a project of public visibility and continuing memory;
- an artwork and family of artworks;
- a computational image and video system;
- a web project capable of supporting multiple iterations;
- a possible interactive, real-time, installation, and generated-video work;
- a research process from which relevant academic writing may emerge.

The generated videos are not demonstrations of an underlying tool. They are primary manifestations of the memorial.

## The triptych as three computational re-enactments

### Todos somos familiares

**Political proposition:** the disappeared cannot remain the concern of biological relatives alone; disappearance reorganises and implicates the whole social body.

**Artistic operation:** the documented portrait of a disappeared person emerges from fragments of contemporary people.

**Computational operation:** contemporary images of people become dispersed visual material without identity matching, demographic inference, naming, or representation of source persons as subjects of the work.

The disappeared person should remain recognisable. Contemporary source persons should not necessarily remain recognisable. This target/source asymmetry is an artistic and technical requirement, not a generic privacy feature.

Possible techniques include:

- target-side salience or landmark weighting, particularly around the eyes, mouth, silhouette, and other features necessary for memorial recognition;
- source-side limits on fragment extent, contiguity, adjacency, duration, and repeated contribution;
- final-output review for accidental reconstruction or prolonged exposure of source faces;
- transformations that preserve useful local visual structure without reconstructing a living source person;
- visible fragmentation and incompletion rather than seamless restoration.

### Están en todas partes

**Political proposition:** disappearance persists throughout the material, visual, institutional, and territorial present of Uruguay.

**Artistic operation:** portraits emerge from the country’s places, things, surfaces, buildings, streets, landscapes, infrastructures, and publicly circulating images.

**Computational operation:** images of contemporary Uruguay are decomposed and recomposed so that place becomes the material of memorial appearance rather than a background behind it.

The system should support different territorial and material source fields, including self-captured imagery, reviewed public imagery, traversals, institutional sources, and future commissioned or collaborative corpora.

### Seguimos buscando

**Political proposition:** the search remains unfinished, plural, situated, and active.

**Artistic operation:** traversal and searching become the temporal structure of the work.

**Computational operation:** the available visual vocabulary changes through time. A portrait may use only material that has already been encountered by the traversal. Different routes and temporal histories must be able to produce different partial appearances.

The process should preserve temporal causality:

- no fragment can appear before it is encountered;
- the found set grows through the traversal;
- partial searches may produce partial portraits;
- the image may become recognisable and then dissolve or return to searching;
- apparent completion must not imply political closure.

## Shared computational architecture

The system should evolve from a fixed photomosaic implementation into a general fragment-based image and video architecture.

A fragment placement may include:

- source and target identifiers;
- source coordinates or mask;
- target position;
- scale;
- rotation;
- opacity;
- z-order;
- temporal entrance and exit;
- source-acquisition time;
- target salience or perceptual weight;
- review and provenance references.

A grid is one possible rendering strategy, not the ontology of the work. The system should support:

- regular grids;
- irregular non-overlapping layouts;
- overlaps and layering;
- variable fragment sizes;
- masks and shaped fragments;
- visible gaps and incompletion;
- fragments that travel from source material into a portrait;
- live reorganisation and real-time rendering;
- different visual grammars for each part of the triptych.

Persistent placement histories are artistically useful because they support process-video replay, interactive inspection, overlapping and moving fragments, future regeneration, and the visibility of computational operations that would otherwise remain hidden.

## Artistic constraints with computational consequences

The following requirements emerge from the memorial:

- **collectivity:** a large database is insufficient if the realised image is dominated by a few convenient sources;
- **recognisability without restoration:** the disappeared person must become perceptible without presenting computation as recovery or repair;
- **source-person non-representation:** contemporary people may constitute the image materially without becoming represented subjects;
- **temporal causality:** search-based assembly may use only what has been found;
- **visible process:** source acquisition, selection, movement, assembly, instability, and dissolution may be part of the artwork;
- **incompletion:** outputs must be able to remain partial, unstable, multiple, and revisable;
- **accountability:** the project should know enough about its sources and transformations to support artistic, curatorial, ethical, and technical review;
- **iteration:** the architecture must support new sources, visual grammars, modes of display, and future versions without reducing the triptych to the current prototype.

Provenance, contribution limits, placement histories, review procedures, and source exclusion should be developed where they strengthen these requirements. They must not become a general-purpose compliance ontology imposed by an academic argument.

## Evaluation principles

Evaluation must examine properties that matter to the artwork rather than substitute generic optimisation objectives for artistic judgement.

Relevant evaluations include:

1. **collective participation**
   - number and distribution of realised contributors;
   - maximum source share and concentration;
   - spatial adjacency or clustering from one source;
   - whether apparent plurality is produced by genuinely distinct material;

2. **memorial recognisability**
   - whole-image and salient-feature similarity;
   - comparison of uniform and feature-aware synthesis;
   - limited human recognition studies where appropriate;
   - explicit separation between recognisability and restoration;

3. **source-person recognisability**
   - effects of fragment size, adjacency, repetition, source reveal, and display duration;
   - review of accidental reconstruction or contextual exposure;
   - no unsupported claim of anonymity;

4. **temporal causality**
   - every placed fragment was available when used;
   - route changes produce meaningfully different source histories and outputs;
   - incomplete searches remain computationally and visually incomplete;

5. **visual grammar**
   - grid, irregular, overlapping, layered, and feature-weighted strategies;
   - the relation between visual legibility, fragment visibility, and political meaning.

Quantitative evidence may support the analysis, but it cannot determine memorial legitimacy, artistic success, or historical adequacy.

## Relationship to academic papers

Papers derived from the project should begin from the artwork’s propositions and identify the computational problems discovered in making them operational.

The preferred research framing is computational re-enactment: the three propositions are not illustrated by finished images but enacted through collective synthesis, territorial recomposition, and continuing search.

A defensible technical contribution may include:

- a computational model of memorial re-enactment;
- a shared fragment-based architecture for three conceptually distinct processes;
- collective synthesis under recognisability and source-participation constraints;
- target/source asymmetry between memorial recognition and source-person non-representation;
- temporally causal traversal-based assembly;
- analysis of tensions between resemblance, plurality, anonymity, visible process, and incompletion.

Papers must distinguish implemented behaviour, planned artistic development, and speculative future work. They must never describe a paper-driven requirement as though it originated in the artwork.

## Decision test

Before adding a substantial requirement, ask:

1. Which memorial proposition or artistic operation requires it?
2. How will it become perceptible in the artwork or sustain its future iterations?
3. Is it necessary for the project, or only convenient for a paper?
4. Can the paper be revised instead of distorting the artwork?

If the only strong justification is publication, do not impose the requirement on the project.