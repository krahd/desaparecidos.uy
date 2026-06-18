# Incomplete Reconstruction: Conversational AI, Collective Memory, and the Governance of an Archive of the Disappeared

## Working note

This is a draft for a full Research Paper submission to the AI & SOCIETY special collection on responsible AI in art creation and archival practice. It is designed to be distinct from the Open Forum paper, **Against Restoration**, which focuses on computational memorial imagery and the artwork triptych. This manuscript focuses on the broader archive, conversational memory capture, governance, and methodological framework.

For double-blind review, replace project names, repository paths, authorial self-references, and self-citations with anonymised placeholders. Restore after review where allowed.

## Abstract

This article proposes a framework for the responsible use of conversational AI in the capture, preservation, and study of collective memories of detained-disappeared persons connected to Uruguay's civic-military dictatorship. It argues that AI-mediated memory work cannot be evaluated only through generic criteria of accuracy, usability, consent, or data protection. In contexts marked by enforced disappearance, archival incompletion, political denial, and intergenerational transmission of trauma, the central question is not simply whether an AI system can collect more testimony, but how it participates in the production of memory as an archival, social, and political form.

The paper presents a practice-based research project that develops a governed computational archive for memories of the disappeared in Uruguay. The project uses AI-based conversational interfaces not as neutral data-collection tools but as structured instruments for eliciting, preserving, and contextualising oral-style memory while preserving plurality, uncertainty, contradiction, silence, and participant agency. The article contributes: (1) a conceptual distinction between memory capture and archival extraction; (2) a modular architecture for conversational memory systems; (3) a governance model based on layered access, reversibility, provenance, minimality, and adversarial resilience; and (4) a methodological framework for evaluating AI-mediated memory work in politically sensitive contexts.

The central claim is that responsible AI archives of contested memory must resist the fantasy of synthetic historical completion. Their purpose is not to generate a single coherent account of the past, nor to replace existing archives, forensic work, legal processes, or the labour of relatives and human-rights organisations. Rather, they must create protected conditions under which situated voices can be captured, curated, studied, and, where appropriate, publicly encountered without reducing memory to extractable data.

## Keywords

responsible AI; collective memory; conversational AI; archives; enforced disappearance; Uruguay; human rights; AI governance; oral history; digital humanities

## 1. Introduction

Collective memories are being lost. In post-dictatorship societies such as Uruguay, a substantial part of the memory of political violence remains housed in living persons rather than in stable archival institutions. Relatives, former classmates, neighbours, co-workers, militants, teachers, students, journalists, local activists, and ordinary citizens continue to carry fragments of what happened: a remembered name, a rumour, a fear, a school absence, a phrase repeated in a family, a place avoided, an atmosphere of silence, a partial story of detention, exile, imprisonment, or disappearance. Many of these memories have never entered formal archives. Some may never be narrated unless conditions exist for their narration.

Artificial intelligence appears to offer new possibilities for this problem. Conversational systems can lower the barrier to participation, support oral-style interaction, adapt prompts to participants, generate metadata, assist transcription and redaction, and create pathways for later scholarly retrieval. Yet the same systems can also distort memory, over-structure narrative, extract sensitive data, simulate empathy, normalise surveillance, and convert contested memories into computationally convenient records. The problem is therefore not whether AI can help collect memory. It is under what conditions AI may participate responsibly in the construction of an archive.

This article examines that question through a practice-based research project concerned with collective memories of detained-disappeared persons connected to Uruguay's civic-military dictatorship. The project proposes a computational, humanistic, and artistic framework for capturing, preserving, governing, and studying memories of the disappeared. Its starting point is the recognition that enforced disappearance is not only a crime located in the past. It is a continuing violence whose effects persist through unresolved absence, incomplete records, legal struggle, family memory, public commemoration, and political denial. An AI system that enters this field does not operate on neutral content. It enters a dense political and ethical infrastructure of truth, justice, trauma, evidence, and memory.

The article argues that responsible AI in this context requires moving from an extractive model of memory capture to a governed model of archival co-production. Memories are not raw materials waiting to be collected. They are produced in discourse, in relation to interlocutors, technologies, expectations, power, trust, and fear. A conversational system does not simply record memory; it helps shape the form in which memory appears. For this reason, the system's prompts, interface, consent sequence, storage model, metadata schema, review process, and access rules are all part of the research contribution.

