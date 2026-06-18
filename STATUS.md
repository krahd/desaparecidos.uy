# desaparecidos.uy - Project Status

Last updated: 2026-06-18 00:38 GMT-3

## Project purpose

`desaparecidos.uy` is a computational memorial artwork series about the persistence of disappearance in Uruguay's present. Stage 1 focuses on **Estan en todas partes**, a place-based prototype that reconstructs public target portraits from fragments of Uruguayan places and surfaces. The repository now also includes an importer for building a full target corpus of detained-disappeared persons connected to Uruguay from Sitios de Memoria Uruguay.

## Current implementation state

The repository contains the Stage 1 local software prototype: a Python pipeline, FastAPI localhost backend, React/Vite GUI, manifest templates, tests, a macOS launcher, a GUI-accessible synthetic demo fixture path, a constrained page-image crawler for explicit or preset pages, generated-output deletion controls, and browser-playable H.264 process-video rendering when `ffmpeg` is available.

The `import-full-disappeared-corpus` branch adds `scripts/import_sitios_memoria.py`, a source-specific importer that downloads the Sitios de Memoria forced-disappearance corpus, enriches records from individual person pages, downloads target portrait candidates, writes person metadata, and creates processed 4:5 portrait derivatives for review.

## Active focus

Build the complete disappeared-person target corpus automatically rather than by hand. Portraits of disappeared persons are treated as target imagery, distinct from crawled public-web source imagery. Public release still requires provenance, legal, privacy, and historical-source review.

## Architecture overview

The project is organised as a localhost tool. The frontend calls a local API. The API validates manifests, performs constrained one-page image crawling on user-supplied or preset URLs, updates row review status, deletes selected generated outputs on request, and invokes reusable Python pipeline code. The pipeline reads approved local inputs and writes ignored outputs plus JSON sidecars. Video generation uses the same assembly trace as still generation: each used source image is introduced full-screen, sampled fragment regions are highlighted, and fragments animate into their actual positions in the reconstructed portrait.

The corpus importer is an offline repository-maintenance script. It writes metadata under `data/persons/`, target manifests under `data/manifests/`, and target portraits under `assets/targets/disappeared/`.

### Architecture diagram

The current architecture is a local-only workflow with an offline import path for target portraits and metadata.

<svg width="820" height="300" viewBox="0 0 820 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="arch-title arch-desc">
  <title id="arch-title">Stage 1 local architecture plus target importer</title>
  <desc id="arch-desc">The importer writes target metadata and portraits; the local GUI and API invoke the Python pipeline to generate outputs from reviewed manifests.</desc>
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="#555" />
    </marker>
  </defs>
  <rect x="30" y="45" width="170" height="70" rx="6" fill="#f7f7f5" stroke="#777" />
  <text x="115" y="77" text-anchor="middle" font-family="Arial, sans-serif" font-size="14">Sitios importer</text>
  <text x="115" y="97" text-anchor="middle" font-family="Arial, sans-serif" font-size="12">offline script</text>
  <rect x="310" y="45" width="170" height="70" rx="6" fill="#f7f7f5" stroke="#777" />
  <text x="395" y="77" text-anchor="middle" font-family="Arial, sans-serif" font-size="14">Target corpus</text>
  <text x="395" y="97" text-anchor="middle" font-family="Arial, sans-serif" font-size="12">metadata + portraits</text>
  <rect x="600" y="45" width="170" height="70" rx="6" fill="#f7f7f5" stroke="#777" />
  <text x="685" y="77" text-anchor="middle" font-family="Arial, sans-serif" font-size="14">Python pipeline</text>
  <text x="685" y="97" text-anchor="middle" font-family="Arial, sans-serif" font-size="12">Stage 1</text>
  <rect x="150" y="180" width="170" height="70" rx="6" fill="#fff" stroke="#999" />
  <text x="235" y="211" text-anchor="middle" font-family="Arial, sans-serif" font-size="14">React GUI</text>
  <text x="235" y="231" text-anchor="middle" font-family="Arial, sans-serif" font-size="12">localhost</text>
  <rect x="410" y="180" width="170" height="70" rx="6" fill="#fff" stroke="#999" />
  <text x="495" y="211" text-anchor="middle" font-family="Arial, sans-serif" font-size="14">FastAPI backend</text>
  <text x="495" y="231" text-anchor="middle" font-family="Arial, sans-serif" font-size="12">localhost</text>
  <line x1="200" y1="80" x2="302" y2="80" stroke="#555" stroke-width="2" marker-end="url(#arrow)" />
  <line x1="480" y1="80" x2="592" y2="80" stroke="#555" stroke-width="2" marker-end="url(#arrow)" />
  <line x1="320" y1="215" x2="402" y2="215" stroke="#555" stroke-width="2" marker-end="url(#arrow)" />
  <line x1="550" y1="180" x2="632" y2="118" stroke="#777" stroke-width="2" marker-end="url(#arrow)" />
