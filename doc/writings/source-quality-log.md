# Source Quality Log: AI & SOCIETY Manuscripts

## Purpose

This file records the source-quality pass for the two AI & SOCIETY manuscripts. It distinguishes sources that are ready for submission from sources that still require catalogue-level verification. It also records internal project-file evidence used for planning and for the ethical history of the manuscripts.

## Summary

| Area | Current decision | Remaining risk |
|---|---|---|
| AI & SOCIETY CFP | Keep Springer CFP URL in both manuscripts. | Low; re-check at submission. |
| Uruguay institutional memory sources | Keep Madres y Familiares, Secretaría de Derechos Humanos para el Pasado Reciente, and Sitios de Memoria Uruguay. | Low. |
| Uruguayan data-protection sources | Keep URCDP Resolution No. 30/020 and URCDP impact-assessment guide. | Low; verify legal wording before final submission. |
| Siluetazo | Keep Longoni and Bruzzone, *El Siluetazo*. | Low. |
| Brodsky, *Buena Memoria* | Keep book citation. | Low. |
| Germano, *Ausencias* | Replaced weak placeholder with book citation: Germano, *Ausencias* / *Verschwunden*. | Medium; verify exact publisher/year/edition used by the submitted reference list. |
| Traverso bicycles | Replaced placeholder with catalogue source: Romero chapter in *The Disappeared / Los Desaparecidos*, plus optional Hite for broader memorial politics. | Low/medium. |
| Parque de la Memoria | Replaced placeholder with institutional work description and Hite context. | Medium; still worth finding the exact institutional page or catalogue entry. |
| Claudia Fontes, *Reconstrucción del retrato de Pablo Míguez* | Replaced weak placeholder with public artwork citation in Parque de la Memoria context. | Medium; still requires exact institutional/catalogue source before final submission. |
| Urruzola, *Álbum de memoria* | Retained Dodecá exhibition documentation; reframed as exhibition documentation rather than definitive catalogue source. | Medium; improve if a catalogue or artist text is located. |
| Implementation description | Corrected to current code: six-dimensional colour/contrast/edge descriptor + deterministic L2 nearest-neighbour matching. | Low; must re-check after any future algorithm change. |
| Contribution cap | Runtime fixed so API/CLI and default Python settings use an active 240-tile source cap; zero/unset legacy values are normalised to 240 in API/CLI. | Low/medium; frontend label still needs UI polish. |
| Ethical project history | Internal grant/report files show a shift from restoration/public-release ambitions toward governed non-release and anti-restoration. | Low for planning; cite cautiously in submitted manuscript if double-blind review permits. |

## Sources added or strengthened

- Germano, Gustavo. 2010. *Ausencias*. Munich: Münchner Frühling Verlag.
- Hite, Katherine. 2012. *Politics and the Art of Commemoration: Memorials to Struggle in Latin America and Spain*. London: Routledge.
- Reuter, Laurel, ed. 2006. *The Disappeared / Los Desaparecidos*. Grand Forks: North Dakota Museum of Art.
- Romero, Juan Carlos. 2006. "Fernando Traverso: Interventions on the Streets of Rosario." In *The Disappeared / Los Desaparecidos*, edited by Laurel Reuter, 58-61. Grand Forks: North Dakota Museum of Art.
- Dodecá. 2009. "Expone Juan Ángel Urruzola." 9 October 2009. https://dodeca.org/2009/10/expone-ja-urruzola/.

## Internal project files read for planning

These are not necessarily references for the double-blind submission, but they inform the writing plan and manuscript history.

| File | Planning implication |
|---|---|
| 2023 *Liminal Memory* proposal | records an earlier restorative/forensic reconstruction ambition; useful only as project genealogy, not current ethical stance |
| 2024 *Capturing Collective Memories* proposal | establishes the conversational-AI archive origin and collaborators |
| 2024-2025 project report | records achieved outputs and the decision not to publicly release anonymised testimony data or interactive-prototype source code |
| PFH proposal | confirms four broader research axes: AI literacy, collective memory/archive politics, cognitive AI-interaction research, and art/computation/politics |
| CHA BatLLM proposal | supports promoting BatLLM to first-wave publication planning in AI education, HCI, and cognitive science venues |
| de Castro application | sharpens the archive as a sociotechnical formation and foregrounds fieldwork/governance |
| Paso de Morlán proposals | support a separate paper on source-conditioned visual hypotheses, co-creation, provenance, and AI historical reconstruction under archival absence |

## Remaining source tasks

1. Find exact institutional or catalogue source for Claudia Fontes's *Reconstrucción del retrato de Pablo Míguez*.
2. Find exact institutional or catalogue source for Parque de la Memoria's monument and public-art programme.
3. Verify the bibliographic details of Germano's *Ausencias* edition to be cited.
4. Search again for a stronger source on Urruzola's *Álbum de memoria*; if none appears, keep Dodecá and make the citation modest.
5. Add one scholarly source for the history of Uruguay's dictatorship and memory field if the word count allows.
6. Patch the frontend copy for source caps so the GUI text no longer calls zero "unlimited"; the running API/CLI path is already capped, but visible text should not conflict with the paper.

## Principle

Do not inflate uncertain references. If only partial or exhibition-documentation sources are available, cite them modestly and avoid overclaiming. The paper does not depend on any single precedent; it depends on a broader lineage of visual absence, public memorial practice, and anti-restorative representation.
