# Against Restoration: Responsible AI, Disappearance, and Computational Memorial Systems in `desaparecidos.uy`

**Target venue:** AI & SOCIETY, Open Forum paper, special collection "Responsible use of AI in Art Creation and Archival Practice"  
**Status:** working manuscript on branch `paper-ai-society-open-forum-import`  
**Submission note:** anonymise author, repository URL, local repository paths, and self-citations before double-blind submission.

## Abstract

This Open Forum paper presents `desaparecidos.uy`, a developing series of computational memorial artworks addressing detained-disappeared persons connected to Uruguay's civic-military dictatorship and the broader Southern Cone apparatus of repression. The project reassembles public images of disappeared persons from fragments of the country that survived them: people, places, streets, walls, landscapes, and contemporary visual infrastructures. It is conceived as a triptych: **Todos somos familiares**, which uses fragments from publicly available images of contemporary people in Uruguay; **Están en todas partes**, which uses images of places, surfaces, streets, buildings, and landscapes; and **Seguimos buscando**, which turns traversal and search across the country's visual field into the temporal structure of the work.

The paper argues that responsible AI in art and archival practice cannot be reduced to consent, provenance, transparency, or technical safeguards, though all of these remain necessary. In contexts of unresolved state violence, responsible practice also requires a politics of refusal: refusal of forensic authority, refusal of resurrection media, refusal of biometric identification, refusal of archival substitution, and refusal of the fantasy that computation can repair what politics destroyed. The project therefore proposes a framework for computational memorial systems based on five principles: archival humility, fragmentary reappearance, non-identification, provenance accountability, and designed incompletion. Rather than presenting AI as a restorative technology, `desaparecidos.uy` treats computation as a means of staging a visual and political condition: disappearance is not an absence sealed in the past, but a structure distributed through the present.

## Keywords

responsible AI; AI art; computational memorials; enforced disappearance; Uruguay; archives; visual culture; memory; biometric refusal; digital memorialisation

## 1. Introduction

The increasing use of artificial intelligence in artistic creation and archival practice has intensified questions that are not only technical or procedural, but historical and political. What may be reactivated? What may be reconstructed? What should remain unresolved? What kinds of absence can be made perceptible without being falsely repaired? These questions become especially urgent when AI systems are used in relation to political violence, forced disappearance, missing persons, traumatic archives, and contested public memory.

This paper presents `desaparecidos.uy`, a developing computational memorial artwork series concerning detained-disappeared persons connected to Uruguay. The project begins from a simple but difficult proposition: the image of each disappeared person is reassembled from fragments of the country that survived them. These fragments may come from images of contemporary Uruguayans, from streets and surfaces, from landscapes and public buildings, or from traversal across the country's present visual field. The work does not claim to restore the disappeared. It does not claim to reconstruct unknown facts, recover lost bodies, generate testimony, or produce forensic evidence. Its aim is more limited and, for that reason, more precise: to construct a visual condition in which the unresolved persistence of disappearance becomes newly perceptible.

The paper is intended for the AI & SOCIETY Open Forum format rather than as a completed empirical article. This is appropriate because the call explicitly welcomes research-in-progress, ideas papers, case studies, working papers, and contributions aimed at a broad audience of academics, designers, practitioners, and general readers. The topical collection calls for work on responsible AI across the full lifecycle of artworks, from creation to preservation and archiving, and asks for theoretical and methodological frameworks that can structure responsible development in art and heritage contexts. This paper answers that call by treating a developing artwork as both a case study and a framework-building site.

The project belongs to a long artistic, political, and memorial lineage in Latin America. This includes the visual activism of the Mothers of Plaza de Mayo and the *Siluetazo*; photographic works such as Marcelo Brodsky's *Buena Memoria* and Gustavo Germano's *Ausencias*; urban interventions such as Fernando Traverso's bicycle stencils in Rosario; memorial architectures such as the Parque de la Memoria in Buenos Aires; and Uruguayan precedents such as Juan Ángel Urruzola's *Álbum de memoria*. `desaparecidos.uy` does not claim novelty at the level of making absence visible through images. Rather, it asks what a computational memorial system may responsibly add to this lineage when AI, computer vision, and large-scale visual processing make restoration, simulation, and biometric capture newly available.

