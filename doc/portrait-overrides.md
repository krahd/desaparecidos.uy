# Portrait overrides

Some primary-source person pages may contain images that are not portraits of the person. A recurring case is an image attached to `Obras de interés`, `Materiales de interés`, publications, posters, audiovisual works, institutional logos, or footer material.

The import workflow therefore includes an explicit override layer:

```bash
python scripts/apply_portrait_overrides.py --overwrite
```

Run this after:

```bash
python scripts/import_sitios_memoria.py --download-images --process-images --overwrite
```

Overrides are listed in:

```text
data/manifests/portrait-overrides.csv
```

## Current override: Abeledo Sotuyo, Horacio Adolfo

The Sitios de Memoria page for `abeledo-sotuyo-horacio-adolfo` exposes a poster for *El tiempo pasa* under `Obras de interés`, not a portrait of Horacio Adolfo Abeledo Sotuyo. The override points to the Parque de la Memoria public record instead.

The override script replaces the generated `portrait_candidates` entry for the matching slug and replaces the corresponding row in `data/manifests/targets-sitios-de-memoria.csv`.

Portrait overrides remain `review_status=candidate` until manually inspected.