The contribution of the paper is fourfold. First, it develops a conceptual framework for distinguishing memory capture from archival extraction. Second, it proposes a modular architecture for AI-mediated memory archives, including interface, orchestration, conversational intelligence, storage, governance, and research-access layers. Third, it offers a governance model based on minimality, reversibility, layered access, provenance, adversarial resilience, and the distinction between public knowledge and public raw data. Fourth, it defines an evaluation agenda for politically sensitive AI memory systems, including technical, ethical, humanistic, and public-review criteria.

The paper is deliberately distinct from work on computational memorial imagery. That adjacent strand asks how the disappeared may be made visually perceptible without false restoration. The present article asks how memories surrounding the disappeared may be elicited, protected, studied, and governed without becoming extractable data or synthetic historical closure.

## 2. Historical and archival problem

Uruguay's civic-military dictatorship lasted from 1973 to 1985 and produced systematic human-rights violations, including political imprisonment, torture, exile, censorship, surveillance, and enforced disappearance. The dictatorship belongs to a broader Southern Cone history of state terror and transnational repression, including operations that crossed national borders and connected Uruguayan victims to events in Argentina and elsewhere.

The disappeared occupy a specific position within this history. Disappearance does not end with the removal of the person. It continues through the concealment of bodies, the destruction or withholding of records, the dispersal of testimony, the uncertainty imposed on relatives, and the political management of oblivion. A disappeared person remains socially present through an unresolved absence. Names, photographs, legal files, commemorative acts, family narratives, and public demands for truth and justice keep the disappeared in circulation, but often in fragmentary and unequal ways.

This produces a difficult archival condition. Some materials are public and institutionalised: lists of victims, judicial documents, public reports, human-rights organisation records, biographical entries, sites of memory, and historical studies. Other materials remain informal, private, or dispersed: memories held by persons who were not direct relatives, small episodes that never entered testimony, place-based recollections, rumours, affective atmospheres, political interpretations, inherited family stories, and everyday silences. These latter materials are often historically meaningful precisely because they show how political violence entered ordinary life.

The archive imagined in this project is therefore not only a repository of testimony. It is a sociotechnical structure for preserving plurality. It must be able to hold contradictory memories, partial memories, uncertain memories, emotional memories, and memories that are not directly evidentiary but are nevertheless culturally and historically significant. It must also accept that not every memory should become public. Responsible preservation does not equal indiscriminate publication.

## 3. From memory capture to archival co-production

The phrase memory capture can be misleading if it implies that memories exist as stable objects that can simply be extracted and stored. Collective memory is produced through narration, circulation, repetition, omission, conflict, and institutional framing. It is social before it is computational. A person does not narrate the same memory in every context. They speak differently to a relative, an interviewer, a museum, a judge, a journalist, a student, or an AI-mediated interface. The interlocutor matters.

Conversational AI makes this problem sharper. Unlike a passive recording device, a conversational system prompts, follows up, summarises, categorises, and sometimes suggests. It may invite detail, but it may also impose shape. It may encourage a participant to continue, but it may also make a traumatic memory feel bureaucratically processed. It may provide accessibility for people who would not write a formal testimony, but it may also create a false impression that the machine understands the historical weight of what is being said.

For this reason, the project treats AI-mediated memory capture as archival co-production. The system is part of the conditions under which the memory becomes recordable. Its design must therefore be evaluated not only technically but epistemologically and politically. What does it ask? What does it not ask? What forms of hesitation does it allow? What does it do with contradiction? Does it summarise too early? Does it ask for unnecessary personal data? Does it make the participant feel that a single narrative must be completed? Does it preserve the difference between a raw conversational trace, a transcript, a redacted version, metadata, and scholarly interpretation?

A responsible system must avoid two opposite failures. The first is romantic naivety: imagining that any memory offered to the system is automatically authentic, stable, and ethically available. The second is technocratic reductionism: treating memory as data to be normalised, classified, embedded, clustered, and retrieved. The system must instead support situated narration while preserving uncertainty, context, and participant agency.

## 4. System architecture

The project proposes a modular architecture organised into six layers: interface, orchestration, conversational intelligence, storage, governance, and research access. These layers are conceptually distinct even when implemented within the same software environment.

### 4.1 Interface layer

The interface layer consists of mobile-first and web-based conversational clients. Text interaction provides a baseline because it is technically robust and easy to review. Voice input and playback should be supported where appropriate because oral-style communication is central to memory work and may be more accessible for participants with limited literacy, limited comfort with formal writing, or stronger familiarity with spoken narration.