This paper is also distinct from the author's earlier work on AI-supported collective memory and testimony capture. That earlier project concerned conversational interfaces and the capture of collective memories through human dialogue. The present paper concerns computational memorial imagery, visual source fields, fragment assembly, and the responsibilities of AI-assisted artistic and archival practice. The two projects share a political-historical concern with Uruguay's disappeared, but they ask different questions and use different methods. For double-blind review, this distinction should be kept while self-citations are anonymised.

The paper is written at the stage of a developing artwork and therefore does not present a finished public-reception study or completed installation analysis. It does, however, refer to an implemented Stage 1 prototype: **Están en todas partes**, the place-fragment work. The current codebase includes manifest-driven ingestion, target preprocessing, review gates, bounded crawling, duplicate detection, local OpenCV/NumPy image gating, deterministic fragment matching, still outputs, optional process videos, and JSON sidecars. The paper therefore treats the work as a functioning prototype and uses it to articulate a framework for responsible AI art in relation to archives, political violence, and memorial practice.

## 2. Historical and political horizon

Uruguay's civic-military dictatorship, from 1973 to 1985, belongs to a wider Southern Cone history of state terror, clandestine detention, torture, exile, surveillance, censorship, and enforced disappearance. The disappeared connected to Uruguay include people detained in Uruguay, Argentina, and elsewhere through transnational repressive networks. Their public memory has been sustained by relatives' organisations, human-rights groups, legal struggles, forensic work, archives, sites of memory, and public acts of insistence.

The term "disappeared" is not a metaphor. It names a political technology. A disappeared person is not simply missing. Disappearance is produced by institutional and state violence, followed by denial, concealment, fragmentation of evidence, and the prolonged withholding of truth. The disappeared person is removed not only from social life but from the systems through which society verifies presence and death: legal records, bodies, graves, testimony, institutional acknowledgment, and public narration.

In Uruguay, relatives' organisations and memory institutions have built a long public history of resistance to this erasure. Madres y Familiares de Uruguayos Detenidos Desaparecidos maintains public materials, lists, biographies, posters, and memory resources. The Secretaría de Derechos Humanos para el Pasado Reciente provides public victim files and lists. Sitios de Memoria Uruguay maps and documents places connected to repression, detention, findings of disappeared persons, and operations of state terrorism. These resources are not simply data sources. They are part of a decades-long political and ethical infrastructure of memory, truth, and justice.

`desaparecidos.uy` does not attempt to create a parallel authority over this infrastructure. It does not replace official archives, family testimonies, forensic investigation, legal process, or the historical work of human-rights organisations. The project depends on such sources for provenance, naming, and minimal public historical information, but its own contribution is artistic rather than archival or judicial. It asks how computational art can make absence active without claiming to solve it.

The project therefore treats Uruguay itself as the image field of the work. The country is not a background, landscape, or national symbol. It becomes the material support through which the disappeared reappear. The central claim is not that the disappeared can be restored, but that the present cannot be understood without them.

## 3. The triptych: people, places, search

`desaparecidos.uy` is conceived as a triptych of related computational memorial systems.

The first work, **Todos somos familiares**, reconstructs public images of disappeared persons from fragments extracted from publicly available images of contemporary Uruguayans. Its title is deliberately direct. It does not claim that all Uruguayans have the same relation to disappearance, nor does it flatten the specific historical and political labour of relatives' organisations. Rather, it states an ethical demand: the disappeared cannot remain the responsibility of biological families alone. Disappearance reorganises the social body and produces a collective debt, even when pain and responsibility are not equally distributed.

