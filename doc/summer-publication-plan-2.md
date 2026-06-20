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

---

## 1. Governing principle

The two goals — *no self-plagiarism* and *most publications at the best venues* — partially conflict. The first pushes toward fewer, sharply distinct papers; the second toward more. They reconcile only if the metric stops being **submissions** and becomes **accepted papers at good venues that do not trip an overlap flag or dilute reputation.** Under that metric, more output comes from (a) merging the weakest slices into stronger papers and (b) running many non-colliding tracks in parallel — not from firing fifteen thin slices at once.

Each manuscript must still have a distinct **object, mechanism, argument, and readership.** Speed is never a reason to choose a weak venue.

---

## 2. Clusters

The portfolio sorts into seven thematic clusters. Papers in *different* clusters do not compete for reviewers or trip overlap flags and may be in review simultaneously. Papers in the *same* cluster must be staggered.

| Cluster | Theme | Papers |
|---|---|---|
| **A** | Memory & the disappeared | Against Restoration; Incomplete Reconstruction; Algorithmic Postmemory; (Paso de Morlán); (Memory framework — held) |
| **B** | Music, sound & digital lutherie | audio_scripter; Temperamento; LLM-r (Failure as Method); Recording as Research Environment |
| **C** | PhD-derived theory / technical agency | Media Appropriation → AI Appropriation; User-Programmer Continuum |
| **D** | Political media & synthetic speech | Ave Imperator (Imperial Ventriloquism); Cruel Continuity (Silence as Summary) |
| **E** | Speculative / generative reconstruction | Speculative Ruins; Hommage Numérique (Reactivating the Avant-Garde) |
| **F** | Statistical representation | National Average (Statistical Sovereignty) |
| **G** | Bioart & the body | If This Is a Man (Melanin/Race); Vail of Tears (Pain); Mold (Physarum) |

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
| 1 | **Against Restoration** (computational memorial imagery; refusal) | A | ● | **AI & SOCIETY** (Open Forum, this collection) | AI & SOCIETY regular | Lead paper. Method + figures fixable now (§7). |
| 2 | **Incomplete Reconstruction** (conversational archive; governance) | A | ○ | **AI and Ethics** *or* Memory Studies | — | **Do not co-submit to the collection.** Build a pilot or reframe first (§7). |
| 3 | **audio_scripter** (real-time scriptable DSP; digital lutherie) | B | ● | **Organised Sound** | Computer Music Journal; JNMR | Strong second track — has a repo. Launch now. |
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

The Stage 1 imagery prototype is genuinely implemented (~4,120 LOC Python + ~1,300-line React frontend: bounded crawler, OpenCV gating, deterministic matcher, manifest-driven review states, backend API). The method section can be made concrete and credible:

- **Fragments:** 24×24-pixel, non-overlapping (stride = fragment size; min 8 px enforced).
- **Descriptor:** a deliberately small **6-dimensional** per-patch vector — mean RGB (3), luminance contrast as std of luminance (1), mean horizontal/vertical luminance-gradient energy (2).
- **Matching:** L2 (Euclidean) nearest-neighbour over the descriptor matrix (argmin).
- **Limits:** up to 240 fragments per source (evenly sampled); each fragment reusable up to 8×; deterministic (fixed seed, seeded per target).
- **CV place-gate:** rejects images below 320 px, outside aspect 0.4–2.6, below a texture floor, above a 2% face fraction, and outside edge-density / unique-pixel-ratio bounds — i.e., screens out logos, banners, flat graphics, face-dominated shots, and noise, as claimed.

**Two honesty corrections before submission:**
1. The matching-method list overclaims — it names "perceptual similarity, learned embeddings," none of which are built. State the 6-D descriptor that exists; mention embeddings only as a designed extension. Reviewers may glance at the repo.
2. The per-source contribution cap is presented as an active safeguard but is **off by default** (`max_contribution_per_source = 0` = unlimited). Only the per-fragment reuse limit (8) constrains dominance; with the cap off, one source can supply up to 240×8 = 1,920 placements — enough to fill a portrait. Either enable a real cap so the running system embodies the "dispersed field" claim, or describe the cap as available-but-optional and rest the argument on the reuse limit plus the 240-fragment ceiling.

**Reframe (an upgrade, not a fix):** the crudeness *is* the ethics. A 6-D descriptor and 24-px tiles cannot smooth into photorealism — "designed incompletion" is enforced at the algorithmic level, not policed by the artist. Owning the photomosaic coarseness pre-empts the "this is just a photomosaic" objection by making it the point.

**Figures:** use **real** screenshots and generated output from the running frontend — a reconstructed portrait visibly resolving into 24-px tiles proves the prototype in one image. Do not ship schematic SVGs.

### #2 Incomplete Reconstruction — hold or reroute

A grep across all 4,120 lines for any LLM/chat/prompt/consent/testimony token returns nothing: **the conversational system does not exist in code.** The IBERAMIA 2024 paper is a 4-page concept note (6 references) — the seed of this project. The Research Paper's novelty (architecture, governance, seven-stage pipeline, evaluation, the capture-vs-extraction distinction) is all absent from IBERAMIA, so the expansion is defensible — but the paper is currently all-proposal while the *adjacent* paper ships a real system, which is exactly the contrast a reviewer will draw.

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
