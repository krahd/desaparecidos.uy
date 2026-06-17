# desaparecidos.uy - Project Status

Last updated: 2026-06-17 10:59 GMT-3

## Project purpose

`desaparecidos.uy` is a computational memorial artwork series about the persistence of disappearance in Uruguay's present. Stage 1 focuses on **Estan en todas partes**, a place-based prototype that reconstructs public target portraits from fragments of Uruguayan places and surfaces.

## Current implementation state

The repository now contains the Stage 1 local software prototype: a Python pipeline, FastAPI localhost backend, React/Vite GUI, manifest templates, tests, a macOS launcher, and a GUI-accessible synthetic demo fixture path.

## Active focus

Review real target/place manifests before introducing non-synthetic imagery, while keeping raw imagery and generated outputs out of version control.

## Architecture overview

The project is organised as a localhost tool. The frontend calls a local API. The API validates manifests and invokes reusable Python pipeline code. The pipeline reads approved local inputs and writes ignored outputs plus JSON sidecars.

### Architecture diagram

The current architecture is a local-only workflow with no public network service.

<svg width="760" height="250" viewBox="0 0 760 250" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="arch-title arch-desc">
  <title id="arch-title">Stage 1 local architecture</title>
  <desc id="arch-desc">React GUI talks to a localhost FastAPI backend, which uses the Python pipeline to read manifests and write generated outputs.</desc>
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="#555" />
    </marker>
  </defs>
  <rect x="30" y="50" width="150" height="70" rx="6" fill="#f7f7f5" stroke="#777" />
  <text x="105" y="82" text-anchor="middle" font-family="Arial, sans-serif" font-size="14">React GUI</text>
  <text x="105" y="102" text-anchor="middle" font-family="Arial, sans-serif" font-size="12">localhost:5173</text>
  <rect x="300" y="50" width="170" height="70" rx="6" fill="#f7f7f5" stroke="#777" />
  <text x="385" y="80" text-anchor="middle" font-family="Arial, sans-serif" font-size="14">FastAPI backend</text>
  <text x="385" y="101" text-anchor="middle" font-family="Arial, sans-serif" font-size="12">localhost:8765</text>
  <rect x="570" y="50" width="150" height="70" rx="6" fill="#f7f7f5" stroke="#777" />
  <text x="645" y="82" text-anchor="middle" font-family="Arial, sans-serif" font-size="14">Python pipeline</text>
  <text x="645" y="102" text-anchor="middle" font-family="Arial, sans-serif" font-size="12">Stage 1</text>
  <rect x="170" y="165" width="160" height="55" rx="6" fill="#fff" stroke="#999" />
  <text x="250" y="188" text-anchor="middle" font-family="Arial, sans-serif" font-size="13">Manifests</text>
  <text x="250" y="206" text-anchor="middle" font-family="Arial, sans-serif" font-size="11">data/manifests</text>
  <rect x="430" y="165" width="170" height="55" rx="6" fill="#fff" stroke="#999" />
  <text x="515" y="188" text-anchor="middle" font-family="Arial, sans-serif" font-size="13">Ignored outputs</text>
  <text x="515" y="206" text-anchor="middle" font-family="Arial, sans-serif" font-size="11">outputs/stage1</text>
  <line x1="180" y1="85" x2="292" y2="85" stroke="#555" stroke-width="2" marker-end="url(#arrow)" />
  <line x1="470" y1="85" x2="562" y2="85" stroke="#555" stroke-width="2" marker-end="url(#arrow)" />
  <line x1="250" y1="165" x2="330" y2="122" stroke="#777" stroke-width="2" marker-end="url(#arrow)" />
  <line x1="610" y1="122" x2="545" y2="165" stroke="#777" stroke-width="2" marker-end="url(#arrow)" />
</svg>

### Flow chart

The Stage 1 flow requires manual review before generation.

<svg width="760" height="180" viewBox="0 0 760 180" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="flow-title flow-desc">
  <title id="flow-title">Stage 1 data flow</title>
  <desc id="flow-desc">Manifest rows are validated, reviewed, assembled into outputs, and then inspected before publication.</desc>
  <defs>
    <marker id="flow-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="#555" />
    </marker>
  </defs>
  <rect x="25" y="55" width="120" height="60" rx="6" fill="#f7f7f5" stroke="#777" />
  <text x="85" y="82" text-anchor="middle" font-family="Arial, sans-serif" font-size="13">Manifests</text>
  <text x="85" y="101" text-anchor="middle" font-family="Arial, sans-serif" font-size="11">targets / places</text>
  <rect x="185" y="55" width="120" height="60" rx="6" fill="#f7f7f5" stroke="#777" />
  <text x="245" y="82" text-anchor="middle" font-family="Arial, sans-serif" font-size="13">Validate</text>
  <text x="245" y="101" text-anchor="middle" font-family="Arial, sans-serif" font-size="11">fields and paths</text>
  <rect x="345" y="55" width="120" height="60" rx="6" fill="#f7f7f5" stroke="#777" />
  <text x="405" y="82" text-anchor="middle" font-family="Arial, sans-serif" font-size="13">Review gate</text>
  <text x="405" y="101" text-anchor="middle" font-family="Arial, sans-serif" font-size="11">approved only</text>
  <rect x="505" y="55" width="120" height="60" rx="6" fill="#f7f7f5" stroke="#777" />
  <text x="565" y="82" text-anchor="middle" font-family="Arial, sans-serif" font-size="13">Generate</text>
  <text x="565" y="101" text-anchor="middle" font-family="Arial, sans-serif" font-size="11">still / video</text>
  <rect x="665" y="55" width="70" height="60" rx="6" fill="#f7f7f5" stroke="#777" />
  <text x="700" y="82" text-anchor="middle" font-family="Arial, sans-serif" font-size="13">Inspect</text>
  <text x="700" y="101" text-anchor="middle" font-family="Arial, sans-serif" font-size="11">outputs</text>
  <line x1="145" y1="85" x2="177" y2="85" stroke="#555" stroke-width="2" marker-end="url(#flow-arrow)" />
  <line x1="305" y1="85" x2="337" y2="85" stroke="#555" stroke-width="2" marker-end="url(#flow-arrow)" />
  <line x1="465" y1="85" x2="497" y2="85" stroke="#555" stroke-width="2" marker-end="url(#flow-arrow)" />
  <line x1="625" y1="85" x2="657" y2="85" stroke="#555" stroke-width="2" marker-end="url(#flow-arrow)" />
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