The interface must avoid the aesthetics of extraction, bureaucracy, and surveillance. It should communicate clarity, consent, and control. Participants should know what kind of project they are entering, what may happen to their materials, what choices they retain, and how to stop or revise the interaction.

### 4.2 Orchestration layer

The orchestration layer coordinates dialogue flow, session state, consent checkpoints, prompt selection, and transitions between conversational stages. It encodes the methodological logic of the encounter: entry and framing, relational calibration, elicitation, clarification, participant review, processing, and governance routing.

This layer is especially important because responsible memory capture depends on the timing and form of prompts. A system that asks too directly may appear interrogatory. A system that asks too generally may fail to elicit useful detail. A system that summarises prematurely may flatten the participant's voice. A system that never clarifies may produce records that later researchers cannot interpret. Orchestration is therefore a methodological rather than merely technical function.

### 4.3 Conversational intelligence layer

The conversational intelligence layer integrates language models with task-specific prompting strategies, controlled retrieval, safety rules, and post-processing functions such as summarisation, metadata generation, uncertainty tagging, and candidate thematic labels. Its purpose is not to produce fluent conversation for its own sake, but to support careful memory work.

The model must be constrained against leading questions, hallucinated context, premature interpretation, and therapeutic overreach. It should avoid claiming knowledge it does not possess. It should not present itself as a historian, lawyer, psychologist, or family member. It should behave as a structured elicitation instrument whose limits remain visible.

### 4.4 Storage layer

The storage layer separates raw interaction logs, audio files where applicable, transcripts, redacted transcripts, metadata, embeddings, and governance records. This separation is not a technical convenience. It is ethically necessary because different forms of data carry different risks.

Raw conversational traces may contain identifying information, third-party references, emotionally sensitive material, and unreviewed claims. Redacted transcripts may support analysis under controlled conditions. Metadata and embeddings may enable retrieval without exposing full narratives, but they also introduce their own risks of inference, clustering, and decontextualisation. The storage design must therefore preserve distinctions between original material, processed material, derived material, and interpretive material.

### 4.5 Governance layer

The governance layer manages identity protection, consent states, participant rights, retention policies, role-based access control, audit logs, and procedures for freezing, revising, reclassifying, or withdrawing records. Governance is implemented both technically and institutionally. It cannot be left as an external policy document detached from the code.

Every record should carry governance metadata: consent status, access tier, redaction status, review state, provenance, restrictions, and conditions for reuse. The system should also preserve the possibility that some materials remain private, embargoed, or unusable for public outputs.

### 4.6 Research-access layer

The research-access layer provides interfaces for approved uses of the archive. These may include controlled researcher workbenches, public-facing visualisations, thematic collections, search tools, timelines, maps, or curated excerpts. Research access should not mean direct access to raw data by default. Instead, access should be tiered and tied to review, purpose, risk, and participant consent.

## 5. Conversational pipeline

The conversational pipeline comprises seven stages.

### 5.1 Entry and framing

The system introduces the project, explains its purpose, clarifies that participation is voluntary, and describes what kinds of data may be retained. The objective is not only legal compliance but epistemic clarity: participants should understand that they are contributing to a memory project, not speaking to a private diary or an ordinary chatbot.

### 5.2 Relational calibration

The system asks whether the participant prefers a guided or open style, text or voice, shorter or longer responses, and whether they want to share their relation to the topic. This stage may include optional contextual information such as generation, region, relation to the dictatorship period, or preferred language register. Such information may improve interpretation, but it should never become mandatory in a way that reproduces bureaucratic distrust.

### 5.3 Elicitation

The system prompts memories using careful, non-leading questions. It may ask about people, places, events, atmospheres, routines, silences, rumours, public rituals, fears, absences, and later recollections. The prompting strategy must avoid implanting content or steering testimony toward simplified templates. It should encourage situated detail while accepting uncertainty.

### 5.4 Clarification

The system asks follow-up questions to clarify references, temporal markers, relationships among actors, place names, and possible ambiguities. Oral memory often contains indexical references that are clear to the speaker but opaque to future researchers. Clarification therefore protects interpretability without forcing artificial coherence.

### 5.5 Participant review

