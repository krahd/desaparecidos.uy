# Summer Publication Plan and Review Matrices

## Purpose

This document coordinates the summer writing programme. It has four functions:

1. keep the two AI & SOCIETY submissions structurally distinct;
2. prevent self-plagiarism or argument cannibalisation across manuscripts;
3. maintain a ranked queue of paper projects for summer and early autumn;
4. provide review tables for status, venue fit, source material, overlap risk, figures, and next actions.

The plan assumes a high-output summer without lowering venue ambition. Speed is not treated as a reason to choose weak venues. Each manuscript must have a distinct object, mechanism, argument, and target readership.

The uploaded review dossier, grant materials, CV, artwork portfolio, and professional plan support a broader publication programme than the immediate AI-memory pair. The plan therefore keeps the AI & SOCIETY submissions first, but also foregrounds BatLLM/AI-literacy papers, Paso de Morlán/digital-humanities reconstruction, music/sound/computational-composition papers, thesis-derived theory, bioart, political media, and artificial-exhibition/curatorial AI work as legitimate publication streams.

---

## 0. Project genealogy and ethical pivot

| Period / material | Project position | Publication consequence |
|---|---|---|
| 2023 *Liminal Memory* proposal | restorative/forensic ambition: high-resolution reconstructions, ageing, family images, phenotypical information | do **not** let current papers inherit this restoration rhetoric; cite only as project prehistory if needed |
| 2024 *Capturing Collective Memories* proposal | conversational AI and public-facing anonymised data/visualisation imagined as primary outputs | useful as origin of the Research Paper, but must be superseded by later governance lessons |
| 2024-2025 final report | prototypes and outputs succeeded, but ethical review led to non-publication of anonymised testimony data and non-release of interactive-prototype source code | central to Research Paper: responsible AI may require non-release, restricted access, or delayed release |
| 2026 de Castro / PFH / PTR framing | archive as sociotechnical formation; memory, AI literacy, governance, fieldwork, and public-facing art | strengthens Research Paper and justifies future archive-politics papers |
| Current `desaparecidos.uy` implementation | anti-restorative computational memorial system; coarse fragment matcher; no identity model; active source cap | central to Open Forum: designed incompletion is operational, not merely rhetorical |
| Paso de Morlán proposals | source-conditioned visual hypotheses under archival absence, with co-creation, model cards, provenance, and reviewability | separate digital-humanities / AI-historical-reconstruction paper; do not merge with disappeared papers |

---

## 1. Immediate AI & SOCIETY pair

| Manuscript | Type | Working title | Core object | Core contribution | Status | Primary risk | Next action |
|---|---|---|---|---|---|---|---|
| Open Forum | Open Forum paper | **Against Restoration: Responsible AI, Disappearance, and Computational Memorial Systems** | computational memorial artwork triptych; Stage 1 **Están en todas partes** prototype | argues for refusal of restoration, biometric capture, archival substitution, resurrection media, and synthetic completion; now accurately describes the implemented 6-D descriptor, L2 nearest-neighbour matcher, 24-pixel tiles, reuse limits, and active source cap | revised manuscript in `doc/writings/ai-society-open-forum.md`; four SVG figures added | final double-blind anonymisation; final reference style; frontend label still needs UI polish even though runtime cap is active | proofread; run final anonymisation; export figures; confirm source-cap behaviour in one generated sidecar |
| Research Paper | Research Paper | **Incomplete Reconstruction: Conversational AI, Collective Memory, and the Governance of an Archive of the Disappeared** | conversational AI archive for collective memories of the disappeared | proposes architecture, governance, conversational pipeline, access model, evaluation framework, and ethical pivot from open release to governed non-release | revised draft in `doc/writings/ai-society-research-paper-draft.md`; four SVG figures added | overlap with IBERAMIA paper if expansion is not explicit enough; must not imply dataset/code release by default | expand literature and empirical/method detail; final overlap audit; add fieldwork/prototype status precisely |

### Separation rule

The Open Forum paper is about **computational memorial imagery**. The Research Paper is about **conversational memory capture and archive governance**. The overlap is historical and ethical, not methodological.

