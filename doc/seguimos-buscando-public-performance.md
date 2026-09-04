# Seguimos buscando — public performance and reusable memorial activation

**Status:** fixed artistic direction, derived from `desaparecidos.uy`; participatory/public layer not yet fully implemented.

## Relation to desaparecidos.uy

**Seguimos buscando** is the third work in the `desaparecidos.uy` triptych and is now also the title of its public participatory derivation. The underlying computational proposition remains unchanged: a disappeared person's documented portrait may only be assembled from visual material that has actually been encountered in the traversal, and no fragment may appear before the search reaches it.

The public derivation turns that traversal into a repeatable performance that can be activated by people and groups rather than performed only by the software from pre-existing street-level imagery.

## Proposition

A person or group walks through a place and documents what they encounter: streets, walls, buildings, landscapes, objects, infrastructures and other fragments of the present. The collected material becomes the source field for a documented portrait of a person detained-disappeared in connection with Uruguay. The portrait develops according to the order in which the material was encountered.

The walk is not documentation of the artwork. The walk is the artwork's performance.

A performance is complete when the walk, ordered encounter material, causal assembly and resulting memorial manifestation have taken place. Participants do **not** need to photograph, film or otherwise document themselves performing it.

Participants may optionally document the performance itself. If they choose to do so, and separately consent to publication, that documentation can accompany the activation in the public memorial. It is an optional secondary contribution, not a condition of participation or completion.

The memorial therefore grows through acts of searching and the memorial manifestations people choose to contribute. Optional documentation can add another layer to that history without becoming obligatory.

## Performance protocol

A complete activation should support the following sequence:

1. **Begin a search.** An activation is associated with a reviewed disappeared-person record and documented public portrait from the canonical corpus. The eventual selection policy must avoid turning people into a popularity-ranked catalogue; balanced or rotating assignment should be evaluated before public release.
2. **Walk and look.** The participant or group moves through a real place. GPS recording is optional rather than mandatory; the ordered image sequence is sufficient to establish traversal chronology.
3. **Document encounters.** Participants photograph or record place-based material encountered during the walk. Public contribution should avoid identifiable living people unless explicit consent and an appropriate rights basis exist.
4. **Assemble causally.** The source material is reviewed and fed to the `Seguimos buscando` runtime. A fragment cannot be used before the source frame or image has been encountered in the recorded sequence.
5. **Produce a memorial manifestation.** The activation generates a portrait and/or audiovisual work together with provenance sufficient to reconstruct which encounter contributed which fragments and when. At this point the performance is complete.
6. **Optionally contribute the activation.** If participants choose to do so, the encounter sequence, generated manifestation and appropriate provenance can enter the growing public memorial after explicit consent, rights review and curatorial review. Publication is never automatic.
7. **Optionally document the performance.** Participants may also contribute photographs, video, text or other documentation of themselves or the group carrying out the activation. This is a separate opt-in layer and is not required for the activation to enter the memorial.
8. **Reuse the protocol.** Schools, memory organisations, museums, universities, neighbourhood groups and informal groups should be able to run an activation without Tomas Laurenzo being physically present.

## Activation record

The system should distinguish the core record of an activation from optional documentation of its performance.

A core activation record may contain:

- activation date;
- place or coarse location, when the participants choose to disclose it;
- disappeared-person record and target-image provenance;
- ordered encounter/source sequence;
- generated portrait and/or video;
- source-to-fragment provenance and temporal-causality record;
- attribution preference, including anonymous or collective attribution where appropriate;
- consent, public-display and removal state;
- version of the software and activation protocol used.

Optional performance documentation may be attached separately when participants choose to contribute it. It may include photographs, video, text, sound or other records of carrying out the search, with its own attribution, licence, consent and removal state.

The memorial should never infer that participation, activation or submission equals permission for publication or every later use.

## Growing memorial

The public site should accumulate reviewed activation records that participants or groups choose to contribute over time. A visitor can therefore encounter both the disappeared and the continuing history of searches carried out in the present, even when no participant-facing documentation of those performances exists.

A later optional extension may allow separately opted-in documentation from previous activations to become source material for future searches. If implemented, this recursion must remain explicit: a later portrait could be assembled partly from images generated by earlier acts of searching. This is conceptually attractive but is **not** required for the first public version and must not be implied until implemented and rights-cleared.

## Reuse and publicness

The project should separate rights layers rather than treating "open" as one blanket permission:

- **software:** publish under an explicit open-source licence;
- **activation protocol and facilitator documentation:** publish under an explicit reusable Creative Commons licence;
- **canonical disappeared-person records and source portraits:** retain their existing provenance and rights conditions; do not relicense them merely because the code is open;
- **participant encounter material:** publish only under the contribution terms chosen for that activation;
- **optional performance documentation:** publish only under the consent/licence chosen for that contribution;
- **generated memorial outputs:** state their reuse terms explicitly and preserve the rights/provenance of their inputs.

The goal is that the method can be reused publicly without turning sensitive historical or participant material into an unrestricted data commons.

## Naming note

Tomas Laurenzo acquired the `desaparecidos.uy` domain and the current project takes its name from that domain. Do **not** claim that `desaparecidos.uy` was used by the 2020 virtual Marcha del Silencio without primary evidence.

A primary 2020 Uruguayan human-rights report identifies `marchadelsilencio.uy` as the site that aggregated social-media posts carrying the Marcha hashtags and `vivosennuestramemoria.com` as the site that distributed the 197 portraits for virtual participation. The earlier claim connecting `desaparecidos.uy` to that mobilisation was unsupported and has been withdrawn.

## Current urgency

The search is not a closed historical matter. In May 2026 the Institución Nacional de Derechos Humanos y Defensoría del Pueblo reported work on 243 investigations concerning allegations of enforced disappearance, including 162 active cases and 81 allegations still under analysis. The same month, the INDDHH reported continuing forensic investigation and excavation at Batallón 14. The 2026 Marcha del Silencio read 205 names.

These facts may ground the work's current urgency, but the artwork must not claim institutional authority, investigative status or endorsement from memory organisations merely because it addresses an active public search.

## Current implementation boundary

The existing `Seguimos buscando` traversal/runtime already provides:

- route authoring and recorded traversal sequences;
- reviewed traversal frames;
- incremental portrait assembly;
- strict temporal causality: future source frames cannot contribute early;
- generated still/video manifestations and provenance sidecars.

The public-performance derivation still requires work before it can be represented as a deployed public participatory system. In particular:

- direct ingestion of self-captured participant sequences needs a supported workflow rather than relying only on current Mapillary acquisition;
- activation-record storage/publication needs to be implemented;
- contribution, withdrawal/removal, attribution and rights flows need to be made explicit;
- an activation guide needs to be published;
- at least one complete human-performed pilot should be run and reviewed.

Performance documentation is not an implementation gate. A participant must be able to complete and, if desired, contribute an activation without photographing or filming themselves.

Until those gates are completed, describe the derived public piece as a **prototype built on an implemented artwork runtime**, not as an already operating public platform.

## ZKM / Arte Útil direction

For the 2026 ZKM / Arte Útil case-study call, submit **Seguimos buscando**, not the entire triptych, while making its derivation from `desaparecidos.uy` explicit.

The strongest Arte Útil relation is the shift from spectator to user/performer: people do not merely see a memorial image. They carry out a situated search, contribute the present-day material from which the image becomes possible, and may add the reviewed activation to a memorial that remains available for later activation and reuse. If they also choose to document the performance itself, that documentation can be added as an optional further layer.
