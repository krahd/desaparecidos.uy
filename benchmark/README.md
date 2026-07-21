# URUCON 2026 benchmark

This directory contains the independent proxy benchmark and verification artifact for **Bounding and Auditing Source Participation in Fragment-Based Image Synthesis**.

The benchmark is analytically separate from the memorial corpus. It uses only example images distributed with scikit-image and contains no memorial portraits, contemporary source corpus, downloaded crawler output, or crawled source manifests.

## Reproduce the reported values

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r benchmark/requirements.txt
python benchmark/reproduce.py
```

The script regenerates the 432-run proxy experiment, parent-level concentration analysis, reduced greedy-versus-exact comparison, and an independent source-dependency/regeneration diagnostic. It writes `benchmark-results.json` and verifies the values reported in the paper against numerical tolerances. The committed `reported-results.json` records the corresponding reference output.

GitHub Actions also runs the production test suite and this benchmark on changes to the relevant code or artifact files.