| Dimension | Open Forum paper | Research Paper |
|---|---|---|
| Main verb | visualise / stage / refuse | elicit / preserve / govern |
| Main object | artwork triptych and place-fragment prototype | AI-supported collective memory archive |
| Main method | fragment matching, visual source fields, process videos | conversational pipeline, consent, metadata, access tiers |
| Main theory | anti-restoration; archival humility; designed incompletion | archival co-production; governance; interpretive humility; non-release by default |
| Main risk | being read as deepfake/restoration art or as merely a photomosaic | being read as generic chatbot-for-oral-history project |
| Main output | Open Forum position paper | full Research Paper framework |

---

## 2. Required work before AI & SOCIETY submission

| Task | Open Forum | Research Paper | Priority | Status |
|---|---:|---:|---:|---|
| Double-blind anonymisation | required | required | high | pending final pass |
| Replace project/repo identifiers where needed | required | required | high | partially done; manuscript still contains project-specific titles intentionally for working draft |
| Verify all external factual claims | required | required | high | improved; final line-level check pending |
| Align technical description with running code | required | not central | high | complete: 6-D descriptor, L2 NN, 24px tiles, reuse limit, active cap |
| Make source-contribution cap active | required | not central | high | runtime fixed in API/CLI; frontend label still needs UI polish |
| Strengthen references for Germano, Fontes, Parque de la Memoria, Traverso, Urruzola | required | optional unless cited | high | improved with stronger bibliography; Urruzola still relies mainly on Dodecá/exhibition documentation |
| Add 3-4 figures | required | required | high | complete: 4 Open Forum figures + 4 Research Paper figures |
| Add concrete prototype numbers | useful | not needed | medium | still pending; add if current run data is available |
| Expand governance architecture | not central | required | high | improved in Research Paper draft |
| Add evaluation method | concise | detailed | high | improved; still needs final methodological specificity |
| Check overlap with IBERAMIA paper | low risk | high risk | high | Research Paper now explicitly states extension beyond earlier conference paper |
| Convert references to Springer style | required | required | medium | pending |
| Final word count | required | required | medium | pending |

---

## 3. Figure status

### Open Forum paper figures

| Figure | File | Purpose | Status |
|---|---|---|---|
| Figure 1. Triptych diagram | `doc/writings/figures/open-forum-fig1-triptych.svg` | shows people/place/search structure | added and referenced |
| Figure 2. Stage 1 data flow | `doc/writings/figures/open-forum-fig2-stage1-data-flow.svg` | shows prototype accountability | added and referenced; should be updated visually to include 6-D descriptor and active cap |
| Figure 3. Process-video sequence | `doc/writings/figures/open-forum-fig3-process-video.svg` | shows search before selection | added and referenced |
| Figure 4. Ethics/provenance model | `doc/writings/figures/open-forum-fig4-ethics-provenance.svg` | shows review and exclusion rules | added and referenced |

### Research Paper figures

| Figure | File | Purpose | Status |
|---|---|---|---|
| Figure 1. System architecture | `doc/writings/figures/research-paper-fig1-system-architecture.svg` | gives research-paper technical substance | added and referenced |
| Figure 2. Conversational pipeline | `doc/writings/figures/research-paper-fig2-conversational-pipeline.svg` | shows method | added and referenced |
| Figure 3. Layered access model | `doc/writings/figures/research-paper-fig3-layered-access.svg` | makes governance legible | added and referenced; should include non-release by default in the final version |
| Figure 4. Record transformation provenance | `doc/writings/figures/research-paper-fig4-record-transformation.svg` | shows archival accountability | added and referenced |

---

## 4. Source audit for AI & SOCIETY pair

