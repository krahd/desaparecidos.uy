# Summer Publication Plan — Revised

*Coordinating document for a high-output summer without lowering venue ambition. This revision replaces the prior plan. It adds four instruments the previous version lacked: a **thesis ledger** (the real anti-self-plagiarism control), a **venue map with prestige/speed tiers**, a **cluster + parallelization model** for throughput, and a **built-ness ranking** grounded in the actual state of the code and the artworks.*

---

## 0. What changed in this revision

1. **Anti-self-plagiarism is now thesis-based, not corpus-based.** Prose reuse is not the exposure — argument recurrence is. Each core thesis gets one *home* paper; everything else cites and defers (§3).
2. **Throughput is reframed.** The binding constraint is review latency and collision risk, not writing speed. The engine is *parallelize across clusters, stagger within them, never two simultaneous submissions to one journal* (§4, §10).
3. **Built-ness drives sequencing.** The codebase audit confirms the imagery system is real and the conversational system is unbuilt; lead every cluster with its most-built piece (§5).
4. **Venue corrections.** *Leonardo Music Journal* is defunct (removed). *Big Data & Society* promoted to primary for National Average. *AI and Ethics* (Springer) added as a fast-credible alternative (§6, §12).
5. **The two AI & SOCIETY papers are decoupled.** Open Forum goes to the collection alone; the Research Paper is held or rerouted until it has a system or is reframed (§7).
6. **Memorial-art sources are verified.** All five prior placeholders now have authoritative sources (§8).
7. **Repo-state update (2026-06-21, §18).** Both repos cloned. desaparecidos.uy is now a full built triptych on a real sourced corpus (cap=1 resolves the dispersal claim; conversational system still absent). **3bs (The Three Body Solution)** added — a shipped generative MIDI instrument, new cluster-B lead.

---

## 1. Governing principle

The two goals — *no self-plagiarism* and *most publications at the best venues* — partially conflict. The first pushes toward fewer, sharply distinct papers; the second toward more. They reconcile only if the metric stops being **submissions** and becomes **accepted papers at good venues that do not trip an overlap flag or dilute reputation.** Under that metric, more output comes from (a) merging the weakest slices into stronger papers and (b) running many non-colliding tracks in parallel — not from firing fifteen thin slices at once.

Each manuscript must still have a distinct **object, mechanism, argument, and readership.** Speed is never a reason to choose a weak venue.

---

## 2. Clusters

The portfolio sorts into seven thematic clusters. Papers in *different* clusters do not compete for reviewers or trip overlap flags and may be in review simultaneously. Papers in the *same* cluster must be staggered.

