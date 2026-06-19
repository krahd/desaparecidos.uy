# Source audit for AI & SOCIETY Open Forum paper

Branch: `paper-ai-society-open-forum-import`  
Manuscript: `doc/writings/ai-society-open-forum.md`  
Audit date: 2026-06-18

## Venue and CFP

| Claim / use | Verification | Status | Source |
|---|---|---|---|
| AI & SOCIETY has a topical collection titled "Responsible use of AI in Art Creation and Archival Practice". | Springer page lists that exact collection. | Verified | https://link.springer.com/journal/146/updates/27850936 |
| Guest editors are Lydia Farina, Helena Webb, and Bernd Stahl; Larry Stapleton is collection adviser. | Springer CFP lists these names. | Verified | https://link.springer.com/journal/146/updates/27850936 |
| Manuscript deadline is 30 June 2026. | Springer CFP lists manuscript submission deadline as 30 June 2026. | Verified | https://link.springer.com/journal/146/updates/27850936 |
| Open Forum papers are max. 8,000 words, research-in-progress / ideas / case-study compatible, and double-blind reviewed. | Springer CFP describes Open Forum papers in these terms. | Verified | https://link.springer.com/journal/146/updates/27850936 |
| CFP asks for implementable/theoretical frameworks, broad AI beyond GenAI, and lifecycle of art creation, documentation, reactivation, preservation, and archiving. | Springer CFP explicitly states these aims. | Verified | https://link.springer.com/journal/146/updates/27850936 |

## Uruguay, disappeared persons, and data sources

| Claim / use | Verification | Status | Source |
|---|---|---|---|
| Uruguay's civic-military dictatorship ran from 1973 to 1985. | Widely established; corroborated by public histories and current news coverage. | Verified | https://apnews.com/article/901429b132cd3c5e2e6af8d201ca646c |
| The disappeared connected to Uruguay include persons detained in Uruguay, Argentina, and elsewhere. | Sitios de Memoria victim pages and table include detention/disappearance locations in Uruguay and Argentina. | Verified | https://sitiosdememoria.uy/desaparicion-forzada |
| SDHPR provides public victims files and lists. | SDHPR victims page links to fichas and official detained-disappeared list. | Verified | https://www.gub.uy/secretaria-derechos-humanos-pasado-reciente/victimas |
| Sitios de Memoria provides forced-disappearance entries and exportable data. | Site has forced-disappearance table and export page. | Verified | https://sitiosdememoria.uy/desaparicion-forzada ; https://sitiosdememoria.uy/exportar-datos |
| Sitios de Memoria contents are CC BY-SA 4.0. | Export page footer states content is published under Creative Commons Atribución-Compartir Igual 4.0 Internacional. | Verified | https://sitiosdememoria.uy/exportar-datos |
| Public availability is not equivalent to unrestricted consent. | Ethical argument; not a factual claim from one source. It is supported by data-protection law and privacy scholarship, but should remain framed as an ethical position. | Framing retained | URCDP sources below; additional privacy scholarship can be added. |
| Biometric processing requires special caution under Uruguayan rules. | URCDP Resolution 30/020 states that biometric data includes facial images and that biometric-data processing must undergo a data-protection impact assessment. | Verified | https://www.gub.uy/unidad-reguladora-control-datos-personales/institucional/normativa/resolucion-n-30020 |
| DPIA guidance exists for regional personal-data processing. | URCDP/AAIP guide describes itself as a reference for entities in the region processing personal data. | Verified | https://www.gub.uy/unidad-reguladora-control-datos-personales/comunicacion/publicaciones/guia-evaluacion-impacto-proteccion-datos |

## Memorial and artwork precedents

