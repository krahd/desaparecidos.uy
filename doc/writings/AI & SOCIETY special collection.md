Insertions still needed before submission
Artwork description: one concrete paragraph describing the current prototype’s actual output: number of portraits, source image corpus, still/video form, and reconstruction behaviour.
Figures: at least 3–5 images: source-place fragments, target preparation, reconstruction process, finished still, temporal/video storyboard.
Method specificity: current algorithmic details: patch size, feature matching, colour/texture/embedding pipeline, whether ML/AI is used beyond computational assembly.
Evaluation paragraph: even if preliminary, include internal review criteria and any first responses from trusted viewers/collaborators.
Anonymisation: because AI & SOCIETY uses double-blind review for Open Forum papers, author/project URLs and repository identifiers will need to be anonymised in the submitted manuscript.


# Against Restoration: Responsible AI, Disappearance, and Computational Memorial Systems in *desaparecidos.uy*

**Tomas Laurenzo**

## Abstract

This Open Forum paper presents *desaparecidos.uy*, a developing series of computational memorial artworks addressing the detained-disappeared connected to Uruguay’s civic-military dictatorship and the broader regional apparatus of repression in the Southern Cone. The project reconstructs public images of disappeared persons from fragments of the country that survived them: people, places, streets, walls, landscapes, and contemporary visual infrastructures. It is conceived as a triptych: *Todos somos familiares*, which uses fragments from publicly available images of contemporary people in Uruguay; *Están en todas partes*, which uses images of places, surfaces, streets, buildings, and landscapes; and *Seguimos buscando*, which turns traversal and search across the country’s visual field into the temporal structure of the work.

The paper argues that responsible AI in art and archival practice cannot be reduced to consent, provenance, transparency, or technical safeguards, though all of these remain necessary. In contexts of unresolved state violence, responsible practice also requires a politics of refusal: refusal of forensic authority, refusal of resurrection media, refusal of biometric identification, refusal of archival substitution, and refusal of the fantasy that computation can repair what politics destroyed. The project therefore proposes a framework for computational memorial systems based on five principles: archival humility, fragmentary reappearance, non-identification, provenance accountability, and designed incompletion. Rather than presenting AI as a restorative technology, *desaparecidos.uy* treats computation as a means of staging a visual and political condition: disappearance is not an absence sealed in the past, but a structure distributed through the present.

## Keywords

responsible AI; AI art; computational memorials; enforced disappearance; Uruguay; archives; visual culture; memory; biometric refusal; digital memorialization

## 1. Introduction

The increasing use of artificial intelligence in artistic creation and archival practice has intensified a set of questions that are not only technical or procedural, but also historical and political. What may be reactivated? What may be reconstructed? What should remain unresolved? What kinds of absence can be made perceptible without being falsely repaired? These questions become especially urgent when AI systems are used in relation to political violence, forced disappearance, missing persons, traumatic archives, and contested public memory.

This paper presents *desaparecidos.uy*, a developing computational memorial artwork series concerning Uruguay’s detained-disappeared. The project begins from a simple but difficult proposition: the image of each disappeared person is reassembled from fragments of the country that survived them. These fragments may come from images of contemporary Uruguayans, from streets and surfaces, from landscapes and public buildings, or from traversal across the country’s present visual field. The work does not claim to restore the disappeared. It does not claim to reconstruct unknown facts, recover lost bodies, generate testimony, or produce forensic evidence. Its aim is more limited and, for that reason, more precise: to construct a visual condition in which the unresolved persistence of disappearance becomes newly perceptible.

The project’s central premise is that disappearance is not only a historical absence. It is a continuing political structure. Enforced disappearance attacks evidence, kinship, narration, mourning, and legal recognition. It makes a person unavailable to family, public record, justice, biography, and the social rituals through which the living are recognized and the dead are mourned. In this sense, disappearance continues for as long as fate and whereabouts remain unresolved, archives remain incomplete, perpetrators withhold information, and public life treats absence as a settled historical fact rather than as an active structure.