| Claim / reference area | Current source status | Risk | Action |
|---|---|---|---|
| AI & SOCIETY CFP categories and scope | CFP URL retained | low | confirm instructions at submission time |
| Uruguay dictatorship 1973-1985 | currently supported by human-rights/public-memory sources; should add one scholarly history source if space allows | medium | add scholarly history source before final submission |
| Madres y Familiares | URL retained | low | retain |
| Secretaría de Derechos Humanos para el Pasado Reciente | URL retained | low | retain |
| Sitios de Memoria Uruguay | URL retained | low | retain |
| URCDP Resolution 30/020 / biometric DPIA | URL retained | low | retain; verify legal wording before submission |
| Siluetazo | Longoni and Bruzzone | low | retain |
| Brodsky, *Buena Memoria* | book citation retained | low | retain |
| Germano, *Ausencias* | replaced placeholder with book citation | medium | confirm publisher/year/edition before submission |
| Traverso bicycles | strengthened with *The Disappeared / Los Desaparecidos* and Romero catalogue chapter | low/medium | retain; optionally add Hite if discussing wider memorial politics |
| Parque de la Memoria | placeholder replaced with institutional work description + Hite context | medium | add exact institutional page or catalogue if available |
| Claudia Fontes, *Reconstrucción del retrato de Pablo Míguez* | placeholder replaced with public artwork citation | medium | confirm exact catalogue/institutional page before final submission |
| Urruzola, *Álbum de memoria* | Dodecá source retained; reframed as exhibition documentation | medium | still worth improving if a catalogue or artist text is located |
| Responsible AI / RRI | Dignum; Stilgoe/Owen/Macnaghten | low | retain in Research Paper |
| Archive theory | Derrida, Taylor, Caswell, Jelin | low | retain; add Trouillot or Hartman only if needed |
| Postmemory | Hirsch | low | optional in Open Forum; useful in broader memory paper |

---

## 5. Summer manuscript portfolio

| Rank | Manuscript | Primary venue | Backup venues | Source material | Distinct mechanism | Status |
|---:|---|---|---|---|---|---|
| 1 | **Against Restoration** | AI & SOCIETY special collection, Open Forum | AI & SOCIETY regular issue | computational memorial triptych | refusal of restoration; crude matcher as ethics | revised draft with figures and corrected method |
| 2 | **Incomplete Reconstruction** | AI & SOCIETY special collection, Research Paper | Memory Studies; International Journal of Heritage Studies; Digital Scholarship in the Humanities | collective memory archive | conversational AI governance; non-release by default | revised draft with figures |
| 3 | **BatLLM and Situated AI Literacy** | Computers and Education: Artificial Intelligence | International Journal of Artificial Intelligence in Education; AI & Society; CHI/CSCW work-in-progress if empirical data matures | BatLLM, CICEA, UDELAR course/workshops | game-based AI literacy, prompt behaviour, cross-cultural pedagogy | promoted from secondary to first-wave paper because grant files define protocols, workshops, and publication targets |
| 4 | **audio_scripter: Real-Time Scriptable DSP as Digital Lutherie** | Organised Sound | Computer Music Journal; JNMR | audio_scripter repo; music/software practice | real-time scriptable DSP | not started here |
| 5 | **From Media Appropriation to AI Appropriation** | Leonardo | Digital Creativity; AI & SOCIETY | PhD/MSc + current AI work | thesis-derived theory | not started here |
| 6 | **Visualizing the Unphotographed Past** | Digital Humanities Quarterly | Leonardo; Memory Studies; AI & SOCIETY; Journal of Artistic Research | Paso de Morlán | source-conditioned visual hypotheses under archival absence | promoted as separate digital-humanities / AI-historical-reconstruction paper |
| 7 | **Algorithmic Postmemory** | Memory Studies | AI & SOCIETY; Visual Studies | *Montevideo, 1983* | childhood memory + generative reconstruction | not started here |
| 8 | **Synthetic Speech and Imperial Ventriloquism** | Third Text | Convergence; AI & SOCIETY; Leonardo | *Ave Imperator* | testimony redistributed through political speech | not started here |
| 9 | **Speculative Ruins** | JSTA | Digital Creativity; Leonardo | *Abandoned Fictions* / *Abandoned Future* | generative developmental memory | not started here |
| 10 | **The User-Programmer Continuum after Generative AI** | Digital Creativity | AI & SOCIETY; Leonardo | PhD/MSc + BatLLM + code generation | technical agency after prompting | not started here |
| 11 | **Temperamento** | JNMR | Organised Sound; Leonardo Music Journal | Temperamento project | musical syntax as computation | not started here |
| 12 | **Statistical Sovereignty** | AI & SOCIETY regular issue | Big Data & Society; Digital Creativity | National Average | averaging as political representation | draft elsewhere |
| 13 | **Reactivating the Avant-Garde** | Leonardo | JSTA; Digital Creativity | *Hommage Numérique* | AI and abstract cinema lineage | not started here |
| 14 | **Failure as Research Method** | Organised Sound | Digital Creativity | LLM-r | failed natural-language DAW control | not started here |
| 15 | **Silence as Algorithmic Summary** | Convergence | AI & SOCIETY; Digital Creativity | *The Cruel Continuity* | political speech reduced by algorithmic deletion | not started here |
| 16 | **Recording as Research Environment** | JAR | Organised Sound; Contemporary Music Review | large music archive | unfinished recordings as research corpus | not started here |
| 17 | **Bioart, Melanin, and the Biological Residue of Race** | Leonardo | Third Text | *If This Is a Man* | bioart and racial classification critique | not started here |
| 18 | **Synthetic Exhibition as Archive and Lie** | JAR | Leonardo; Digital Creativity; Curator | *Liminal Exhibitions* | generated exhibition documentation and curatorial fiction | second-wave |
| 19 | **Place as Subject-Making Machine** | Literary Geographies | Memory Studies; Cultural Geographies | *Liviano Gurméndez* | fiction as research into place, class, provincial repetition | second-wave, lower priority |
| 20 | **Pain, Biochemistry, and Visualisation** | Leonardo | BioSocieties; JSTA | *Vail of Tears* | scientific-artistic collaboration around tears/pain | wait until project matures |
| 21 | **Physarum, Performance, and Visual Instrument Design** | Digital Creativity | Leonardo; JSTA | *Mold* | Physarum-inspired live-cinema system and performance tool | second-wave |

