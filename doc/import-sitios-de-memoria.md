# Sitios de Memoria import

`scripts/import_sitios_memoria.py` downloads the Sitios de Memoria Uruguay forced-disappearance corpus and writes repository-local metadata and target portrait candidates.

## Outputs

```text
data/persons/disappeared.json
data/persons/disappeared-sitios-de-memoria.csv
data/manifests/targets.csv
assets/targets/disappeared/raw/<person-slug>/...
assets/targets/disappeared/selected/<person-slug>.jpg
```

Portraits of disappeared persons are treated as target imagery. Existing files are not deleted. Raw downloads remain ignored; reviewed selected derivatives in `assets/targets/disappeared/selected/` are the trackable curated portrait corpus.

## Test import

```bash
python scripts/import_sitios_memoria.py --limit 5 --download-images --process-images
```

## Full import

```bash
python scripts/import_sitios_memoria.py --download-images --process-images
```

By default, target manifest rows are written with `review_status=pending`. Add `--approved-targets` only after deciding that the imported portraits should be available as approved target imagery.

## Regenerate existing imported files

```bash
python scripts/import_sitios_memoria.py --download-images --process-images --overwrite
```

## Portrait overrides

Some Sitios de Memoria person pages include images for related works, publications, posters, or audiovisual material rather than a portrait of the person. Those images must not be used as target portraits.

Explicit corrections live in:

```text
data/manifests/portrait-overrides.csv
```

Apply them after the main import:

```bash
python scripts/apply_portrait_overrides.py --overwrite
```

This downloads the override image, creates a processed 3:4 derivative with white borders removed, replaces the matching person's `portrait_candidates` entry in the canonical JSON, and replaces the corresponding target-manifest row.

The first override is for `abeledo-sotuyo-horacio-adolfo`: Sitios de Memoria exposed a poster for *El tiempo pasa* under `Obras de interés`; the override uses the Parque de la Memoria record instead.

## Source basis

Primary source: Sitios de Memoria Uruguay.

Secondary verification/source layer for selected corrections: Secretaría de Derechos Humanos para el Pasado Reciente and Parque de la Memoria.

## Notes

The importer records provenance for every candidate portrait and does not perform identification, classification, enhancement, or forensic reconstruction. It normalises processed derivatives to 3:4 at up to 900 × 1200 pixels by default, trimming white borders and centring on detected faces when possible. Manual review remains necessary for portraits with lettering, frames, or embedded layout elements.