In recent years, generative AI has made plausible the simulation of faces, voices, gestures, and documentary styles. This has opened powerful artistic possibilities, but also specific dangers. When directed toward the dead, the disappeared, or the politically silenced, AI can easily slide into resurrection aesthetics: a technological performance of restoration in which the system appears to speak for those who were deprived of speech, produce bodies where bodies were disappeared, or complete images that historical violence made fragmentary. *desaparecidos.uy* takes the opposite route. It treats incompletion not as a defect to be overcome, but as an ethical form.

The paper is written at the stage of a developing artwork. It therefore does not present a finished evaluation, public reception study, or completed installation analysis. Instead, it offers a case-based methodological framework for responsible AI art in relation to archives, political violence, and memorial practice. The first prototype under development is *Están en todas partes*, the place-based component of the triptych, because it is conceptually strong while carrying lower privacy risk than a face-fragment work using images of living persons. Evaluation, exhibition documentation, and public reception will be added in later versions of the research.

## 2. Historical and political horizon

Uruguay’s civic-military dictatorship, from 1973 to 1985, belongs to a wider Southern Cone history of state terror, clandestine detention, torture, exile, surveillance, censorship, and enforced disappearance. The disappeared connected to Uruguay include people detained in Uruguay, Argentina, and elsewhere through transnational repressive networks. Their public memory has been sustained by relatives’ organizations, human-rights groups, legal struggles, forensic work, archives, sites of memory, and public acts of insistence.

The term “disappeared” is therefore not a metaphor. It names a political technology. A disappeared person is not simply missing. Disappearance is produced by institutional and state violence, followed by denial, concealment, fragmentation of evidence, and the prolonged withholding of truth. The disappeared person is removed not only from social life but from the systems through which society verifies presence and death: legal records, bodies, graves, testimony, institutional acknowledgment, and public narration.

In Uruguay, relatives’ organizations and memory institutions have built a long public history of resistance to this erasure. Madres y Familiares de Uruguayos Detenidos Desaparecidos maintains public materials, lists, biographies, posters, and memory resources. The Secretaría de Derechos Humanos para el Pasado Reciente provides public victim files and lists. Sitios de Memoria Uruguay maps and documents places connected to repression, detention, findings of disappeared persons, and operations of state terrorism. These resources are not simply data sources. They are part of a decades-long political and ethical infrastructure of memory, truth, and justice.

*desaparecidos.uy* does not attempt to create a parallel authority over this infrastructure. It does not replace official archives, family testimonies, forensic investigation, legal process, or the historical work of human-rights organizations. The project depends on such sources for provenance, naming, and minimal public historical information, but its own contribution is artistic rather than archival or judicial. It asks how computational art can make absence active without claiming to solve it.

The project therefore treats Uruguay itself as the image field of the work. The country is not a background, landscape, or national symbol. It becomes the material support through which the disappeared reappear. The central claim is not that the disappeared can be restored, but that the present cannot be understood without them.

## 3. The triptych: people, places, search

*desaparecidos.uy* is conceived as a triptych of related computational memorial systems.

The first work, *Todos somos familiares*, reconstructs public images of disappeared persons from fragments extracted from publicly available images of contemporary Uruguayans. Its title is deliberately direct. It does not claim that all Uruguayans have the same relation to disappearance, nor does it flatten the specific historical and political labour of relatives’ organizations. Rather, it states an ethical demand: the disappeared cannot remain the responsibility of biological families alone. Disappearance reorganizes the social body and produces a collective debt, even when pain and responsibility are not equally distributed.

In this work, contemporary faces become visual material from which disappeared faces partially reappear. The system does not identify the living persons whose images contribute fragments. It does not classify them, name them, infer attributes from them, or represent them as individuals. Their images enter only as dispersed visual matter: colour, tone, texture, shadow, contour, surface, and partial form. The work is therefore not a biometric database but a political condensation of visual responsibility.

