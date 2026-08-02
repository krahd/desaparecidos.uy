# desaparecidos.uy Project Status

Last updated: 2026-08-02 02:20 GMT-3

## Governing principle

`desaparecidos.uy` is first a computational memorial and artwork. Technical architecture, constraints, evaluation and academic writing must emerge from its artistic and political operations. The project must not acquire arbitrary requirements solely to satisfy a paper.

Durable sources of truth:

- `doc/artistic-computational-principles.md` — artistic and computational hierarchy;
- `doc/development-roadmap.md` — completion programme;
- `doc/desaparecidos-uy-project-description.md` — historical, political and artistic description;
- `doc/implementation-corrections.md` — current technical corrections to legacy descriptions;
- `doc/artwork-runtime.md` — canonical rendering, evaluation, exhibition and publication workflow.

## Project

The triptych computationally re-enacts three continuing propositions:

- **Todos somos familiares** — documented portraits of the disappeared emerge from dispersed fragments of the contemporary social body;
- **Están en todas partes** — documented portraits emerge from Uruguay's places, surfaces, infrastructures, things and territories;
- **Seguimos buscando** — traversal and continuing search determine which visual material can participate and when.

Generated videos are primary manifestations of the memorial, not software demonstrations. The work is not a forensic reconstruction, restoration system, biometric identifier, deepfake, resurrection medium or replacement archive.

## Two runtime paths

### Legacy local application

The existing localhost-only GUI, FastAPI backend and `desaparecidos` command remain operational. They provide target administration, source ingestion and review, crawler and traversal workflows, deterministic square-fragment matching, still/MP4 generation and legacy sidecars.

### Canonical artwork runtime

`desaparecidos-artwork` and `src/desaparecidos/artwork_runtime.py` now define the artwork-oriented rendering path. It adds:

- `grid`, `irregular` and `overlap` final visual grammars;
- independent target matching and final render geometry;
- deterministic position, scale, rotation, opacity and z-order;
- portrait-oriented or uniform target-section ordering;
- mandatory positive people-source contribution limits;
- optional prevention of neighbouring fragments from one people source;
- fragment-emergence video without raw contemporary source-image reveal;
- territorially balanced place-source selection using reviewed labels while retaining `unlocated` material;
- incremental traversal rendering with no future-frame access;
- persistent output sidecars using `desaparecidos.uy/output-sidecar/2.0`;
- complete placement histories using `desaparecidos.uy/placement-history/1.0`.

The legacy GUI path is retained for compatibility. It should not be described as the limit of the artwork's current visual architecture.

## Artwork-derived evaluation

`src/desaparecidos/evaluation.py` and `scripts/evaluate_artwork_output.py` report:

- realised source participation, maximum share, HHI and effective source count;
- same-source adjacency and largest connected same-source target region;
- overlap, rotation and opacity properties;
- temporal-causality violations;
- optional low-level target luminance and gradient diagnostics.

These measures do not establish memorial adequacy, identity, consent or anonymity. People-derived outputs remain subject to complete human review.

## Exhibition and online publication

- `scripts/render_exhibition_triptych.py` renders all three video loops from a declared plan and creates target-level evaluations plus a hash-addressed exhibition manifest.
- `config/exhibition-triptych.example.json` records the full render configuration.
- `web/` contains a sober, tracking-free static memorial presentation.
- `scripts/publish_static_memorial.py` copies only explicitly selected works whose SHA-256 digests match the exhibition manifest.
- publication requires explicit acknowledgement that historical, source-rights, contextual, recognisability and full-duration review has been completed.

The tooling is implemented. Final exhibition media are not committed and have not been rendered in this environment because they require the reviewed local source corpora, selected target sequence, an approved traversal, FFmpeg and complete visual review.

## Artwork-derived URUCON paper

The canonical paper package is maintained in:

`krahd/academic-writing/my_papers_2026/2026 - Urucon - Desaparecidos.uy/urucon_v7_artwork_derived/`

Title:

**Computational Re-enactment in a Digital Memorial**

Completed:

- complete artwork-derived manuscript;
- system diagram and claim-to-evidence matrix;
- corrected mixed `lfw_subset` description;
- conference, historical and complete bibliography audit;
- direct verification of the reported benchmark endpoints and percentage changes from the retained CSVs;
- rejection-oriented adversarial review;
- A4 two-column DOCX and four-page PDF within the five-page maximum;
- page-level and mechanical PDF inspection;
- exact artifact hashes.

The paper cites the verified runtime revision `5a5a5626f94dfa6b3982234c948d58ebd088405d`. The final EDAS upload still requires export from Microsoft Word with Times New Roman installed, confirmation of the live conference instructions and resolution of any EDAS diagnostics. The paper explicitly marks final exhibition media and people-derived public-release evidence as pending rather than fabricating them.