In this work, contemporary faces become visual material from which disappeared faces partially reappear. The system does not identify the living persons whose images contribute fragments. It does not classify them, name them, infer attributes from them, or represent them as individuals. Their images enter only as dispersed visual matter: colour, tone, texture, shadow, contour, surface, and partial form. The work is therefore not a biometric database but a political condensation of visual responsibility.

The second work, **Están en todas partes**, reconstructs public images of disappeared persons from fragments extracted from images of Uruguay's places: walls, streets, buildings, pavements, rural roads, institutional facades, river edges, landscapes, ruins, monuments, neighbourhoods, and ordinary surfaces. If **Todos somos familiares** begins from the living social body, **Están en todas partes** begins from the material body of the country. Its claim is not that every place is directly connected to every disappearance. Its claim is structural: disappearance reshapes the political meaning of place. It marks the country as a whole, not only the specific sites of detention, torture, burial, testimony, or commemoration.

This second work is the first prototype because it preserves the conceptual core of the project while lowering immediate privacy risks. Place-based imagery allows the system to develop a visual language of texture, erosion, architecture, geography, institutional austerity, urban decay, rural dispersion, and everyday surfaces. The disappeared appear from the country rather than being placed over it.

The third work, **Seguimos buscando**, transforms the act of search into the temporal structure of the work. It imagines the country as an image field to be scanned, crossed, searched, and revisited. The work may use street-level imagery, self-captured footage, archival routes, crowdsourced material, or other ethically reviewed forms of visual traversal. Its central gesture is not the static composition of a portrait but the process by which a face emerges from movement through the country.

Together, the triptych moves across three forms of implication. The living social body participates in the image. The country's surfaces participate in the image. Search itself becomes the work's temporal form.

## 4. Artistic and memorial lineage

The project should be situated within at least four overlapping lineages: Latin American visual activism around the disappeared, photographic works that make absence visible, public memorial architectures and counter-monumental forms, and the author's earlier practice in political new media art.

The first lineage is the public visual activism of the Southern Cone. The *Siluetazo*, first carried out in Buenos Aires in 1983 in connection with human-rights organisations including the Mothers of Plaza de Mayo, produced life-size paper silhouettes of absent bodies and installed them in public space. Its force lay in the relation between repetition, anonymity, bodily scale, and urban inscription. The absent body was not restored; it was marked as absent. This distinction is crucial for `desaparecidos.uy`: making absence visible is not the same as completing it.

A second lineage is photographic work that reactivates personal and collective memory through damaged, annotated, or re-staged images. Marcelo Brodsky's *Buena Memoria* works from a school class photograph marked by dictatorship, exile, and disappearance. Gustavo Germano's *Ausencias* restages family photographs decades later, preserving the position of the absent person as a visible void. These works do not produce substitute presences. They construct forms in which missing people reorganise the present image.

A third lineage is urban and public memorial practice. Fernando Traverso's bicycle stencils in Rosario transformed the traces of abandoned bicycles into a distributed memorial for the disappeared. The Parque de la Memoria in Buenos Aires combines names, a river-facing site, public sculpture, and a wound-like architectural form. Claudia Fontes's *Reconstrucción del retrato de Pablo Míguez*, installed in the Parque de la Memoria, is especially important as a sculptural attempt to reconstruct the image of a disappeared adolescent in relation to the Río de la Plata. These works matter because they place disappearance in the public, material, and spatial field, rather than only in the archive.

A fourth, more local lineage is Juan Ángel Urruzola's *Álbum de memoria*. In that work, small identification-style photographs of detained-disappeared persons were assembled into the enlarged face of another disappeared person. Tatiana Oroño described the work as a mosaic of tiny faces in which the enlarged image appears through many others. This precedent is not an obstacle but a necessary point of departure. Urruzola's work forms the face of one disappeared person from images of other disappeared persons. `desaparecidos.uy` forms the public images of the disappeared from fragments of contemporary Uruguay: living faces, material surfaces, streets, walls, landscapes, and public visual infrastructures.