The second work, *Están en todas partes*, reconstructs public images of disappeared persons from fragments extracted from images of Uruguay’s places: walls, streets, buildings, pavements, rural roads, institutional facades, river edges, landscapes, ruins, monuments, neighbourhoods, and ordinary surfaces. If *Todos somos familiares* begins from the living social body, *Están en todas partes* begins from the material body of the country. Its claim is not that every place is directly connected to every disappearance. Its claim is structural: disappearance reshapes the political meaning of place. It marks the country as a whole, not only the specific sites of detention, torture, burial, testimony, or commemoration.

This second work is the first prototype because it preserves the conceptual core of the project while lowering immediate privacy risks. Place-based imagery allows the system to develop a visual language of texture, erosion, architecture, geography, institutional austerity, urban decay, rural dispersion, and everyday surfaces. The disappeared appear from the country rather than being placed over it.

The third work, *Seguimos buscando*, transforms the act of search into the temporal structure of the work. It imagines the country as an image field to be scanned, crossed, searched, and revisited. The work may use street-level imagery, self-captured footage, archival routes, crowdsourced material, or other ethically reviewed forms of visual traversal. Its central gesture is not the static composition of a portrait but the process by which a face emerges from movement through the country.

Together, the triptych moves across three forms of implication. The living social body participates in the image. The country’s surfaces participate in the image. Search itself becomes the work’s temporal form.

## 4. Artistic lineage: from memorial mosaic to computational implication

The project acknowledges Juan Ángel Urruzola’s *Álbum de memoria* as a central Uruguayan precedent. In that work, small identification-style photographs of detained-disappeared persons were assembled into the enlarged face of another disappeared person. Tatiana Oroño described the work as a mosaic of tiny faces in which the enlarged image appears only as the viewer approaches.

This precedent is not an obstacle but a lineage. *desaparecidos.uy* differs in source field, computational method, and political operation. Urruzola’s work forms the face of one disappeared person from images of other disappeared persons. *desaparecidos.uy* forms the public images of disappeared persons from fragments of contemporary Uruguay: living faces, material surfaces, streets, walls, landscapes, and public visual infrastructures.

The difference is therefore not merely technical. In *Álbum de memoria*, the disappeared visually sustain one another. In *desaparecidos.uy*, the disappeared emerge from the country that remains. The work shifts from memorial co-presence among the disappeared to an implicating relation between disappearance and the present social and material body of Uruguay.

The project also belongs to a broader history of photographic assemblage, computational mosaics, database aesthetics, new media appropriation, and algorithmic image-making. Yet its originality does not lie in composing a large image from smaller images. It lies in a specific artistic and political operation: a computational memorial system that makes the disappeared appear from the unresolved present.

## 5. Against restoration

The project requires precise negative definitions. These exclusions are not defensive additions to the work. They are part of its method.

First, the works are not forensic reconstructions. They do not claim to improve the historical image of a disappeared person, recover unknown facial details, or produce evidentiary images. Their outputs are not images for identification, prosecution, or documentation of unknown facts.

Second, the works are not documentary archives. They may refer to archives and public records, but they do not replace them. The authority of the historical record remains with families, human-rights organizations, historians, judicial processes, official investigative bodies, and existing archives.

Third, the works are not biometric systems. They do not identify living persons, classify faces, infer demographic or behavioural categories, or create a searchable database of people. In the face-fragment component, the use of publicly circulating images of contemporary people is governed by a distinction between visual fragments and person representation.

Fourth, the works are not deepfakes or resurrection media. They do not animate the disappeared as if they were alive. They do not synthesize speech, fabricate testimony, simulate subjectivity, or produce the fantasy of technological return.

Finally, the works are not monuments to technological power. They do not present computation as the force that restores what politics destroyed. At most, computation can produce a visual and political structure through which the unresolved condition of disappearance becomes perceptible.