The participant should be offered the option to review, revise, segment, embargo, or delete parts of the interaction before it becomes an archival record. This stage is essential for preserving agency and for preventing the false assumption that a conversational trace automatically constitutes archival consent.

### 5.6 Processing

Once a session is authorised for retention, the system generates a protected raw record, a working transcript, and a derived set of metadata. Automated processes may include transcription, redaction suggestions, topic detection, uncertainty tagging, and vector indexing. No derivative layer should override the primacy of the original testimony.

### 5.7 Governance routing

Depending on the content and consent state, materials are routed into different retention classes: private, archived but restricted, research-accessible under protocol, publicly excerptable, or artistically reusable only with additional permission. Routing prevents a single default publication logic from governing all memories equally.

## 6. Governance principles

The governance model is based on six principles.

### 6.1 Minimality

The system should collect only the data necessary for the interaction and for the archival purpose explicitly agreed to by the participant. Identity linkage, if any is needed, should be stored separately from narrative content and protected more strongly.

### 6.2 Reversibility

Participants should retain the possibility, within defined limits, of withdrawing, revising, or reclassifying their contributions. Total reversibility may not always be possible once derivative publications or artworks exist, but the archival system itself should be designed around continuing agency rather than one-time extraction.

### 6.3 Layered access

Instead of a single public archive, the project proposes access tiers: private retention, collaborative review by the core team, vetted scholarly access under protocol, curated public access through redacted excerpts or visualisations, and fully public materials only when consent, risk, and content profile make such circulation responsible.

### 6.4 Provenance

Every transformation of a record should be logged. Researchers should be able to distinguish raw testimony, audio, transcript, redacted transcript, metadata, summary, embedding, clustering output, and curatorial interpretation. Provenance is necessary both for scholarly rigour and for preventing computationally derived views from obscuring the original narrative.

### 6.5 Adversarial resilience

Because the archive concerns a conflictive historical period, it must anticipate disruptive actors, trolling, coordinated disinformation, strategic mass submissions, and attempts to use the archive as a site of political capture. Governance must include moderation procedures, anomaly detection, provenance checks, rate limiting, human review, and institutional oversight.

### 6.6 Public knowledge without public raw data

The archive should contribute to public knowledge, but this does not imply indiscriminate release of collected materials. In many cases, the ethical path is to make interpretations, visualisations, thematic pathways, and carefully governed research access available while keeping raw records under stronger protection.

## 7. Search, analysis, and interpretive humility

A memory archive of this kind requires search and analysis tools, but those tools must not be mistaken for neutral interpretation. Memories are temporally unstable, metaphorical, affectively dense, incomplete, and socially indexical. Search must therefore combine structured metadata, full-text retrieval, and semantic retrieval while keeping the limits of each visible.

Structured metadata may include approximate dates, places, relational roles, thematic tags, and governance status. Full-text search supports direct retrieval over transcripts and participant-supplied language. Semantic retrieval can reveal related narratives that do not share identical vocabulary but do share conceptual or affective patterns. Yet semantic retrieval also risks producing relations whose logic is opaque to users. The interface must therefore make computational mediation visible.

Above this retrieval layer, the project may develop tools for discourse analysis, network visualisation, chronology reconstruction, thematic clustering, and comparative study. These tools should be presented as analytic aids, not as extracted truths. Summaries, clusters, and timelines must remain contestable and traceable to source materials.

Interpretive humility is the analytic counterpart of archival humility. It means that the archive should enable interpretation without pretending to automate historical understanding. AI may help scholars find, organise, and compare materials, but it cannot resolve political history.

## 8. Methodology

The project combines participatory design, ethnographic sensitivity, computational implementation, archival theory, discourse analysis, and iterative evaluation.

The participatory dimension is indispensable. Memories of traumatic and politically charged periods cannot be responsibly captured through a purely top-down technical design process. Prompts, interaction styles, consent flows, access categories, and review procedures must be developed in dialogue with local researchers, memory organisations, and, when appropriate, participants themselves.

An ethnographic sensibility is equally necessary. The archive must attend to the situated conditions under which memories are narrated: who is speaking, to whom, through what device, in what environment, and with what expectations or anxieties. The archive cannot pretend to store memory independently of the conditions of its elicitation.

The project also relies on iterative prototyping. Conversational prompts, workflow stages, metadata schemas, redaction procedures, and governance rules should be tested, evaluated, and revised across cycles of design and deployment. Failure modes are especially informative: overly directive prompts, unsafe emotional transitions, unusable consent flows, misleading summaries, or redaction systems that erase interpretively important detail all provide evidence necessary to refine the system.