The difference is therefore not merely technical. In *Álbum de memoria*, the disappeared visually sustain one another. In `desaparecidos.uy`, the disappeared emerge from the country that remains. The work shifts from memorial co-presence among the disappeared to an implicating relation between disappearance and the present social and material body of Uruguay.

Finally, the project continues a broader research trajectory in political new media art, data, interaction, and mediated political visibility. Earlier works and writings include political new-media artworks, media appropriation, data visualisation as political performance, AI ethics through everyday objects, and prior research on collective memories of Uruguay's disappeared. For double-blind submission, these should be cited as anonymised prior work where structurally necessary, and fully restored after review.

## 5. Against restoration

The project requires precise negative definitions. These exclusions are not defensive additions to the work. They are part of its method.

First, the works are not forensic reconstructions. They do not claim to improve the historical image of a disappeared person, recover unknown facial details, or produce evidentiary images. Their outputs are not images for identification, prosecution, or documentation of unknown facts.

Second, the works are not documentary archives. They may refer to archives and public records, but they do not replace them. The authority of the historical record remains with families, human-rights organisations, historians, judicial processes, official investigative bodies, and existing archives.

Third, the works are not biometric systems. They do not identify living persons, classify faces, infer demographic or behavioural categories, or create a searchable database of people. In the face-fragment component, the use of publicly circulating images of contemporary people is governed by a distinction between visual fragments and person representation.

Fourth, the works are not deepfakes or resurrection media. They do not animate the disappeared as if they were alive. They do not synthesise speech, fabricate testimony, or simulate subjectivity.

Finally, the works are not monuments to technological power. They do not present computation as the force that restores what politics destroyed. At most, computation can produce a visual and political structure through which the unresolved condition of disappearance becomes perceptible.

This refusal of restoration is central to the responsible use of AI in contexts of political violence. AI systems are often valued for their capacity to fill gaps, increase resolution, interpolate missing frames, infer hidden structures, and generate plausible continuities. In this project, those capacities are approached with suspicion. The gaps are not simply technical absences. They are the marks of a political crime. To fill them too smoothly risks transforming violence into a solvable representational problem.

## 6. Stage 1 prototype: `Están en todas partes`

The current implemented prototype is **Están en todas partes**, the place-fragment work. It reconstructs public images of disappeared persons from fragments extracted from curated images of Uruguayan places, surfaces, streets, landscapes, and material environments. This implementation gives the paper a concrete methodological base: it is no longer only a proposal for a future AI artwork, but a working local computational pipeline whose constraints instantiate the paper's argument.

The call for papers explicitly asks contributors to move beyond an exclusive focus on generative AI and to consider the broader range of AI techniques used in art and archiving. This point matters here. The Stage 1 prototype does not depend on a large generative model or on synthetic portrait generation. Its present AI/computational components are narrower and more accountable: local computer-vision gating, deduplication, manifest-driven provenance, deterministic fragment matching, and generation of process videos that expose rather than hide selection and assembly. The project is therefore an AI-and-computation artwork in the broad sense invited by the call, not a demonstration of foundation-model image synthesis.

The prototype uses manifest-driven ingestion. Target manifests describe disappeared persons' public images and provenance. Place manifests describe source images of surfaces, streets, landscapes, buildings, and other material environments. People manifests exist only for internal Stage 2 experimentation and remain separate from the Stage 1 place-source pipeline. Rows must pass review before the generation pipeline can use them. This review gate is important: the artwork treats data acquisition as a curatorial and ethical process rather than as automatic extraction.

Target preparation normalises public portrait images only to the degree necessary for reconstruction. The current local tooling trims white scan borders and caption margins, writes processed portrait copies, and retains original filenames and provenance notes. This preprocessing is not framed as repair or enhancement. It prepares the image as a referential target while preserving the ethical distinction between the historical photograph and the generated output.