This refusal of restoration is central to the responsible use of AI in contexts of political violence. AI systems are often valued for their capacity to fill gaps, increase resolution, interpolate missing frames, infer hidden structures, and generate plausible continuities. In this project, those capacities are approached with suspicion. The gaps are not simply technical absences. They are the marks of a political crime. To fill them too smoothly risks transforming violence into a solvable representational problem.

## 6. Visual and computational method

The system begins with public images of disappeared persons. These target images are drawn from responsible public sources and accompanied by provenance metadata: source, date of access, image status, person’s name, and any minimal public biographical details included in the source. The goal is not to enhance, beautify, complete, or modernize the target image. The historical image remains the referential anchor.

Source images differ across the three works. *Todos somos familiares* uses fragments from publicly available images of contemporary people in Uruguay. *Están en todas partes* uses images of places, surfaces, landscapes, buildings, streets, and material environments. *Seguimos buscando* uses traversal-based imagery: routes, sequences, street-level views, self-captured footage, or other moving visual fields.

The computational process has six stages.

First, target preparation: each public image of a disappeared person is prepared as a target. Normalization may occur for scale, contrast, or alignment, but only to the extent required by the reconstruction process. The image is not repaired.

Second, source acquisition: the source image field is collected according to the rules of each work. In the place-based prototype, acquisition privileges self-captured, licensed, institutional, public-domain, or clearly reusable imagery of places. In the face-fragment prototype, any use of public images of living persons must be legally and ethically reviewed before release.

Third, fragment extraction: the source image field is decomposed into visual units. These may be rectangular patches, irregular fragments, texture samples, colour fields, edge fields, or other visual units. The important constraint is that the fragment remains materially legible in the final output. The face must not dissolve into photorealistic smoothing.

Fourth, matching and assembly: regions of the target portrait are compared with fragments from the source field. Matching may use colour, luminance, gradient, edge direction, texture, local contrast, spatial composition, perceptual similarity, learned embeddings, or combinations of these methods. The system should not require semantic identification of source persons or places.

Fifth, temporal rendering: video becomes central because it can show reappearance as process. A typical sequence begins with unorganized fragments; the system sorts, moves, compares, and places them; a face becomes perceptible; the portrait reaches a fragile moment of recognition; the person’s name and minimal public data appear; the image destabilizes, dissolves, or returns to the visual field; and the next reconstruction begins. The work should not end in restoration but in continued search.

Sixth, output: the project may exist as a web artwork, generated videos, a multi-channel installation, large-format prints, lightboxes, an interactive kiosk, or a documented open-source system with restricted or synthetic sample data. The web version should expose method, limits, source categories, privacy principles, relation to archives, and artistic lineage rather than simply displaying finished images.

## 7. Privacy and non-identification

The project’s responsible-AI framework begins from the recognition that public availability is not equivalent to unrestricted consent. Images circulating online may be technically accessible but ethically fragile. This is especially true when processing faces, when working across national and institutional jurisdictions, or when images may reveal sensitive contexts.

For the face-fragment component, the working principle is that the work may store face-derived visual fragments but does not identify, classify, or represent the living persons whose publicly available images may have contributed fragments. It treats the web as a dispersed visual field, not as a biometric archive.

This principle has practical consequences. The release pipeline should avoid storing full source faces wherever possible; store fragments rather than complete portraits; limit the size of contiguous fragments; avoid recognizable crops of eyes, mouths, or full facial structures; prevent any single source image from contributing too much to any final portrait; separate source identity from visual fragments; document deletion policies for raw source material; and exclude images from contexts involving minors, health, criminal justice, education, protests, funerals, religious ceremonies, political meetings, shelters, or other sensitive situations unless explicit permission exists.

Generated outputs require their own review. Each output should be inspected to ensure that no living person appears recognizably, no source image is reconstructable, and no output creates a false implication about the source persons. A public ethics statement should describe what is collected, what is stored, what is discarded, what is never done, how opt-out or removal requests work, how legal review was conducted, and how the work relates to existing archives and relatives’ organizations.