Finally, the archive is itself a humanities research object. The project does not merely use humanities methods to support technology design; it generates a corpus for studying discourse, memory transmission, narrative form, silence, contradiction, and the cultural life of recent history.

## 9. Evaluation plan

Evaluation must be broader than usability. A system may be usable and still ethically or historically inadequate. The project therefore requires five evaluation layers.

### 9.1 Interaction quality

This layer evaluates whether participants understand the project, consent flow, rights, and possible uses of their contribution. It also examines whether prompts are clear, respectful, non-leading, and accessible across different levels of digital literacy.

### 9.2 Narrative integrity

This layer evaluates whether the system preserves the participant's voice, uncertainty, hesitation, and contextual meaning. It examines whether summaries distort the narrative, whether metadata is too reductive, and whether clarification prompts improve rather than flatten the record.

### 9.3 Privacy and safety

This layer evaluates whether identifying information, third-party references, sensitive details, and emotionally difficult content are handled appropriately. It also tests redaction workflows, access tiers, and withdrawal or revision procedures.

### 9.4 Scholarly usefulness

This layer evaluates whether the archive can support serious historical, discursive, and humanistic research. It asks whether records are sufficiently contextualised, whether provenance is clear, whether search and metadata are useful, and whether computational analysis remains traceable to source materials.

### 9.5 Public and institutional responsibility

This layer evaluates whether the archive contributes to public knowledge without competing with, replacing, or undermining existing memory institutions, relatives' organisations, legal processes, or forensic work. It also examines whether public-facing outputs are clearly framed and whether access decisions are legitimate.

## 10. Relation to artistic research

Although this paper focuses on archival and conversational systems, the project is also embedded in artistic research. The archive may eventually support installations, generative visual works, documentary experiments, audiovisual pieces, maps, timelines, and public interfaces. However, artistic reuse must be governed by the same ethical seriousness that guides the rest of the project.

Not every collected memory should become artistic material. Consent for archival retention is not automatically consent for exhibition, publication, performance, or generative transformation. Artistic reuse requires additional review and, in some cases, additional permission. This is especially important when working with trauma, third-party memories, family histories, and politically sensitive testimony.

The artistic dimension is nevertheless important because art can create public encounters with memory that do not depend on scholarly expertise. It can make fragmentation, silence, contradiction, and affect perceptible. It can show that an archive is not a static storehouse but a contested structure of attention, absence, and public responsibility.

## 11. Discussion: against synthetic completion

The most dangerous fantasy surrounding AI in memory work is the fantasy of completion. Because contemporary systems can generate plausible text, fill missing images, interpolate gaps, summarise documents, and produce fluent narratives, they invite the belief that historical incompletion is a technical problem. In the context of enforced disappearance, this is ethically wrong.

The incompletion of the archive is not merely a lack of data. It is the result of political violence. Records were hidden, bodies were concealed, testimony was suppressed, families were denied truth, and public knowledge was contested. A responsible AI system cannot repair that damage by generating a smoother story. At most, it can help preserve, organise, and interpret situated memories while marking the limits of what is known.

For this reason, the system should not aim to produce a single authoritative narrative of the dictatorship or the disappeared. It should preserve multiplicity. It should make contradiction visible. It should keep uncertainty attached to records. It should distinguish witness, memory, hearsay, family story, public document, computational summary, and scholarly interpretation. It should make its own mediation accountable.

This is the paper's central theoretical claim: responsible AI archives of contested memory should not complete the past; they should protect the conditions under which incompletion can be studied, remembered, and publicly confronted.

## 12. Conclusion

This article has proposed a framework for the responsible use of conversational AI in the capture, preservation, and study of collective memories of the disappeared in Uruguay. It has argued that AI-mediated memory work must be understood as archival co-production rather than neutral data collection. The system's interface, prompts, consent flow, storage model, governance rules, metadata, and access procedures are not auxiliary features. They shape what kind of memory becomes possible.

The proposed framework centres minimality, reversibility, layered access, provenance, adversarial resilience, interpretive humility, and the distinction between public knowledge and public raw data. It treats conversational AI as a structured instrument that may support memory work only if embedded within strong ethical, institutional, and political constraints.