| Claim / use | Verification | Status | Source |
|---|---|---|---|
| The first Siluetazo took place in Buenos Aires in 1983 and produced life-size silhouettes in public space. | Public historical sources corroborate 21 September 1983 and life-size silhouettes in Plaza de Mayo. | Verified; use Longoni/Bruzzone book as scholarly reference where possible | https://es.wikipedia.org/wiki/Siluetazo ; Longoni and Bruzzone 2008 |
| Mothers of Plaza de Mayo are a central visual-political precedent for disappearance activism. | Public historical sources corroborate formation and sustained Thursday marches. | Verified | https://en.wikipedia.org/wiki/Mothers_of_Plaza_de_Mayo ; prefer scholarly source in final paper |
| Marcelo Brodsky's *Buena Memoria* works from a school/class photograph and disappearance. | Public artist/biographical sources corroborate the work and 1997 publication. | Verified | https://es.wikipedia.org/wiki/Marcelo_Brodsky |
| Gustavo Germano's *Ausencias* restages family photographs and marks absent disappeared persons. | Public sources corroborate the series and its method. | Verified; needs stronger primary source if available | https://es.wikipedia.org/wiki/Carmen_Salvay_de_Germano |
| Fernando Traverso's bicycle stencils in Rosario memorialise disappeared persons. | Public sources identify the 350 bicycle stencil intervention and its relation to disappeared persons in Rosario. | Verified | https://es.wikipedia.org/wiki/Fernando_Traverso ; https://en.wikipedia.org/wiki/Fernando_Traverso%27s_Bicis |
| Parque de la Memoria is a public memorial in Buenos Aires facing the Río de la Plata with a Monumento a las Víctimas del Terrorismo de Estado and public sculptures. | Public sources corroborate site, monument, river orientation, and wound-like ramp. | Verified; prefer official Parque source if accessible | https://es.wikipedia.org/wiki/Parque_de_la_Memoria_de_Buenos_Aires |
| Claudia Fontes's *Reconstrucción del retrato de Pablo Míguez* is installed at Parque de la Memoria. | Public sources list the work among Parque sculptures. | Verified through secondary source; needs primary/official source if found | https://es.wikipedia.org/wiki/Parque_de_la_Memoria_de_Buenos_Aires |
| Juan Ángel Urruzola's *Álbum de memoria* uses small ID-style photos of detained-disappeared persons to form another disappeared person's face. | Dodecá page quotes Tatiana Oroño describing a mosaic of small ID-style faces forming the enlarged face of another disappeared person. | Verified | https://dodeca.org/2009/10/expone-ja-urruzola/ |

## Project-internal claims

| Claim / use | Verification | Status | Source |
|---|---|---|---|
| `desaparecidos.uy` is a triptych of *Todos somos familiares*, *Están en todas partes*, and *Seguimos buscando*. | Project statement says this explicitly. | Verified internally | `doc/desaparecidos-uy-project-description.md` |
| The works are not forensic, archival, biometric, deepfake, resurrection, or restoration systems. | Project statement gives negative definitions. | Verified internally | `doc/desaparecidos-uy-project-description.md` |
| Stage 1 is *Están en todas partes* because it is conceptually strong and lower privacy risk. | Project statement development stages say Stage 1 should be place-based. | Verified internally | `doc/desaparecidos-uy-project-description.md` |
| Current repo implements crawler, review gates, CV gating, manifests, process videos, and sidecars. | `STATUS.md` documents current implementation. | Verified internally | `STATUS.md` |

## References not yet sufficiently grounded

- Gustavo Germano, *Ausencias*: find official artist/site or catalogue source.
- Claudia Fontes, *Reconstrucción del retrato de Pablo Míguez*: find official Parque de la Memoria or artist page.
- Parque de la Memoria architectural details: replace Wikipedia/secondary source with official or scholarly source if available.
- Full Springer style: convert all entries after citation manager/export workflow is chosen.
- Memory/visual theory references (Azoulay, Derrida, Didi-Huberman, Hirsch, Jelin, Nora, Sontag, Taylor) are standard bibliographic references but were not individually re-downloaded; use library/Zotero records for final copy-edit.

## Notes on downloading references

This audit records verified URLs and bibliographic anchors in `doc/writings/references/`. I did not commit copyrighted book PDFs. For open web pages and public official sources, the stable URLs are recorded in this folder. If PDF archiving is needed, use Zotero/Bookends or a repository policy for binary reference files before committing them.