| Cluster | Theme | Papers | Realized works feeding it |
|---|---|---|---|
| **A** | Memory & the disappeared | Against Restoration; Incomplete Reconstruction; Algorithmic Postmemory; (Paso de Morlán); (framework — held) | desaparecidos.uy; **Nibia** (2010); Montevideo 1983; **Memoirs of the Blind** (2018) |
| **B** | Music, sound & digital lutherie | **3bs (The Three Body Solution)**; audio_scripter; Temperamento; LLM-r; Recording as Research Environment | **3bs** (shipped C++ AU/VST3/standalone, ~6.7k LOC); **YARMI** (NIME'09); **Critical Point** (CHI'10); **5500** (NIME'16); Improvisatio; Face Study |
| **C** | PhD-derived theory / technical agency | Media Appropriation → AI Appropriation; User-Programmer Continuum | PhD thesis; **Pushing Back on Colonization** (IEEE CG&A'21); Facing Interaction |
| **D** | Political media, violence & spectacle | Ave Imperator; Cruel Continuity; **+ consolidated political-violence paper (new)** | Ave Imperator; Cruel Continuity; **Smile** (Gaza); **HOMS** (Syria); **5500** (migration); **Be Water** (HK); Two Systems |
| **E** | Speculative / generative reconstruction | Speculative Ruins; Hommage Numérique | Abandoned Future/Fictions; Hommage Numérique; Estudio Generativo #3 |
| **F** | Statistical representation | National Average (Statistical Sovereignty) | National Average; Poem Race |
| **G** | Bioart & the body | If This Is a Man; Vail of Tears; Mold; **+ body-as-apparatus paper (new)** | If This Is a Man; Vail of Tears; Mold; **Ekphrasis**; **Brain Portraits**; **5500**; Be Water |

---

## 3. Thesis ledger — the anti-self-plagiarism backbone

The exposure is **argument recurrence**, not copied prose. Each thesis below has exactly one **home** paper that develops it. Every other paper that touches it states it in one sentence, cites the home paper, and proceeds to its own contribution. This is stricter than "change three of five elements" because it pins the argument, which is the thing that actually leaks across venues.

| # | Recurring thesis | Home paper | Papers that must cite-and-defer |
|---|---|---|---|
| T1 | AI should refuse synthetic completion and **expose incompleteness**, not restore | **Against Restoration** | Incomplete Reconstruction; Algorithmic Postmemory; Speculative Ruins; Paso de Morlán; Memory framework |
| T2 | The **representation operation is itself political** — the chosen space produces the "truth" | **National Average** | Ave Imperator; the memorial-imagery work |
| T3 | **Media appropriation → AI appropriation**; the user-programmer continuum; explicitation | **Media Appropriation → AI Appropriation** | User-Programmer Continuum; BatLLM; audio_scripter |
| T4 | **Synthetic / redistributed political speech** and visibility asymmetry | **Ave Imperator** | Cruel Continuity |
| T5 | **Digital lutherie / executable musical thought** | **audio_scripter** | Temperamento; LLM-r; Recording as Research Environment |

**Self-plagiarism rule (retained, sharpened):** Do not reuse paragraphs. Reuse concepts only with citation. Beyond a thesis's home paper, no paper may re-argue it — a single cited sentence is the ceiling. Each paper must change at least three of: object, method, corpus, theoretical frame, conclusion.

---

## 4. Throughput engine

1. **Parallelize across clusters.** Keep one paper in review from each of A–G at once — seven parallel tracks that cannot collide. This is the real multiplier.
2. **Stagger within a cluster.** Never two cluster-mates in review in the same venue-adjacent space simultaneously; submit one, let it clear first round, then send the next elsewhere.
3. **Never two simultaneous submissions to the same journal.** Several papers list Leonardo or Third Text; do not stack them. Route to backups or wait.
4. **Lead each cluster with its most-built piece.** Built work survives first round; proposals invite the "what did you actually do" desk-check.
5. **Front-load scaffolding papers** (Media Appropriation; National Average). Once published they become citable anchors that strengthen every later paper in their cluster and make the synthesis/framework papers credible.

---

## 5. Portfolio — re-ranked by built-ness and cluster

**Built legend:** ● working system / repo · ◐ artwork realized & exhibited · ○ proposal only.

| # | Paper (working title) | Cluster | Built | Primary venue | Backups | Status / decision |
|---:|---|:--:|:--:|---|---|---|
| 1 | **Against Restoration** (computational memorial imagery; refusal) | A | ● | **AI & SOCIETY** (Open Forum, this collection) | AI & SOCIETY regular | Lead paper. **Full triptych now built** (10.7k LOC), real sourced corpus, cap=1 resolves the dispersal claim. Submission-ready bar figures (§7). |
| 2 | **Incomplete Reconstruction** (conversational archive; governance) | A | ○ | **AI and Ethics** *or* Memory Studies | — | Conversational system **still unbuilt**, but a real **197-biography corpus now exists** → pilot now feasible. Don't co-submit (§7). |
| 3 | **The Three Body Solution** (`3bs`; deterministic generative MIDI instrument from a 3-body simulation) | B | ● | **NIME** | Computer Music Journal; Organised Sound | ★ NEW. Shipped alpha (AU/VST3/standalone, ~6.7k LOC C++/JUCE/Metal). Most-built music work; new cluster-B lead. No paper yet — clean novel artifact. |
| 3b | **audio_scripter** (real-time scriptable DSP; digital lutherie) | B | ● | **Organised Sound** | Computer Music Journal; JNMR | Has a repo. Distinct object from 3bs (scripting vs physics-mapping). |
| 4 | **Media Appropriation → AI Appropriation** | C | ◐ | **Leonardo** | Digital Creativity; AI & SOCIETY | Scaffolding paper. Front-load. Home of T3. |
| 5 | **Algorithmic Postmemory** (*Montevideo, 1983*) | A | ◐ | **Memory Studies** | Visual Studies; Convergence | Keep **off** AI venues. Contribution = postmemory, not refusal. |
| 6 | **Imperial Ventriloquism** (*Ave Imperator*) | D | ◐ | **Third Text** | Convergence; AI & SOCIETY | Home of T4. Politically delicate — frame as recontextualization. |
| 7 | **Speculative Ruins** (*Abandoned Future / Fictions*) | E | ◐ | **JSTA** | Digital Creativity; Leonardo | Fast diamond-OA fit; existing relationship. |
| 8 | **User-Programmer Continuum after Generative AI** | C | ◐ | **Digital Creativity** | AI & SOCIETY; Leonardo | Keep only if object ≠ #4 (agency/labor, not aesthetics). Cross-cite #4. |
| 9 | **Temperamento** (musical syntax as computation) | B | ◐ | **JNMR** | Organised Sound; Computer Music Journal | ~~Leonardo Music Journal~~ removed (defunct). |
| 10 | **Statistical Sovereignty** (*National Average*) | F | ◐/● | **Big Data & Society** *(promoted)* | AI & SOCIETY; Digital Creativity | Home of T2. Five backends built. Scaffolding paper. |
| 11 | **Reactivating the Avant-Garde** (*Hommage Numérique*) | E | ◐ | **Leonardo** | JSTA; Digital Creativity | Frame as reactivation, not stylistic homage. |
| 12 | **Failure as Research Method** (*LLM-r*) | B | ◐ | **Organised Sound** | Digital Creativity; Computer Music Journal | Failed NL DAW control as method. |
| 13 | **Silence as Algorithmic Summary** (*The Cruel Continuity*) | D | ◐ | **Convergence** | AI & SOCIETY; Digital Creativity | Take only the deletion/summarization cut of T4. |
| 14 | **Recording as Research Environment** | B | ◐ | **JAR** | Organised Sound; Contemporary Music Review | JAR = exposition format (media-rich, non-linear). |
| 15 | **Bioart, Melanin, and Race** (*If This Is a Man*) | G | ◐ | **Third Text** | Leonardo | Pair with Vail of Tears / Mold to anchor the cluster. |

### Secondary set (from the broader file review — specifics lower-confidence pending source files)

| Paper | Cluster | Primary venue | Status |
|---|:--:|---|---|
| **Responsible AI in Human-Rights Memory Work: A Framework** | A | AI & SOCIETY / AI and Ethics | **Held.** Re-runs T1 and overlaps #1/#2. Write as a *synthesis after* the case studies land. |
| **Synthetic Exhibition as Archive and Lie** (*Liminal Exhibitions*) | — | Convergence; Leonardo | Candidate; distinct object (curatorial AI). |
| **Place as Subject-Making Machine** (*Liviano Gurméndez*) | — | Leonardo; Third Text | Candidate. |
| **Pain, Biochemistry, Visualisation** (*Vail of Tears*) | G | Leonardo | Bioart cluster; distinct object from #15. |
| **Physarum, Performance, Instrument Design** (*Mold*) | G/B | Leonardo; Organised Sound | Candidate. |

---

## 6. Venue map — the prestige/speed barbell

There is a real tradeoff. Anchor a few flagship submissions at slow, selective venues and accept the latency; fill the rest of the pipeline with fast-credible venues. Sending everything to flagships yields two papers in eighteen months; sending everything to fast OA caps the prestige ceiling.

| Tier | Venues | Use for |
|---|---|---|
| **Flagship — selective, slow** | Leonardo (MIT); Third Text; Memory Studies (SAGE); Organised Sound (Cambridge); Computer Music Journal (MIT); Big Data & Society (SAGE) | Anchor papers; scaffolding papers worth the wait |
| **Fast — credible, quicker turnaround** | AI & SOCIETY (≈3-day first decision; IF 4.7); JSTA (diamond OA, Scopus, existing relationship); AI and Ethics (Springer, OA, double-blind); Digital Creativity (T&F); Convergence (SAGE); JNMR (T&F) | Pipeline throughput; practice-based pieces |
| **Artistic-research / special format** | JAR (exposition format) | Recording as Research Environment; a full National Average exposition later |

**Corrections baked in:** *Leonardo Music Journal* ceased after Vol. 30 (Dec 2020) and was folded into *Leonardo* (leonardo.info) — removed everywhere. *Big Data & Society* is the exact fit for National Average — promoted from backup to primary. *AI and Ethics* (Springer, ISSN 2730-5953; responsible-AI/regulatory/policy scope; double-blind) added as a non-colliding home for the conversational Research Paper or the memory framework, since the Open Forum already occupies AI & SOCIETY.

---

## 7. Immediate AI & SOCIETY work (per-paper status)

### #1 Against Restoration — lead paper, nearly submission-ready

The imagery system is now **fully implemented as a three-artwork triptych** (≈10,675 LOC, latest commit 2026-06-21): **Todos somos familiares** (approved face-region fragments), **Están en todas partes** (place fragments), and **Seguimos buscando** (street-level traversal via a Mapillary adapter, GeoJSON/GPX/autonomous route authoring, deterministic rendering) — plus a bounded crawler, stricter OpenCV gating, deterministic matcher, manifest-driven review states, a FastAPI backend, and a React GUI. It runs on a **real, sourced corpus**: 204 disappeared-person records, 197 Sitios de Memoria biographies, 202 reviewed portraits with per-field source attribution — and it explicitly records two portraits it **could not find** (`camuyrano-bottini-mario`, `gadea-hernandez-liborio`) rather than fabricating them, which is the designed-incompletion/archival-humility thesis made concrete. The method section can be made precise:

- **Fragments:** 24×24-pixel, non-overlapping (stride = fragment size; min 8 px enforced).
- **Descriptor:** a deliberately small **6-dimensional** per-patch vector — mean RGB (3), luminance contrast as std of luminance (1), mean horizontal/vertical luminance-gradient energy (2).
- **Matching:** L2 (Euclidean) nearest-neighbour over the descriptor matrix (argmin).
- **Limits:** up to 240 fragments per source (evenly sampled); each fragment reusable up to 8×; deterministic (fixed seed, seeded per target).
- **CV place-gate:** rejects images below 320 px, outside aspect 0.4–2.6, below a texture floor, above a 2% face fraction, and outside edge-density / unique-pixel-ratio bounds — i.e., screens out logos, banners, flat graphics, face-dominated shots, and noise, as claimed.

**Honesty corrections — one now resolved by the code, one still standing:**
1. **(Still open)** The matching-method list overclaims — it names "perceptual similarity, learned embeddings," none of which are built. The matcher is still the hand-designed **6-D descriptor + L2 nearest-neighbour**; the only "perceptual" thing in the repo is a `perceptual_hash` used for *deduplication*, not matching. State the descriptor that exists; mention embeddings only as a designed extension. Reviewers may glance at the now-public repo.
2. **(Resolved — update the paper to match)** The per-source contribution cap is no longer off by default: `DEFAULT_MAX_CONTRIBUTION_PER_SOURCE = 1`, i.e. each source image contributes **at most one fragment** by default — the maximal "dispersed field" guarantee. The paper's claim that the portrait is composed from many sources rather than a disguised single-source transform is now literally true in the running default. Describe the cap=1 default explicitly; it is now a strength, not a liability.

**Reframe (an upgrade, not a fix):** the crudeness *is* the ethics. A 6-D descriptor and 24-px tiles cannot smooth into photorealism — "designed incompletion" is enforced at the algorithmic level, not policed by the artist. Owning the photomosaic coarseness pre-empts the "this is just a photomosaic" objection by making it the point.

**Figures:** use **real** screenshots and generated output from the running frontend — a reconstructed portrait visibly resolving into 24-px tiles proves the prototype in one image. Do not ship schematic SVGs.

### #2 Incomplete Reconstruction — hold or reroute

A grep across all ≈10,675 lines for any LLM/chat/prompt/consent/testimony token still returns nothing: **the conversational system does not exist in code**, even after the repo more than doubled. The imagery side grew; the conversational side did not. The IBERAMIA 2024 paper is a 4-page concept note (6 references) — the seed of this project. The Research Paper's novelty (architecture, governance, seven-stage pipeline, evaluation, the capture-vs-extraction distinction) is all absent from IBERAMIA, so the expansion is defensible — but the paper is all-proposal while the *adjacent* paper now ships a real, full triptych, which sharpens the contrast a reviewer will draw. **However**, the repo now holds a real, sourced **197-biography text corpus** (Sitios de Memoria), currently not consumed by generation pending an editorial review and display-length policy — which means a minimal conversational pilot is now materially more feasible: the data exists, only the conversational layer is missing.

- **Decision:** do **not** co-submit to the collection. Either (a) build a minimal pilot — a handful of real sessions, a working governance schema, one redaction worked example — and submit as a Research Paper, or (b) reframe as a framework/position paper and route to **AI and Ethics** or **Memory Studies**, staggered behind #1.
- **Missing reference (conspicuous):** *New Dimensions in Testimony* (USC Shoah Foundation / ICT) — an AI-mediated conversational interface to recorded survivor testimony, the closest existing analogue. Add it, plus the Shoah Foundation Visual History Archive, as the comparative baseline.
- **Double-blind:** cite IBERAMIA in third person ("[29]"), not "Author"; strip the named prior-work blocks and the project name; accept that anonymity is best-effort given the project's specificity.

---

## 8. Source audit — memorial-art references (verified this round)

All five prior placeholders now have authoritative sources. Convert to Springer style at submission.

| Reference | Verified source(s) |
|---|---|
| **Fontes**, *Reconstrucción del retrato de Pablo Míguez* (Parque de la Memoria, 1999–2010) | Artist site (claudiafontes.com); Museo Moderno; scholarly essay by Vikki Bell |
| **Germano**, *Ausencias* (2006) | Artist site (gustavogermano.com); peer-reviewed article in *photographies* 9(1), 2016; Van Dembroucke (2010), *InTensions* |
| **Traverso**, bicycle stencils, Rosario (350 bicycles, from 24 March 2001) | Museo de la Memoria, Rosario (museodelamemoria.gob.ar); SeDiCI/UNLP. *Do not assert "Las bicicletas de Rosario" as a formal title.* |
| **Parque de la Memoria** (Monumento a las Víctimas del Terrorismo de Estado) | parquedelamemoria.org.ar |
| **Urruzola**, *Álbum de memoria* (Fac. de Arquitectura, UdelaR, 2010) | Centro de Fotografía de Montevideo (cdf.montevideo.gub.uy); retain Dodecá/Oroño for the mosaic-of-faces description |

Stable, already-cited sources retained: Siluetazo (Longoni & Bruzzone); Brodsky, *Buena Memoria*; Madres y Familiares; Secretaría de DDHH para el Pasado Reciente; Sitios de Memoria Uruguay; URCDP Resolution 30/020 (verify wording).

---

## 9. Figures

- **Against Restoration:** real frontend screenshots + generated output (data flow; process-video stills; a tiled reconstruction; the ethics/provenance gate). Schematic SVGs are unnecessary now that the system runs.
- **Incomplete Reconstruction:** architecture, seven-stage pipeline, layered access model, record-transformation provenance — schematic is acceptable here precisely because the system is a proposal; do not imply a running build.

---

## 10. Submission order — collision-free waves

**Wave 1 (launch now — one per cluster, distinct journals, lead with built):**
- A → **Against Restoration** → AI & SOCIETY
- B → **audio_scripter** → Organised Sound
- C → **Media Appropriation → AI Appropriation** → Leonardo
- F → **National Average** → Big Data & Society
- D → **Ave Imperator** → Third Text
- E → **Speculative Ruins** → JSTA

**Wave 2 (after Wave 1 clears first round — stagger within clusters, keep journals distinct):**
- A → Algorithmic Postmemory → Memory Studies
- B → Temperamento → JNMR
- C → User-Programmer Continuum → Digital Creativity
- D → Cruel Continuity → Convergence
- E → Hommage Numérique → Leonardo (only once #4 has moved through)
- G → If This Is a Man → Third Text (only once #6 has moved through) *or* Leonardo

**Wave 3:**
- A → Incomplete Reconstruction (post-pilot/reframe) → AI and Ethics or Memory Studies
- B → LLM-r → Organised Sound; Recording as Research Environment → JAR
- G → Vail of Tears; Mold
- A → Memory framework (synthesis, once case studies are published)

---

## 11. Pre-submission review checklist

| Check | Question |
|---|---|
| Venue fit | Does it answer the venue's actual scope, not just its title? |
| Object clarity | Is the object/corpus/tool/artwork named on the first page? |
| Argument clarity | Can the central claim be stated in one sentence? |
| Thesis ledger | Is every borrowed thesis cited to its home paper, not re-argued? |
| Built-ness honesty | Does the paper claim only what the code/artwork actually does? |
| Source strength | Are historical and legal claims authoritatively sourced? |
| Double-blind | Are repo names, project identifiers, prior-work blocks, and acknowledgements removed where required? |
| Self-citation | Prior work cited in third person, not "Author"? |
| Ethics | Privacy, consent, and source risks discussed concretely? |
| Figures | Do figures clarify method rather than decorate? |
| No collision | Is any cluster-mate or same-journal paper already in review? |
| Style | Reference list in the venue's required style? |

---

## 12. Verification log (this round)

| Fact | Status |
|---|---|
| AI & SOCIETY Open Forum ≤ 8,000 words | **Confirmed** (CFP / guidelines) |
| AI & SOCIETY Research/Original Article ≤ 10,000 words | **Unconfirmed** — GPT's claim; verify at the detailed CFP (link.springer.com/journal/146/updates/27850936) before sizing the Research Paper |
| Special collection deadline 30 June 2026; IF 4.7 (2024); median first decision 3 days; guest editors Farina, Stahl, Webb (Nottingham) | **Confirmed** |
| Leonardo Music Journal status | **Confirmed defunct** (ceased Vol. 30, Dec 2020; folded into Leonardo) — removed |
| AI and Ethics (Springer, ISSN 2730-5953) — active, double-blind, responsible-AI/policy scope | **Confirmed** — added as fast-credible alternative |
| desaparecidos.uy codebase: imagery built (~4,120 LOC + React), conversational unbuilt | **Confirmed** by direct inspection |

**Open items:** confirm Springer reference style for AI & SOCIETY; confirm current submission windows for Memory Studies, Third Text, and JAR; resolve the BatLLM dual-submission / double-blind question before any IBERAMIA 2026 use; verify URCDP Resolution 30/020 wording.

---

## 13. Immediate next actions

1. Lock the **thesis ledger** (§3) — the anti-self-plagiarism backbone.
2. Finalize **Against Restoration**: insert the real method numbers, apply the two honesty corrections, add real figures, run the double-blind pass — then submit to the collection **alone**.
3. **Decouple Incomplete Reconstruction** from the collection; decide pilot-vs-reframe; add the *New Dimensions in Testimony* baseline.
4. Open **audio_scripter** as the second parallel track (Organised Sound).
5. Apply venue corrections: drop LMJ, promote Big Data & Society, add AI and Ethics.
6. Resolve the **two-theory-papers** split (§5, #4/#8) — keep only with genuinely distinct objects.
7. Convert all five memorial-art references to Springer style (§8).
8. Launch the rest of **Wave 1** (§10).

---

## 14. Source-works inventory (laurenzo.net + published record)

The realized practice that feeds the portfolio. **Role:** *anchor* = the paper is built on it; *precedent* = your own prior work to cite for lineage/grounding; *example/contrast* = supporting case. **Double-blind note:** for the AI & SOCIETY submissions, cite these third-person ("a prior installation [x]"), never as "the author's" — the autobiographical grounding is strong but compounds de-anonymization risk (see §7).

| Work (year) | Cluster | Feeds | Role | Note |
|---|:--:|---|:--:|---|
| **desaparecidos.uy / Están en todas partes** (2024–25) | A | Against Restoration | anchor | Built prototype (~4,120 LOC + React). |
| **Nibia** (2010) | A | Against Restoration; Algorithmic Postmemory | precedent | Burning projected portrait of Nibia Sabalsagaray that *refuses erasure* — the erasure/completion inverse of the new work. Cite ISEA 2011 + PhD thesis. Museo de la Memoria. |
| **Montevideo, 1983** (2024) | A | Algorithmic Postmemory | anchor | Generative non-documentary reconstruction; postmemory (Hirsch). |
| **Memoirs of the Blind** (2018) | A / methods | Against Restoration; User-Programmer | precedent | Capture-process-**don't-store** face work; *published SIGGRAPH Asia 2018 (ACM)*. Derrida ("self-portrait and other ruins") + Virilio. Grounds the privacy/non-identification framework. |
| **Ave Imperator** (2024) | D | Imperial Ventriloquism | anchor | Redistributed political speech; victims' silencing vs leaders' double standards (Gaza). Exhibited by UNESCO Human Rights Chair, 2025. |
| **Cruel Continuity** (Harris–Trump debate) | D | Silence as Algorithmic Summary | anchor | Political speech reduced by algorithmic deletion. |
| **Smile** (2019) | D | political-violence paper | anchor/example | Gaza drone footage that plays *only while the viewer smiles* — complicity. NeurIPS Creativity 2019. |
| **HOMS** (2018) | D / E | political-violence paper | anchor/example | Homs ruins reflected into "beautiful caustics" — aestheticization of war. |
| **5500** (2015–16) | D/B/G/F | political-violence; digital-lutherie; bioart | anchor | Beethoven disrupted by nerve electrodes; 5,500 migrant deaths mapped to the sonata. *Published NIME 2016*. Multi-cluster keystone. |
| **Be Water** (2020) | D / G | political-violence; Against Restoration (contrast) | precedent/contrast | HK protests; *uses* face-tracking + remote heart-rate — the biometric capture the memorial work refuses. |
| **Two Systems** | D | political-violence paper | example | Control and representation; burning fire animation. |
| **Ekphrasis** (2018) | G | bioart/body paper | anchor/example | Scarred body on a violently stretched elastic screen; corporeity, the imperfect body. |
| **Brain Portraits** (2020) | G | bioart/body paper | example | EEG self-portraits (Muse). |
| **If This Is a Man** | G | Bioart, Melanin, Race | anchor | Race/melanin classification critique. |
| **Vail of Tears** | G | Pain/biochemistry paper | anchor | Pain visualization. |
| **Mold** (Physarum) | G/B | Physarum paper | anchor | Slime-mold performance/instrument. |
| **Hommage Numérique** | E | Reactivating the Avant-Garde | anchor | AI + abstract-cinema lineage. CVPR AI Art. |
| **Abandoned Future / Fictions** | E | Speculative Ruins | anchor | Generative industrial ruins. CVPR AI Art. |
| **Estudio Generativo #3** (2018) | E | Reactivating the Avant-Garde | precedent | Pre-2024 generative-print practice (Processing). |
| **Improvisatio** | B | audio_scripter; Temperamento | example | Composition vs improvisation; explicitation of perceptual interpretation. |
| **Face Study** | B | audio_scripter (instruments) | example | Face-as-instrument (FFT bands → face regions). |
| **YARMI** (2009) | B | audio_scripter | precedent | AR musical instrument. *Published NIME 2009*. |
| **Critical Point** (2010) | B | Recording as Research Environment | precedent | Cello + computer composition w/ Roger Dannenberg (CMU). *Published CHI EA 2010*. |
| **Poem Race** (2014) | F | National Average | example | Absurdity of ranking/objective comparison in art. |
| **Facing Interaction** (2012) | C | User-Programmer Continuum | example | Face-based interaction; Microsoft Research. |

---

## 15. Own-publications ledger (grounding)

Per the working principle that framing should rest on your own published record, not generic placeholders. Cite the relevant prior work in each paper.

| Publication | Venue / year | Grounds |
|---|---|---|
| *Decoupling and context in new media art* (PhD thesis) | PEDECIBA/UdelaR | Media Appropriation → AI Appropriation; User-Programmer Continuum (media appropriation, explicitation, perceptual cloud, interaction-as-political) |
| Media-appropriation article | JSTA 2016 | Media Appropriation → AI Appropriation |
| *Nibia and the ludic component* | ISEA 2011 | Against Restoration; Algorithmic Postmemory |
| *Interlacing Worlds: Fibres and Sensory Mediation* | ISEA 2014 | sensory mediation / materiality (supporting) |
| *Memoirs of the blind* | SIGGRAPH Asia 2018 (ACM) | Against Restoration (privacy framework) |
| *YARMI: an Augmented Reality Musical Instrument* | NIME 2009 | audio_scripter |
| *Critical point, a composition for cello and computer* | CHI EA 2010 | Recording as Research Environment |
| *5500: performance, control, and politics* | NIME 2016 | political-violence paper; digital-lutherie |
| *Designing Interfaces for Children with Motor Impairments* | SCCC 2010 (IEEE) | accessibility/HCI (peripheral) |
| *Tomás Laurenzo: Pushing Back on Colonization* | IEEE CG&A 2021 | Media Appropriation → AI Appropriation (decolonial/periphery); political-violence paper |
| *Capturing Collective Memories of the Disappeared with AI* | IBERAMIA 2024 | Incomplete Reconstruction (prior work — cite third-person) |

---

## 16. Biographical / institutional assets

For cover letters, CVs, and framing — deploy selectively per venue.

- **Broad Institute of MIT & Harvard** (visiting scientist) + **Global Community Bio Summit 2018** → grounds the **bioart cluster (G)** in a genomics-research affiliation; strong credential for *If This Is a Man* / *Vail of Tears*.
- **UNESCO Chair in Human Rights (UdelaR)** exhibited **Ave Imperator** (2025) → grounds the political-media and memory work; ties to Achugar.
- **City University of Hong Kong, School of Creative Media** (under Jeffrey Shaw), 2014–2021 → grounds the HK works (*Be Water*, *Two Systems*).
- **First place, inaugural Colorado State AI Art Competition**; work in the Town of Superior permanent collection → current GenAI-art standing.
- Exhibition/performance record: Ars Electronica, SIGGRAPH / SIGGRAPH Asia, NIME, ISEA, NeurIPS, ECCV, ICMC, Sónar+D, MUTEK, Guggenheim Bilbao, K11, MNAV, Subte, Solís Theatre.

---

## 17. New paper opportunities the works open

1. **Consolidated political-violence / spectacle paper (cluster D).** *Smile* (Gaza), *HOMS* (Syria), *Be Water* (HK), *5500* (migration), *Two Systems*, plus *Ave Imperator* and *Cruel Continuity*, form a large, coherent body: computational art, contemporary violence, spectacle, and complicity. Consolidate into **one strong survey/framework paper** (Third Text or Convergence) anchored on two or three works, leaving *Ave Imperator* and *Cruel Continuity* as their own focused papers. The distinctive throughline to foreground: **the viewer's body triggers the work** — *Smile*'s smile-to-reveal, *Memoirs*' blink-to-capture — complicity as mechanism. This is a strength to consolidate, not slice; enforce T4 (home = Ave Imperator).
2. **"Facial computer vision and its refusals" paper (cluster A / methods).** *Memoirs of the Blind* (capture-don't-store), *Be Water* (heart-rate inference), *Smile* (expression-triggered), *Face Study* (face-as-instrument), and *Están en todas partes* (fragment reconstruction refusing identification) form a decade-long body on doing CV *to faces* while refusing identification/storage. Strong Leonardo or AI & SOCIETY paper, and it reinforces Against Restoration's privacy argument by demonstrating sustained practice. Keep distinct from Against Restoration's memorial focus — this one is about method-ethics across works.
3. **Body-as-apparatus / biometric-intervention paper (cluster G).** *5500* (electrode-disrupted performance), *Be Water* (heart-rate), *Brain Portraits* (EEG), *Ekphrasis* (scarred body) → the body as both sensor and site of inscription. Pairs with the Broad Institute affiliation.
4. **5500 journal extension (low-friction, high-yield).** Already has a NIME 2016 paper; extend to Organised Sound or a music-and-politics venue with minimal new writing.

**Discipline note:** these opportunities expand the portfolio's *reach*, but they also raise within-cluster overlap (especially D). Hold each to the thesis ledger (§3) and the parallelize-across / stagger-within rule (§4): of the political-violence material, one consolidated paper plus two focused papers is the ceiling for near-term, staggered, not simultaneous.

---

## 18. Repo-state update — 2026-06-21 (both repos cloned & inspected)

Both repos are now public and were cloned directly (no upload needed).

### desaparecidos.uy (commit `aa05e9a`, "improvements")

- **More than doubled: ≈10,675 LOC.** The imagery system is now a **fully realized triptych** — *Todos somos familiares* (face-region fragments), *Están en todas partes* (place fragments), and *Seguimos buscando* (street-level traversal: Mapillary adapter, route authoring, deterministic rendering). New modules since the upload: `persons.py` (686), `traversals.py` (594), expanded `api.py` (620), `crawl.py` (927).
- **Real, sourced corpus:** 204 disappeared-person records, 197 Sitios de Memoria biographies, 202 reviewed 3:4 portraits, 321 candidates, with per-field `field_sources`/`field_source_refs`. Two portraits explicitly recorded as **not found** rather than fabricated — archival humility, operational.
- **Honesty flag #2 → resolved.** `DEFAULT_MAX_CONTRIBUTION_PER_SOURCE = 1` (one fragment per source by default = maximal dispersal). Update the paper to describe this default; the "dispersed field" claim is now literally true.
- **Honesty flag #1 → still open.** Matching is unchanged: hand-designed 6-D descriptor + L2 NN. The only "perceptual" code is a dedup `perceptual_hash`. Drop "learned embeddings" from the method.
- **Conversational system → still absent.** No LLM/chat/consent/testimony code anywhere in 10.7k LOC. The Research Paper remains held — but the new 197-biography corpus makes a minimal pilot materially more feasible (data exists; only the conversational layer is missing).
- The papers now live in-repo under `doc/writings/`, and `doc/summer-publication-plan-2.md` is a committed copy of **an earlier version of this plan** (its §2 lacks the realized-works column; no §14–§17). **This file is the current version — commit it to replace `summer-publication-plan-2.md`.**

**Net effect:** *Against Restoration* is now the clear, well-built lead — full triptych, real corpus, ethical claims embodied in the default config, recorded gaps as evidence. Ship it (after fixing flag #1 and adding real figures). Nothing here changes the decoupling of the Research Paper.

### 3bs — The Three Body Solution (commit `1213df0`)

- **A shipped (alpha) deterministic generative MIDI instrument** that maps a normalized three-body gravitational simulation to three interlocking musical voices. **~6.7k LOC C++20** (5,312 `.cpp` + 1,415 `.h`, external deps excluded), built as a JUCE core library + Logic AU MIDI effect + VST3 instrument + standalone CoreMIDI app, with a Metal HDR renderer, 24 factory presets, host-state serialization, portable `.3bs` files, automated tests, macOS CI, a `v0.1.0-alpha.1` release, and a GitHub Pages site. **No paper yet.**
- **Portfolio placement (new):** cluster **B**, and the **most-built work in it** — new cluster-B lead ahead of audio_scripter (portfolio #3). It is a **distinct object** from audio_scripter (scriptable DSP), Temperamento (musical syntax), and LLM-r (failure case), so it adds rather than cannibalizes. Cite T5 (digital-lutherie home = audio_scripter); its own contribution is *deterministic physical simulation as a reproducible, seed-stable generative-music engine* — a clean, novel, defensible thesis.
- **Venue:** **NIME** primary (exact fit, and you already publish there — YARMI'09, 5500'16), with Computer Music Journal and Organised Sound as flagship backups. Built-and-shippable means it survives first round; it's a strong Wave-1/Wave-2 candidate for cluster B.
- **Possible second cut:** the simulation→audiovisual rendering (Metal HDR, planetary cinematics) could support a separate audiovisual-performance paper, but hold to one paper unless the objects genuinely diverge (instrument vs visualization).

### Revised Wave 1 note

Cluster B can now lead with **3bs** (NIME) instead of audio_scripter, because it is more built and more novel as a single artifact; audio_scripter then staggers behind it within cluster B (different venue — Organised Sound). The six-track Wave 1 (§10) otherwise stands; swap the cluster-B slot to 3bs → NIME.
