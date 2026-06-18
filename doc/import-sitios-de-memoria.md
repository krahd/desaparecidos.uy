# Sitios de Memoria import

`scripts/import_sitios_memoria.py` downloads the Sitios de Memoria Uruguay forced-disappearance corpus and writes repository-local metadata and target portrait candidates.

## Outputs

```text
data/persons/disappeared-sitios-de-memoria.json
data/persons/disappeared-sitios-de-memoria.csv
data/manifests/targets-sitios-de-memoria.csv
assets/targets/disappeared/raw/<person-slug>/...
assets/targets/disappeared/processed/<person-slug>.png
```

Portraits of disappeared persons are treated as target imagery. Existing files are not deleted.

## Test import

```bash
python scripts/import_sitios_memoria.py --limit 5 --download-images --process-images
```

## Full import

```bash
python scripts/import_sitios_memoria.py --download-images --process-images
```

By default, target manifest rows are written with `review_status=candidate`. Add `--approved-targets` only after deciding that the imported portraits should be available as approved target imagery.

## Regenerate existing imported files

```bash
python scripts/import_sitios_memoria.py --download-images --process-images --overwrite
```

## Source basis

Primary source: Sitios de Memoria Uruguay.

Secondary verification source for later integration: Secretaría de Derechos Humanos para el Pasado Reciente.

## Notes

The importer records provenance for every candidate portrait and does not perform identification, classification, enhancement, or forensic reconstruction. It normalises processed derivatives to 4:5 at 1200 × 1500 pixels. Manual review remains necessary for portraits with lettering, frames, or embedded layout elements.