</svg>

### Flow chart

The target-import flow is separate from source-corpus crawling and generation.

<svg width="820" height="190" viewBox="0 0 820 190" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="flow-title flow-desc">
  <title id="flow-title">Target corpus import flow</title>
  <desc id="flow-desc">Sitios de Memoria data and pages are fetched, portraits are downloaded and processed, then manifests are reviewed before generation.</desc>
  <defs>
    <marker id="flow-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="#555" />
    </marker>
  </defs>
  <rect x="20" y="60" width="125" height="60" rx="6" fill="#f7f7f5" stroke="#777" />
  <text x="82" y="86" text-anchor="middle" font-family="Arial, sans-serif" font-size="13">CSV export</text>
  <text x="82" y="105" text-anchor="middle" font-family="Arial, sans-serif" font-size="11">base rows</text>
  <rect x="175" y="60" width="125" height="60" rx="6" fill="#f7f7f5" stroke="#777" />
  <text x="237" y="86" text-anchor="middle" font-family="Arial, sans-serif" font-size="13">Person pages</text>
  <text x="237" y="105" text-anchor="middle" font-family="Arial, sans-serif" font-size="11">richer fields</text>
  <rect x="330" y="60" width="125" height="60" rx="6" fill="#f7f7f5" stroke="#777" />
  <text x="392" y="86" text-anchor="middle" font-family="Arial, sans-serif" font-size="13">Portraits</text>
  <text x="392" y="105" text-anchor="middle" font-family="Arial, sans-serif" font-size="11">raw targets</text>
  <rect x="485" y="60" width="125" height="60" rx="6" fill="#f7f7f5" stroke="#777" />
  <text x="547" y="86" text-anchor="middle" font-family="Arial, sans-serif" font-size="13">Process</text>
  <text x="547" y="105" text-anchor="middle" font-family="Arial, sans-serif" font-size="11">4:5 outputs</text>
  <rect x="640" y="60" width="155" height="60" rx="6" fill="#f7f7f5" stroke="#777" />
  <text x="717" y="86" text-anchor="middle" font-family="Arial, sans-serif" font-size="13">Review manifest</text>
  <text x="717" y="105" text-anchor="middle" font-family="Arial, sans-serif" font-size="11">candidate or approved</text>
  <line x1="145" y1="90" x2="167" y2="90" stroke="#555" stroke-width="2" marker-end="url(#flow-arrow)" />
  <line x1="300" y1="90" x2="322" y2="90" stroke="#555" stroke-width="2" marker-end="url(#flow-arrow)" />
  <line x1="455" y1="90" x2="477" y2="90" stroke="#555" stroke-width="2" marker-end="url(#flow-arrow)" />
  <line x1="610" y1="90" x2="632" y2="90" stroke="#555" stroke-width="2" marker-end="url(#flow-arrow)" />
</svg>

## Setup and run instructions

Use the macOS launcher for the GUI:

```bash
./Start\ desaparecidos.command
```

Manual setup:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
npm --prefix frontend install
python -m desaparecidos serve --host 127.0.0.1 --port 8765
npm --prefix frontend run dev -- --host 127.0.0.1 --port 5173
```

Run a small importer test:

```bash
python scripts/import_sitios_memoria.py --limit 5 --download-images --process-images
```

Run the full target-corpus import:

```bash
python scripts/import_sitios_memoria.py --download-images --process-images
```

## Configuration and environment variables

- No secrets are required.
- The backend must bind to `127.0.0.1` by default.
- Raw crawler downloads belong under ignored `data/raw/`.
- Generated outputs belong under ignored `outputs/stage1/`.
- Target portraits of disappeared persons are written under `assets/targets/disappeared/` by the importer.
- Browser-playable video generation requires `ffmpeg` with H.264/libx264 support.

## Important files and directories

- `README.md`: project overview and setup.
- `AGENTS.md`: repository instructions for AI coding agents.
- `STATUS.md`: mandatory project state report.
- `src/desaparecidos/`: Python pipeline and API.
- `frontend/`: local GUI.
- `scripts/import_sitios_memoria.py`: automated Sitios de Memoria metadata and target portrait importer.
- `doc/import-sitios-de-memoria.md`: importer usage notes.
- `data/persons/`: importer output for disappeared-person metadata.
- `data/manifests/`: tracked manifest templates and importer target manifest output.
- `assets/targets/disappeared/`: raw and processed target portraits imported from historical-memory sources.
- `outputs/stage1/`: ignored generated stills, videos, and sidecars.
- GitHub: private repository at `https://github.com/krahd/desaparecidos.uy`.