The project contributes to responsible AI in art and archival practice by shifting the question from what AI can collect to what kind of archive AI helps produce. In contexts of enforced disappearance, the responsible archive is not the most complete archive, nor the most open archive, nor the most computationally searchable archive. It is the archive that preserves memory without extracting it, enables study without flattening it, supports public knowledge without exposing vulnerable persons, and refuses the fantasy that synthetic continuity can repair political violence.

## Figure placeholders

**Figure 1. Project architecture.** Mobile/web/voice interface, orchestration layer, conversational intelligence layer, protected storage, governance layer, and research-access layer.

**Figure 2. Conversational pipeline.** Entry/framing, relational calibration, elicitation, clarification, participant review, processing, governance routing.

**Figure 3. Layered access model.** Private record, restricted archive copy, research-access copy, curated public excerpts/visualisations, artistic reuse under additional permission.

**Figure 4. Record transformation provenance.** Raw interaction, transcript, redacted transcript, metadata, embeddings, summaries, research interpretation.

## References

AI & SOCIETY. 2026. "CfP: Collection on Responsible use of AI in Art Creation and Archival Practice." Springer Nature. Accessed 18 June 2026. https://link.springer.com/journal/146/updates/27850936.

Achugar, Mariana. 2016. *Discursive Processes of Intergenerational Transmission of Recent History: (Re)making Our Past*. New York: Palgrave Macmillan.

Azoulay, Ariella. 2008. *The Civil Contract of Photography*. New York: Zone Books.

Caswell, Michelle. 2014. *Archiving the Unspeakable: Silence, Memory, and the Photographic Record in Cambodia*. Madison: University of Wisconsin Press.

Crawford, Kate. 2021. *Atlas of AI: Power, Politics, and the Planetary Costs of Artificial Intelligence*. New Haven: Yale University Press.

Derrida, Jacques. 1996. *Archive Fever: A Freudian Impression*. Translated by Eric Prenowitz. Chicago: University of Chicago Press.

Dignum, Virginia. 2019. *Responsible Artificial Intelligence: How to Develop and Use AI in a Responsible Way*. Cham: Springer.

Hirsch, Marianne. 2012. *The Generation of Postmemory: Writing and Visual Culture After the Holocaust*. New York: Columbia University Press.

Jelin, Elizabeth. 2003. *State Repression and the Labors of Memory*. Minneapolis: University of Minnesota Press.

Madres y Familiares de Uruguayos Detenidos Desaparecidos. n.d. "Desaparecidos." Accessed 18 June 2026. https://desaparecidos.org.uy/.

Nora, Pierre. 1989. "Between Memory and History: Les Lieux de Mémoire." *Representations* 26: 7-24.

Secretaría de Derechos Humanos para el Pasado Reciente. n.d. "Víctimas." Gobierno de Uruguay. Accessed 18 June 2026. https://www.gub.uy/secretaria-derechos-humanos-pasado-reciente/victimas.

Sitios de Memoria Uruguay. n.d. "Desaparición forzada." Accessed 18 June 2026. https://sitiosdememoria.uy/desaparicion-forzada.

Stilgoe, Jack, Richard Owen, and Phil Macnaghten. 2013. "Developing a Framework for Responsible Innovation." *Research Policy* 42 (9): 1568-1580.

Taylor, Diana. 2003. *The Archive and the Repertoire: Performing Cultural Memory in the Americas*. Durham, NC: Duke University Press.

Unidad Reguladora y de Control de Datos Personales. 2020. "Resolución N° 30/020." Gobierno de Uruguay, 12 May 2020. Accessed 18 June 2026. https://www.gub.uy/unidad-reguladora-control-datos-personales/institucional/normativa/resolucion-n-30020.

Unidad Reguladora y de Control de Datos Personales. 2020. "Guía de Evaluación de Impacto en la Protección de Datos." Gobierno de Uruguay, 28 January 2020. Accessed 18 June 2026. https://www.gub.uy/unidad-reguladora-control-datos-personales/comunicacion/publicaciones/guia-evaluacion-impacto-proteccion-datos.

### Author's prior work to cite only if double-blind rules allow, or anonymise as Author

Author. 2024. "Capturing Collective Memories of the Disappeared with Artificial Intelligence." *Advances in Artificial Intelligence - IBERAMIA 2024*, LNCS 15277.

Author. 2026. "Against Restoration: Responsible AI, Disappearance, and Computational Memorial Systems." Draft Open Forum manuscript.