Source acquisition is similarly constrained. The current crawler is bounded and explicit: it crawls only user-supplied or preset starting pages, follows links within depth, page, image, and domain limits, respects `robots.txt` by default, and records crawl cache and crawl trail data so traversal can be inspected or replayed. The presets deliberately privilege mundane contemporary Uruguay sources rather than memory-site pages, because the work's logic is to form the disappeared from the ordinary visual field of the country rather than from already memorial material.

The crawler includes duplicate detection and local image gating. It records checksums, uses perceptual duplicate detection to prevent repeated image variants from entering manifests, and applies OpenCV/NumPy-based heuristics to distinguish plausible place-source material from flat graphics, logos, posters, prominent faces, and random-noise-like textures. For people-source crawling, the system requires an actual detected face before writing a pending row, but this is internal-only and does not infer identity, category, demographic traits, or relation to a disappeared person. The distinction between detection as a gate and identification as a prohibited operation is central to the project's privacy framework.

The reconstruction algorithm decomposes approved source images into fragments and matches them to regions of the target portrait. The current implementation uses deterministic, vectorised nearest-fragment matching. It compares target regions with source fragments, supports reuse limits and per-source contribution caps, and records sidecar metadata about source usage and output generation. These contribution caps have both visual and ethical significance. Visually, they prevent one source image from dominating the reconstruction. Ethically, they support the claim that the output is composed from a dispersed visual field rather than from a disguised single-source transformation.

The prototype generates still PNG outputs and optional browser-playable H.264 MP4 process videos. The video form is especially important. Generated videos show a search before selection: local crawl candidates that do not contribute are flashed quickly in crawl order, then a usable source is introduced, sampled fragment regions are highlighted, and those fragments animate into their actual positions in the reconstructed portrait. Page URLs can appear along the bottom during search and assembly frames, and the video finishes with a commemorative outro. This temporal form makes search, selection, and assembly perceptible. The face does not simply appear as a finished computational result; it emerges from a traversal of the country's visual field.

The prototype also uses JSON sidecars for generated outputs. These sidecars are not merely technical logs. They are part of the work's provenance layer. They can document target identity, source usage, parameter settings, generation time, and review state. They support the broader claim that responsible AI art must make its own operations accountable, especially when working with politically and emotionally charged historical material.

Generated outputs, processed target copies, raw downloads, crawl caches, crawl trails, and review manifests are intentionally ignored by git. The curated portrait collection is tracked intentionally as foundational material for the work. This split between tracked foundational material and ignored/generated operational data is another practical expression of archival humility: not everything that can be captured by the system should become part of the public repository.

## 7. Privacy and non-identification

The project's responsible-AI framework begins from the recognition that public availability is not equivalent to unrestricted consent. Images circulating online may be technically accessible but ethically fragile. This is especially true when processing faces, when working across national and institutional jurisdictions, or when images may reveal sensitive contexts.

For the face-fragment component, the working principle is that the work may store face-derived visual fragments but does not identify, classify, or represent the living persons whose publicly available images may have contributed fragments. It treats the web as a dispersed visual field, not as a biometric archive.

This principle has practical consequences. The release pipeline should avoid storing full source faces wherever possible; store fragments rather than complete portraits; limit the size of contiguous fragments; avoid recognisable crops of eyes, mouths, or full facial structures; prevent any single source image from contributing too much to any final portrait; separate source identity from visual fragments; document deletion policies for raw source material; and exclude images from contexts involving minors, health, criminal justice, education, protests, funerals, religious ceremonies, political meetings, shelters, or other sensitive situations unless explicit permission exists.

Uruguayan data-protection rules are relevant here because facial images can be personal data, and biometric processing requires special caution. Uruguay's data-protection authority has stated that biometric data include facial images and fingerprint data, and Resolution No. 30/020 requires a data-protection impact assessment for processing biometric data. The paper therefore avoids declaring the face-fragment component publicly releasable before legal review. The place-fragment prototype can proceed earlier because it avoids the same direct facial privacy risk.