### Rationale for added and promoted items

The grant and report files show that the portfolio is broader than AI-memory. The final report from the 2024-2025 project is especially important because it records an ethical change: after confronting anonymity, ownership/control, and integrity problems, the project did not publicly release the anonymised testimony dataset or the interactive prototype source code. The Research Paper should make that change central rather than accidental.

The PFH and CHA materials justify promoting BatLLM. They frame it not merely as a software spin-off but as a research platform for AI literacy, cognitive/psychological studies of LLM interaction, bilingual pedagogy, and cross-cultural collaboration with UDELAR/CICEA. The Paso de Morlán materials justify a separate paper on AI historical reconstruction under archival absence, distinct from the disappeared/conversational-memory manuscripts.

---

## 6. Anti-overlap and anti-self-plagiarism matrix

| Paper | Must not reuse from | Safe reuse | Required novelty |
|---|---|---|---|
| Against Restoration | IBERAMIA collective-memory paper; Research Paper draft | historical context, project concern, anonymised prior citation | artwork triptych, computational memorial imagery, refusal framework, concrete crude matcher |
| Incomplete Reconstruction | IBERAMIA collective-memory paper | project origin, collaborators, broad motivation | governance architecture, conversational pipeline, access model, non-release by default, evaluation framework |
| BatLLM and Situated AI Literacy | Demokritos; Collective Memories proposals | AI-literacy motivation; Uruguay collaboration | empirical/pedagogical study of gameplay, prompt histories, learning outcomes |
| Visualizing the Unphotographed Past | Against Restoration; Incomplete Reconstruction | archival absence / responsible AI language | Paso de Morlán case, co-creation, visual hypotheses, model cards, multimodal conditioning |
| Media Appropriation to AI Appropriation | PhD/MSc; 2016 media appropriation article | concepts and genealogy with citation | AI-era reformulation; new objects; no reused prose |
| User-Programmer Continuum after Generative AI | PhD; ISEA/HCI writings | conceptual continuity | prompting, code generation, BatLLM, audio_scripter, Demokritos |
| Algorithmic Postmemory | Open Forum and Research Paper | Uruguay dictatorship context | personal childhood memory, generative film, postmemory theory |
| Ave Imperator paper | Smile, Homs, Gaza writings | broad political-media practice | synthetic speech, testimony, imperial ventriloquism |
| National Average | Ave Imperator; Abandoned Future | political representation concern | statistical aggregation and national-symbol averaging |
| audio_scripter paper | Temperamento; LLM-r | digital lutherie / media appropriation ideas | real-time scriptable DSP, plugin design, scripting practice |
| LLM-r failure paper | audio_scripter paper | music-software context | failure, safety workflow, DAW control architecture |
| Temperamento | audio_scripter | music/computation relation | formal language design, harmony as opcode space |
| Liminal Exhibitions | Hommage Numérique; generative AI image papers | AI art and documentation concern | synthetic exhibition as institutional/curatorial fiction |
| Vail of Tears | If This Is a Man | bioart/science-art trajectory | biochemical analysis of tears and pain visualisation |
| Liviano Gurméndez | Montevideo 1983; Reflections on Displacement | Uruguay/place/memory concerns | literary form and place-generated subjectivity |
| Mold | Ribbons/audio_scripter | visual instrument lineage | Physarum-inspired live-cinema system and performance tool |