This framework is not only legal compliance. It is part of the artwork’s conceptual structure. The work depends on distinguishing a visual field from a database of persons. If the system became a biometric apparatus, it would contradict the project’s political logic.

## 8. Archival humility and responsible reactivation

The AI & archival-practice question at the centre of this paper is not simply whether AI can reactivate archives. It is what kind of reactivation is permissible when the archive is incomplete because violence made it incomplete.

In many cultural-heritage contexts, reactivation can mean making materials searchable, reconstructing missing parts, restoring damaged media, or generating new access pathways. In the context of disappearance, however, absence is not only material degradation. It is an effect of political concealment. A responsible computational memorial system must therefore avoid treating absence as a neutral information deficit.

I use the term archival humility to name this orientation. Archival humility means that the artwork relies on archives but does not claim their authority; cites sources but does not absorb them as raw material without context; presents names but does not convert lives into database entries; uses public images but does not treat them as unrestricted computational fuel; and makes visible the limits of what the system can know.

Archival humility also requires acknowledging that computational systems are seductive because they appear to produce continuity. A generated image can look more complete than the record. A reconstructed face can appear more vivid than an archival photograph. A smooth sequence can make the political wound seem formally resolved. In *desaparecidos.uy*, the visual language must therefore resist smoothness. The reconstructions should remain incomplete, unstable, materially legible, and visibly assembled. The viewer should perceive the tension between face and fragments, between person and country, between reconstruction and loss.

This approach contributes to responsible AI in art by shifting emphasis from what the system can generate to what the system must refuse to generate.

## 9. A framework for responsible computational memorial systems

The project proposes five principles for responsible AI and computational art in contexts of disappearance and unresolved political violence.

### 9.1. Archival humility

The system must not become a substitute archive. It should rely on existing public sources, cite them, and direct viewers back to them. It should avoid presenting itself as official, exhaustive, evidentiary, or corrective. Where possible, collaboration or consultation with memory and human-rights organizations should be pursued, but the artwork must remain clear about its own scope.

### 9.2. Fragmentary reappearance

The output should stage reappearance rather than restoration. The disappeared person becomes visible, but the image remains marked by the fragments that compose it. The system produces temporary apparitions, not replacement portraits.

### 9.3. Non-identification

The system must not identify, classify, or infer attributes from living source persons. In works using images of living people, source persons should not become represented subjects. The system should treat source imagery as visual matter under strict privacy constraints, not as a biometric resource.

### 9.4. Provenance accountability

Historical target images require provenance metadata. Visual source fields require documented acquisition rules. Generated outputs require review before publication. The project should make clear which images come from authoritative public sources, which images are self-captured, which are licensed, and which are excluded.

### 9.5. Designed incompletion

The artwork should preserve seams, gaps, mismatches, fragment boundaries, and temporal dissolution. Incompletion is not a failure to be solved after more technical work. It is a responsible form for a subject that cannot be repaired by representation.

These five principles are not a general ethics checklist. They emerge from the specific demands of a memorial artwork about enforced disappearance. However, they may be useful for other AI-art and archival projects dealing with violent histories, missing records, contested memory, or vulnerable visual subjects.

## 10. Planned evaluation and public review

Because the project is still in development, evaluation remains planned rather than completed. The evaluation should not be reduced to usability testing or aesthetic preference. It should examine whether the work’s ethical and political distinctions remain legible.

The first evaluation layer will be internal artistic and technical review. Outputs will be examined for recognizability of the disappeared person, visibility of the fragmentary process, avoidance of photorealistic closure, absence of recognizable living source persons, and correct display of names and provenance.

The second layer will be expert review. This may include consultation with scholars of memory, human-rights practitioners, legal advisors, data-protection specialists, artists working with archives, and, where appropriate, people connected to memory organizations. The purpose is not to ask others to authorize the work wholesale, but to identify risks, failures of framing, or harmful implications.