Generated outputs require their own review. Each output should be inspected to ensure that no living person appears recognisably, no source image is reconstructable, and no output creates a false implication about the source persons. A public ethics statement should describe what is collected, what is stored, what is discarded, what is never done, how opt-out or removal requests work, how legal review was conducted, and how the work relates to existing archives and relatives' organisations.

This framework is not only legal compliance. It is part of the artwork's conceptual structure. The work depends on distinguishing a visual field from a database of persons. If the system became a biometric apparatus, it would contradict the project's political logic.

## 8. Archival humility and responsible reactivation

The AI and archival-practice question at the centre of this paper is not simply whether AI can reactivate archives. It is what kind of reactivation is permissible when the archive is incomplete because violence made it incomplete.

In many cultural-heritage contexts, reactivation can mean making materials searchable, reconstructing missing parts, restoring damaged media, or generating new access pathways. In the context of disappearance, however, absence is not only material degradation. It is an effect of political concealment. A responsible computational memorial system must therefore avoid treating absence as a neutral information deficit.

I use the term archival humility to name this orientation. Archival humility means that the artwork relies on archives but does not claim their authority; cites sources but does not absorb them as raw material without context; presents names but does not convert lives into database entries; uses public images but does not treat them as unrestricted computational fuel; and makes visible the limits of what the system can know.

Archival humility also requires acknowledging that computational systems are seductive because they appear to produce continuity. A generated image can look more complete than the record. A reconstructed face can appear more vivid than an archival photograph. A smooth sequence can make the political wound seem formally resolved. In `desaparecidos.uy`, the visual language must therefore resist smoothness. The reconstructions should remain incomplete, unstable, materially legible, and visibly assembled. The viewer should perceive the tension between face and fragments, between person and country, between reconstruction and loss.

This approach contributes to responsible AI in art by shifting emphasis from what the system can generate to what the system must refuse to generate.

## 9. A framework for responsible computational memorial systems

The project proposes five principles for responsible AI and computational art in contexts of disappearance and unresolved political violence.

### 9.1 Archival humility

The system must not become a substitute archive. It should rely on existing public sources, cite them, and direct viewers back to them. It should avoid presenting itself as official, exhaustive, evidentiary, or corrective. Where possible, collaboration or consultation with memory and human-rights organisations should be pursued, but the artwork must remain clear about its own scope.

### 9.2 Fragmentary reappearance

The output should stage reappearance rather than restoration. The disappeared person becomes visible, but the image remains marked by the fragments that compose it. The system produces temporary apparitions, not replacement portraits.

### 9.3 Non-identification

The system must not identify, classify, or infer attributes from living source persons. In works using images of living people, source persons should not become represented subjects. The system should treat source imagery as visual matter under strict privacy constraints, not as a biometric resource.

### 9.4 Provenance accountability

Historical target images require provenance metadata. Visual source fields require documented acquisition rules. Generated outputs require review before publication. The project should make clear which images come from authoritative public sources, which images are self-captured, which are licensed, and which are excluded.

### 9.5 Designed incompletion

The artwork should preserve seams, gaps, mismatches, fragment boundaries, and temporal dissolution. Incompletion is not a failure to be solved after more technical work. It is a responsible form for a subject that cannot be repaired by representation.

These five principles are not a general ethics checklist. They emerge from the specific demands of a memorial artwork about enforced disappearance. However, they may be useful for other AI-art and archival projects dealing with violent histories, missing records, contested memory, or vulnerable visual subjects.

## 10. Evaluation and public review plan

Because the project is still in development, evaluation remains planned rather than completed. The evaluation should not be reduced to usability testing or aesthetic preference. It should examine whether the work's ethical and political distinctions remain legible.

The first evaluation layer is internal artistic and technical review. Outputs are examined for recognisability of the disappeared person, visibility of the fragmentary process, avoidance of photorealistic closure, absence of recognisable living source persons, and correct display of names and provenance.

The second layer is expert review. This may include consultation with scholars of memory, human-rights practitioners, legal advisors, data-protection specialists, artists working with archives, and, where appropriate, people connected to memory organisations. The purpose is not to ask others to authorise the work wholesale, but to identify risks, failures of framing, or harmful implications.