### Self-plagiarism rule

Do not reuse paragraphs. Reuse concepts only with citation. Each paper must change at least three of the following five elements: object, method, corpus, theoretical frame, conclusion.

---

## 7. Drafting order

| Phase | Manuscripts | Goal |
|---|---|---|
| Phase 1 | AI & SOCIETY Open Forum; AI & SOCIETY Research Paper | complete, anonymise, add figures, submit |
| Phase 2 | BatLLM; audio_scripter; Media Appropriation to AI Appropriation | diversify beyond disappeared/AI-memory while keeping venue prestige |
| Phase 3 | Paso de Morlán; Montevideo 1983; Ave Imperator | produce one digital-humanities reconstruction paper and two artwork-specific political-memory papers |
| Phase 4 | Abandoned Future; User-Programmer Continuum; Temperamento; National Average | thesis-derived and technical/conceptual papers |
| Phase 5 | Hommage Numérique; LLM-r; Cruel Continuity; Recording Archive; Bioart | second-wave manuscripts |
| Phase 6 | Liminal Exhibitions; Vail of Tears; Liviano Gurméndez; Mold | develop once objects are mature enough or a precise CFP appears |

---

## 8. Review checklist before each submission

| Check | Question | Pass/Fail |
|---|---|---|
| Venue fit | Does the manuscript answer the venue's actual scope, not just its title? |  |
| Object clarity | Is the main object/corpus/tool/artwork named within the first page? |  |
| Argument clarity | Can the central claim be stated in one sentence? |  |
| Difference from prior work | Is the contribution visibly different from previous conference papers? |  |
| Source strength | Are historical and legal claims supported by authoritative sources? |  |
| Code/prose alignment | Does the manuscript accurately describe the running implementation? |  |
| Self-citation handling | Are prior works cited or anonymised correctly? |  |
| Double-blind compliance | Are project URLs, repo names, authorial clues, and acknowledgements removed where needed? |  |
| Ethics | Are privacy, consent, participant/source risks, and non-release decisions discussed concretely? |  |
| Figures | Do figures clarify method rather than decorate? |  |
| Style | Is the prose rigorous, direct, and not overclaiming? |  |

---

## 9. Immediate next actions

1. Run final double-blind pass on both AI & SOCIETY manuscripts.
2. Convert references to the journal's required style.
3. Add exact prototype numbers to the Open Forum paper if current run logs are stable.
4. Generate one test sidecar and confirm the active 240-tile per-source cap appears in settings.
5. Update Open Forum Figure 2 to show the 6-D descriptor, L2 NN matcher, reuse limit, and source cap.
6. Add one scholarly Uruguay dictatorship/history source to each manuscript.
7. Confirm Fontes/Parque/Urruzola bibliographic details against catalogues or institutional pages.
8. Check the Research Paper against the IBERAMIA paper for direct phrase reuse and structural overlap.
9. Decide whether to submit both AI & SOCIETY papers simultaneously or stagger them by a few days.
10. Patch the frontend label so `0` no longer appears as “unlimited”; runtime is already capped, but the UI text should match.