The third layer will be public reception after a controlled release or exhibition. This may include qualitative responses from viewers, attention to misunderstandings, evaluation of whether the negative definitions are understood, and documentation of requests for removal or correction.

The fourth layer will be legal and institutional review before any public release involving images of living persons. The place-based prototype can proceed earlier because it does not carry the same facial privacy risks, but the face-fragment component should remain internal until counsel review is complete.

The key evaluation questions are:

1. Does the work make disappearance perceptible as a continuing structure rather than a closed historical absence?
2. Does the visual language avoid technological restoration, spectacle, and sentimentality?
3. Are viewers able to understand that the outputs are not forensic, archival, biometric, or resurrection images?
4. Are source provenance, privacy commitments, and opt-out/removal procedures clear?
5. Does the work respect existing archives and relatives’ organizations rather than competing with them?
6. Does the system produce images that are formally compelling without becoming ethically misleading?

These questions will guide the next stage of development and the later full article.

## 11. Conclusion

*desaparecidos.uy* asks what AI and computational art can responsibly do with absence when absence was produced by political violence. Its answer is deliberately limited. Computation cannot restore the disappeared. It cannot replace archives, forensic work, judicial truth, or the labour of families and human-rights organizations. It should not simulate testimony, animate the dead, generate false continuity, or transform disappearance into an aesthetic problem of insufficient data.

What it can do is construct a visual situation in which the unresolved present becomes perceptible. In *Todos somos familiares*, the disappeared emerge from the living social body. In *Están en todas partes*, they emerge from the country’s material surfaces. In *Seguimos buscando*, they emerge through the continuing act of search. Each work insists that disappearance is not outside the present. It remains distributed across bodies, places, institutions, images, and silences.

The responsible use of AI in such a context depends not only on transparency or technical safeguards but on refusal. Refusal of restoration. Refusal of biometric capture. Refusal of archival substitution. Refusal of synthetic testimony. Refusal of the idea that a model can complete what political violence made incomplete.

This is the central proposition of the project: responsible computational memorial art must sometimes make images less complete, not more; less seamless, not more convincing; less resolved, not more lifelike. It must learn to make the missing visible without pretending that they have been returned.

## References

Azoulay, Ariella. 2008. *The Civil Contract of Photography*. New York: Zone Books.

Derrida, Jacques. 1996. *Archive Fever: A Freudian Impression*. Translated by Eric Prenowitz. Chicago: University of Chicago Press.

Didi-Huberman, Georges. 2008. *Images in Spite of All: Four Photographs from Auschwitz*. Translated by Shane B. Lillis. Chicago: University of Chicago Press.

Dodecá. 2009. “Expone Juan Ángel Urruzola.” 9 October 2009.

Hirsch, Marianne. 2012. *The Generation of Postmemory: Writing and Visual Culture After the Holocaust*. New York: Columbia University Press.

Madres y Familiares de Uruguayos Detenidos Desaparecidos. “Desaparecidos.”

Nora, Pierre. 1989. “Between Memory and History: Les Lieux de Mémoire.” *Representations* 26: 7–24.

Secretaría de Derechos Humanos para el Pasado Reciente. “Víctimas.” Gobierno de Uruguay.

Sitios de Memoria Uruguay. “Sitios de Memoria Uruguay.”

Sontag, Susan. 2003. *Regarding the Pain of Others*. New York: Farrar, Straus and Giroux.

Steyerl, Hito. 2009. “In Defense of the Poor Image.” *e-flux journal* 10.

Taylor, Diana. 2003. *The Archive and the Repertoire: Performing Cultural Memory in the Americas*. Durham, NC: Duke University Press.

Unidad Reguladora y de Control de Datos Personales. “Sobre datos personales.” Gobierno de Uruguay.

Unidad Reguladora y de Control de Datos Personales. 2020. “Resolución N° 30/020.” 12 May 2020.