## Configuration and environment variables

- No secrets are required.
- The backend must bind to `127.0.0.1` by default.
- Raw downloads belong under ignored `data/raw/`.
- Generated outputs belong under ignored `outputs/stage1/`.

## Important files and directories

- `README.md`: project overview and setup.
- `AGENTS.md`: repository instructions for AI coding agents.
- `CLAUDE.md`: compatibility pointer for Claude Code.
- `src/desaparecidos/`: Python pipeline and API.
- `frontend/`: local GUI.
- `data/manifests/`: tracked manifest templates.
- `data/manifests/demo-*.csv`: ignored synthetic demo manifests generated on demand.
- `data/demo/`: ignored synthetic demo images generated on demand.
- `doc/`: long-form project source documents.
- GitHub: private repository at `https://github.com/krahd/desaparecidos.uy`.

## Recent changes

- Initial project documentation, Stage 1 pipeline, local GUI, manifest templates, tests, and launcher were created.
- Private GitHub repository `krahd/desaparecidos.uy` was created and `main` was pushed.
- GUI demo fixtures were added so users can recover from empty template manifests without running CLI commands.
- Local API CORS was widened to localhost/127.0.0.1 on any port so alternate Vite ports remain usable.

## Tests and verification status

Verification run on 2026-06-17:

- `python3 -m compileall src tests scripts`: passed before dependency installation.
- `.venv/bin/python -m compileall src tests scripts`: passed.
- `.venv/bin/python -m pytest -q`: passed, 7 tests; one upstream `fastapi.testclient` deprecation warning from Starlette.
- `npm --prefix frontend run build`: passed.
- Synthetic fixture generation with `scripts/create_synthetic_fixtures.py`: passed.
- CLI Stage 1 smoke run against synthetic fixtures: passed and wrote ignored output files under `outputs/stage1/`.
- Local backend health check at `http://127.0.0.1:8765/api/health`: passed.
- Vite GUI load at `http://127.0.0.1:5173`: passed.
- API validation and generation calls matching the GUI workflow: passed against synthetic manifests.
- Desktop and mobile-width Safari screenshots were inspected for visible layout overlap and text fit.
- 2026-06-17 follow-up: `.venv/bin/python -m compileall src tests scripts`, `.venv/bin/python -m pytest -q`, and `npm --prefix frontend run build` passed after adding the demo-fixture GUI path.
- 2026-06-17 follow-up: patched API `/api/demo-fixtures`, `/api/validate`, and `/api/generate` were smoke-tested on isolated verification ports.

## Known issues, risks, and limitations

- Public release requires provenance, legal, privacy, and historical-source review.
- Stage 1 download support is manifest-driven only and does not crawl sites.
- MP4 generation depends on OpenCV runtime support.
- `npm install` reported two high-severity audit findings in the frontend dependency tree. No forced audit fix was applied because it may introduce breaking dependency changes.
- Local server binding required sandbox escalation during verification.
- The GitHub remote is `origin` at `https://github.com/krahd/desaparecidos.uy.git`.

## Recurring tasks

- Keep `STATUS.md` updated after meaningful implementation or verification changes.
- Keep raw imagery, generated outputs, and local caches untracked.
- Review provenance and `review_status` before generation.

## Pending tasks

- No repository setup tasks are pending.

## Next steps

1. Restart the local launcher if it was running before the demo-fixture patch, so the backend loads `/api/demo-fixtures`.
2. Review real target/place manifests before adding any non-synthetic imagery.
3. Decide whether to address the frontend npm audit findings before broader use.

## Longer-term steps

1. Expand visual method documentation.
2. Add public website pages after Stage 1 output review.
3. Prepare legal and privacy review materials before any public release.

## Decisions and rationale

- Stage 1 uses place/surface imagery first because it is visually strong and has lower privacy risk than face-fragment processing.
- The GUI is localhost-only so the artist/developer can operate the pipeline without exposing data or outputs.
- Manifests are the boundary for source acquisition; Stage 1 avoids crawling.

## Documentation alignment notes

- The root README summarises the long project description in `doc/desaparecidos-uy-project-description.md`.
- `AGENTS.md` requires `STATUS.md` to stay current.

---

Last updated: 2026-06-17 10:59 GMT-3