## Source and network safety

- manifest downloads are size-bounded and require an image response;
- crawler defaults now traverse to depth 3 across up to 150 same-domain pages, inspect up to 40 candidates per page and 300 per run, and recognise common lazy-loaded image attributes;
- the Images review page can hide approved and rejected rows independently, select all visible pending rows, approve or reject selected rows in bulk, and keeps contained thumbnails and review actions within naturally sized cards;
- production network requests reject localhost, private, link-local, reserved, unspecified, multicast and credential-bearing targets;
- every redirect target is revalidated;
- explicitly injected test clients remain usable without external DNS;
- raw source imagery, generated media, crawler caches, traversal data and sensitive review material remain ignored.

## Target corpus

- canonical records: `data/persons/disappeared.json`;
- reviewed selected portraits: `assets/targets/disappeared/selected/`;
- current project-curation count: 204 person records and 202 selected portrait derivatives;
- unresolved public-portrait gaps: `camuyrano-bottini-mario` and `gadea-hernandez-liborio`.

These are project-corpus counts, not an authoritative historical total.

## Nine-part completion programme

1. **Documentation reconciliation — implemented.** Current corrections and canonical runtime documentation explicitly supersede stale technical descriptions.
2. **Persistent placement and temporal histories — implemented in the canonical runtime.**
3. **General placement architecture with retained grid baseline — implemented.**
4. **Irregular and overlapping visual grammars — implemented and tested.**
5. **Target salience and source-person non-representation controls — implemented; human review remains mandatory.**
6. **Territorial and traversal processes — implemented, including explicit territorial uncertainty and causal placement histories.**
7. **Verification, CI and software hardening — implemented and verified.**
8. **Exhibition loops and durable online form — render and publication systems implemented; final reviewed media remain a material-production and human-review task.**
9. **Artwork-derived URUCON paper — manuscript, evidence package, complete citation/numerical audit, adversarial review and four-page A4 two-column artifacts completed. Final Microsoft Word/EDAS export checks remain submission operations rather than research or implementation work.**

## Verification

Disposable verification PR `#4` was opened against `main` and closed without merging its trigger file.

GitHub Actions run `30145676564` completed successfully on 25 July 2026:

- Python 3.11 installation, complete test step, local API import and resolved-environment artifact — passed;
- Python 3.12 installation, complete test step, local API import and resolved-environment artifact — passed;
- frontend locked installation, tests and production build — passed;
- launcher shell-syntax validation — passed.

The verification run tested the current `main` implementation through the PR merge ref. It did not render final exhibition media or perform human source/output review.

Local verification on 2 August 2026 after the crawler and image-review changes:

- `python -m compileall -q src tests` — passed;
- `python -m pytest -q` — 162 passed with five existing deprecation warnings;
- `npm --prefix frontend run test` — eight tests passed;
- `npm --prefix frontend run build` — passed with the existing large-chunk advisory;
- visual browser inspection was not completed because browser control could not initialise in the restricted environment.

## Technical and ethical invariants

- Keep the GUI/API localhost-only unless deployment is deliberately redesigned.
- Require `review_status=approved` before ordinary source participation.
- Do not commit raw source imagery, rejected candidates, generated outputs, fragments, downloads, databases, credentials or generated sensitive material.
- Treat historical portraits as documented referents, not material for enhancement, resurrection or forensic claims.
- Do not add identity seeking, face/name matching, demographic inference or biometric identification for contemporary people.
- Public availability is not blanket consent.
- Exclude minors, private contexts and sensitive contexts without explicit permission and a defensible artistic reason.
- Never claim that fragment controls guarantee anonymity.
- Keep `Todos somos familiares` internal until its corpus and complete outputs receive appropriate review.
- Preserve strict temporal causality in `Seguimos buscando`.
- Do not convert source accountability into an inflated claim of legality, consent or memorial legitimacy.

## Primary commands

Local GUI:

```bash
./start.sh
```

Canonical artwork render:

```bash
desaparecidos-artwork render --help
desaparecidos-artwork search --help
```

Evaluation:

```bash
python scripts/evaluate_artwork_output.py --help
```

Exhibition and static publication:

```bash
python scripts/render_exhibition_triptych.py --help
python scripts/publish_static_memorial.py --help
```

Complete verification:

```bash
python -m pytest -q
npm --prefix frontend ci
npm --prefix frontend test
npm --prefix frontend run build
bash -n start.sh
```

Last updated: 2026-08-02 02:20 GMT-3
