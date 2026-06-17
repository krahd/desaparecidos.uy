# desaparecidos.uy

`desaparecidos.uy` is a computational memorial artwork series by Tomas Laurenzo. It reconstructs public images of detained-disappeared persons connected to Uruguay from fragments of the country that survived them: people, places, streets, walls, landscapes, and public visual infrastructures.

The project is not an archive, forensic tool, biometric system, deepfake, or resurrection medium. It is an artistic system for making the continuing structure of disappearance perceptible.

The full draft project statement is in [doc/desaparecidos-uy-project-description.md](doc/desaparecidos-uy-project-description.md).

## Stage 1: Estan en todas partes

Stage 1 implements the place-based prototype. Public target portraits are reconstructed from fragments extracted from curated images of Uruguayan places, surfaces, streets, landscapes, and material environments.

The prototype provides:

- manifest-driven target and place-source ingestion;
- provenance and checksum recording for downloaded files;
- review gates before imagery can be used;
- deterministic fragment matching and assembly;
- still PNG outputs and optional MP4 rendering;
- JSON sidecars for generated outputs;
- a localhost-only GUI so the workflow can be run without typing CLI commands.

Raw source imagery and generated outputs are intentionally ignored by git.

## Local GUI

The normal workflow is the local web GUI.

```bash
./Start\ desaparecidos.command
```

The launcher creates or reuses a local Python environment, installs Python and frontend dependencies when needed, starts the FastAPI backend at `http://127.0.0.1:8765`, starts the Vite GUI at `http://127.0.0.1:5173`, and opens the browser.

The GUI can validate manifests, download manifest-listed sources, run still/video generation, inspect progress logs, and review output sidecars.

The tracked manifests are empty templates. To test the pipeline without editing CSV files, use **Create demo fixtures** in the GUI. It creates ignored synthetic images and demo manifests under `data/demo/` and `data/manifests/demo-*.csv`, switches the GUI to those manifests, and validates them. Demo provenance uses `local://demo/...` fixture identifiers, not placeholder external URLs.

## Manual Setup

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
npm --prefix frontend install
```

Run the backend:

```bash
python -m desaparecidos serve --host 127.0.0.1 --port 8765
```

Run the GUI:

```bash
npm --prefix frontend run dev -- --host 127.0.0.1 --port 5173
```

## CLI

The CLI remains available for automation and testing.

```bash
python -m desaparecidos validate --targets data/manifests/targets.csv --sources data/manifests/places.csv
python -m desaparecidos download --manifest data/manifests/places.csv --kind places
python -m desaparecidos run-stage1 --targets data/manifests/targets.csv --sources data/manifests/places.csv --output outputs/stage1 --seed 17
```

## Manifests and Review

Tracked manifest templates live in `data/manifests/`.

- Target manifests describe disappeared persons' public images and source provenance.
- Place manifests describe place/surface images and reuse terms.
- Rows must use `review_status=approved` before the pipeline can use the corresponding local file.
- Downloads are URL-list processing only. Stage 1 does not crawl websites.
- `reuse_limit` is enforced per extracted source fragment. Sidecars record source usage, fragment count, and the maximum observed fragment reuse.

Downloaded files are written under `data/raw/`; generated stills, videos, and sidecars are written under `outputs/stage1/`. Both directories are ignored.

## Verification

```bash
python -m compileall src tests
python -m pytest -q
npm --prefix frontend run build
```

## Repository Notes

Agents and contributors must read [AGENTS.md](AGENTS.md) and keep [STATUS.md](STATUS.md) current after meaningful changes.