## Current capabilities

- Generate Stage 1 stills and process videos from reviewed local manifests.
- Operate through a localhost GUI and backend.
- Crawl constrained user-supplied or preset place/source pages into pending manifests.
- Import the Sitios de Memoria disappearance corpus automatically into structured JSON/CSV plus target-portrait manifests.
- Download and normalise target portrait candidates to 4:5, 1200 x 1500 pixels.

## Recent changes

- Initial project documentation, Stage 1 pipeline, local GUI, manifest templates, tests, and launcher were created.
- Private GitHub repository `krahd/desaparecidos.uy` was created and `main` was pushed.
- GUI demo fixtures, review controls, constrained crawler, generated-output deletion controls, and source-first process video rendering were added.
- 2026-06-18 00:38 GMT-3 follow-up: added `scripts/import_sitios_memoria.py` for automated import of the full Sitios de Memoria disappearance corpus and target portrait candidates; added `doc/import-sitios-de-memoria.md` documenting test and full-import commands.

## Tests and verification status

Previous verification on 2026-06-17 passed for compile, pytest, frontend build, synthetic fixtures, CLI smoke runs, backend health checks, GUI load, API validation, and process-video smoke rendering.

2026-06-18 importer follow-up:

- Repository files were inspected through the GitHub connector.
- The importer script and documentation were added through GitHub commits on `import-full-disappeared-corpus`.
- The importer was not executed in this environment because the active container has no direct internet access for repository-local Python execution.
- The GitHub Actions self-commit workflow was attempted but blocked by the connector safety layer, so it was not added.
- No automated test, build, or import run was performed after adding the script.

## Known issues, risks, and limitations

- Public release requires provenance, legal, privacy, and historical-source review.
- The importer depends on the current Sitios de Memoria CSV/HTML structure.
- Automated portrait border removal is conservative and does not guarantee removal of all lettering, frames, or layout artefacts.
- The importer does not yet merge SDHPR fichas as a secondary verification layer.
- Stage 1 crawler support is intentionally limited to page URLs entered by the local user. It is not recursive, does not identify people, and writes pending rows that require explicit approval before generation.
- MP4 generation depends on `ffmpeg` with H.264/libx264 support.
- The GitHub remote is `origin` at `https://github.com/krahd/desaparecidos.uy.git`.

## Recurring tasks

- Keep `STATUS.md` updated after meaningful implementation or verification changes.
- Keep generated outputs and local caches untracked.
- Review provenance and `review_status` before generation.
- Keep target portraits of disappeared persons separated from crawled source-corpus imagery.

## Pending tasks

- Run the importer against the live source.
- Inspect generated metadata and portraits.
- Decide whether imported target portraits should remain `candidate` or be marked `approved`.
- Add SDHPR verification/merge support.
- Remove unused empty import branches if desired; the active branch is `import-full-disappeared-corpus`.

## Next steps

1. Run `python scripts/import_sitios_memoria.py --limit 5 --download-images --process-images` locally and inspect outputs.
2. Run the full import after the five-record test succeeds.
3. Commit generated `data/persons/`, `data/manifests/targets-sitios-de-memoria.csv`, and `assets/targets/disappeared/` files after review.
4. Add SDHPR fiche cross-checking.

## Longer-term steps

1. Expand visual method documentation.
2. Add public website pages after Stage 1 output review.
3. Prepare legal and privacy review materials before any public release.
4. Decide which target portraits become canonical and how alternates are represented.

## Decisions and rationale

- Stage 1 uses place/surface imagery first because it is visually strong and has lower privacy risk than face-fragment processing.
- Portraits of disappeared persons are treated as target imagery, not source-corpus imagery.
- The GUI is localhost-only so the artist/developer can operate the pipeline without exposing data or outputs.
- Manifests remain the boundary for generation; crawler output is only a pending manifest-building aid.
- The Sitios de Memoria importer is source-specific to keep provenance explicit and reduce manual collection work.

## Documentation alignment notes

- The root README summarises the long project description in `doc/desaparecidos-uy-project-description.md`.
- `doc/import-sitios-de-memoria.md` documents the corpus importer.
- `AGENTS.md` requires `STATUS.md` to stay current.

---

Last updated: 2026-06-18 00:38 GMT-3