The third layer is public reception after a controlled release or exhibition. This may include qualitative responses from viewers, attention to misunderstandings, evaluation of whether the negative definitions are understood, and documentation of requests for removal or correction.

The fourth layer is legal and institutional review before any public release involving images of living persons. The place-based prototype can proceed earlier because it does not carry the same facial privacy risks, but the face-fragment component should remain internal until counsel review is complete.

The key evaluation questions are:

1. Does the work make disappearance perceptible as a continuing structure rather than a closed historical absence?
2. Does the visual language avoid technological restoration, spectacle, and sentimentality?
3. Are viewers able to understand that the outputs are not forensic, archival, biometric, or resurrection images?
4. Are source provenance, privacy commitments, and opt-out/removal procedures clear?
5. Does the work respect existing archives and relatives' organisations rather than competing with them?
6. Does the system produce images that are formally compelling without becoming ethically misleading?

These questions will guide the next stage of development and the later full article.

## 11. Conclusion

`desaparecidos.uy` asks what AI and computational art can responsibly do with absence when absence was produced by political violence. Its answer is deliberately limited. Computation cannot restore the disappeared. It cannot replace archives, forensic work, judicial truth, or the labour of families and human-rights organisations. It should not simulate testimony, animate the dead, generate false continuity, or transform disappearance into an aesthetic problem of insufficient data.

What it can do is construct a visual situation in which the unresolved present becomes perceptible. In **Todos somos familiares**, the disappeared emerge from the living social body. In **Están en todas partes**, they emerge from the country's material surfaces. In **Seguimos buscando**, they emerge through the continuing act of search. Each work insists that disappearance is not outside the present. It remains distributed across bodies, places, institutions, images, and silences.

The responsible use of AI in such a context depends not only on transparency or technical safeguards but on refusal. Refusal of restoration. Refusal of biometric capture. Refusal of archival substitution. Refusal of synthetic testimony. Refusal of the idea that a model can complete what political violence made incomplete.

This is the central proposition of the project: responsible computational memorial art must sometimes make images less complete, not more; less seamless, not more convincing; less resolved, not more lifelike. It must learn to make the missing visible without pretending that they have been returned.

## Figure placeholders

**Figure 1.** Triptych diagram: people, places, search. Placeholder for a schematic showing the three works and their source fields.

**Figure 2.** Stage 1 data flow. Placeholder for target portrait, approved place sources, fragment extraction, matching, output, and sidecar provenance.

**Figure 3.** Process-video frame sequence. Placeholder for the search scan, candidate rejection, fragment selection, assembly, and commemorative outro.

**Figure 4.** Ethics/provenance model. Placeholder for target images, source visual field, generated outputs, review gates, and exclusion rules.

## References

AI & SOCIETY. 2026. "CfP: Collection on Responsible use of AI in Art Creation and Archival Practice." Springer Nature. Accessed 18 June 2026. https://link.springer.com/journal/146/updates/27850936.

Azoulay, Ariella. 2008. *The Civil Contract of Photography*. New York: Zone Books.

Brodsky, Marcelo. 1997. *Buena Memoria*. Buenos Aires: La Marca.

Crawford, Kate. 2021. *Atlas of AI: Power, Politics, and the Planetary Costs of Artificial Intelligence*. New Haven: Yale University Press.

Derrida, Jacques. 1996. *Archive Fever: A Freudian Impression*. Translated by Eric Prenowitz. Chicago: University of Chicago Press.

Didi-Huberman, Georges. 2008. *Images in Spite of All: Four Photographs from Auschwitz*. Translated by Shane B. Lillis. Chicago: University of Chicago Press.

Dodecá. 2009. "Expone Juan Ángel Urruzola." 9 October 2009. Accessed 18 June 2026. https://dodeca.org/2009/10/expone-ja-urruzola/.

