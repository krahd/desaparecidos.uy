# Gemini CLI Project Instructions

Read [AGENTS.md](AGENTS.md) before making changes. Follow the standard work loop and communication rules defined there.

## Project Summary & Conceptual Reference
- This repository is a local-first computational memorial artwork prototype.
- Use [doc/desaparecidos-uy-project-description.md](doc/desaparecidos-uy-project-description.md) as the conceptual reference for the triptych, ethics, and visual method.

## Critical Mandates & Safety Invariants
- **Localhost Bound:** Keep the GUI and API bound to localhost.
- **Do Not Commit Transients:** Do not commit raw source imagery, rejected candidates, generated outputs, database dumps, crawler caches, or local environment files. Transient crawler data is persisted under ignored `data/raw/crawl/` but must never be tracked.
- **Curated Assets are Tracked:** Curated source portraits under `doc/fotos-desaparecidos/`, canonical metadata in `data/persons/disappeared.json`, and reviewed selected derivatives in `assets/targets/disappeared/selected/` are intentional, trackable corpus files. Do not remove or untrack them.
- **No Biometric/Identity Matching:** Do not add identity-seeking behaviour, face/name matching, or biometric identification for contemporary people images. Ingestion of contemporary images is for internal review-gated source-corpus exploration only.

## Status Tracking & Maintenance
- **Keep STATUS.md updated:** `STATUS.md` is a mandatory project state report, not optional documentation. Always update it after any meaningful change.
- **Timestamp Contract:** `STATUS.md` must contain identical `Last updated: YYYY-MM-DD HH:MM GMT-3` lines at both the top and the bottom of the file (using Montevideo/GMT-3 timezone by default).

## Verification Commands
Always run the narrowest reliable verification commands after making changes:

- **Type-check / Compilation:**
  ```bash
  .venv/bin/python -m compileall src tests scripts
  ```
- **Backend Tests:**
  ```bash
  .venv/bin/python -m pytest -q
  ```
- **Frontend Build:**
  ```bash
  npm --prefix frontend run build
  ```
- **Script Validation & Git Check:**
  ```bash
  zsh -n start.sh
  git diff --check
  ```