Fontes, Claudia. *Reconstrucción del retrato de Pablo Míguez*. Parque de la Memoria, Buenos Aires.

Germano, Gustavo. *Ausencias*.

Hirsch, Marianne. 2012. *The Generation of Postmemory: Writing and Visual Culture After the Holocaust*. New York: Columbia University Press.

Jelin, Elizabeth. 2003. *State Repression and the Labors of Memory*. Minneapolis: University of Minnesota Press.

Longoni, Ana, and Gustavo Bruzzone, eds. 2008. *El Siluetazo*. Buenos Aires: Adriana Hidalgo.

Madres y Familiares de Uruguayos Detenidos Desaparecidos. n.d. "Desaparecidos." Accessed 18 June 2026. https://desaparecidos.org.uy/.

Manovich, Lev. 2001. *The Language of New Media*. Cambridge, MA: MIT Press.

Nora, Pierre. 1989. "Between Memory and History: Les Lieux de Mémoire." *Representations* 26: 7-24.

Parque de la Memoria. n.d. *Monumento a las Víctimas del Terrorismo de Estado*. Buenos Aires.

Secretaría de Derechos Humanos para el Pasado Reciente. n.d. "Víctimas." Gobierno de Uruguay. Accessed 18 June 2026. https://www.gub.uy/secretaria-derechos-humanos-pasado-reciente/victimas.

Sitios de Memoria Uruguay. n.d. "Desaparición forzada." Accessed 18 June 2026. https://sitiosdememoria.uy/desaparicion-forzada.

Sitios de Memoria Uruguay. n.d. "Exportar datos." Accessed 18 June 2026. https://sitiosdememoria.uy/exportar-datos.

Sontag, Susan. 2003. *Regarding the Pain of Others*. New York: Farrar, Straus and Giroux.

Steyerl, Hito. 2009. "In Defense of the Poor Image." *e-flux journal* 10.

Taylor, Diana. 2003. *The Archive and the Repertoire: Performing Cultural Memory in the Americas*. Durham, NC: Duke University Press.

Traverso, Fernando. *Las bicicletas de Rosario*.

Unidad Reguladora y de Control de Datos Personales. 2020. "Resolución N° 30/020." Gobierno de Uruguay, 12 May 2020. Accessed 18 June 2026. https://www.gub.uy/unidad-reguladora-control-datos-personales/institucional/normativa/resolucion-n-30020.

Unidad Reguladora y de Control de Datos Personales. 2020. "Guía de Evaluación de Impacto en la Protección de Datos." Gobierno de Uruguay, 28 January 2020. Accessed 18 June 2026. https://www.gub.uy/unidad-reguladora-control-datos-personales/comunicacion/publicaciones/guia-evaluacion-impacto-proteccion-datos.

Urruzola, Juan Ángel. *Álbum de memoria*.

Zylinska, Joanna. 2020. *AI Art: Machine Visions and Warped Dreams*. London: Open Humanities Press.

### Author's prior work to cite only if double-blind rules allow, or anonymise as Author

Author. 2016. "Media Appropriation and Explicitation." *Journal of Science and Technology of the Arts* 8(2): 27-36.

Author. 2016. "5500: Performance, Control, and Politics." *Proceedings of NIME*.

Author. 2018. "Political New Media Artworks." *ISEA 2018*.

Author. 2021. "Pushing Back on Colonization." *IEEE Computer Graphics and Applications* 41(4): 118-124.

Author. 2024. "Capturing Collective Memories of the Disappeared with Artificial Intelligence." *Advances in Artificial Intelligence - IBERAMIA 2024*, LNCS 15277.

## Remaining revision tasks

1. Convert the reference list into final Springer style after the preferred citation manager/export format is chosen.
2. Insert selected Stage 1 stills or screenshots once the output set is stable.
3. Decide whether self-citations remain anonymised as "Author" at submission.
4. Check word count against the 8,000-word Open Forum limit after figures/captions are added.
5. Replace remaining artwork entries without stable authoritative URLs with stronger sources where available.
