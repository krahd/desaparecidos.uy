# Auditoría de código para postulación al 62.º Premio Nacional de Artes Visuales 2026

Fecha: 2026-07-08  
Rama: `submission-premio-nacional-2026`  
Objetivo: evaluar la viabilidad técnica y los riesgos de presentar `desaparecidos.uy` como una única obra-tríptico compuesta por tres videos generados offline y exhibidos en tres pantallas verticales.

---

## 1. Conclusión ejecutiva

La propuesta de montaje no interactivo es técnicamente viable y reduce riesgos. El repositorio ya permite generar videos MP4 offline para los tres modos de obra: **Todos somos familiares**, **Están en todas partes** y **Seguimos buscando**. La exhibición como tres loops en tres pantallas evita depender de la GUI, de FastAPI, de Mapillary, de internet o de procesos de adquisición durante la muestra.

El riesgo principal no es técnico sino de derechos/fuentes: para la versión final de exhibición hay que asegurar que todos los insumos visuales usados en los tres videos tengan revisión suficiente respecto de derechos de autor, derecho de imagen, datos personales, términos de uso y contextos sensibles. Esto es especialmente importante para **Todos somos familiares**, porque trabaja con imágenes de personas contemporáneas.

---

## 2. Estado técnico relevante

### 2.1. Arquitectura

- La aplicación es local-first y localhost-only.
- La GUI React/Vite llama a un backend FastAPI local.
- La generación se realiza en Python y escribe archivos locales ignorados por git.
- La salida expositiva puede ser sólo video: PNG/MP4/JSON sidecar.
- No hace falta ejecutar la aplicación en sala si los videos finales se renderizan antes.

### 2.2. Tres modos de obra

- **Todos somos familiares** usa fuentes de tipo `people` y extrae fragmentos desde regiones de rostro revisadas.
- **Están en todas partes** usa fuentes de tipo `places` y fragmentos de imágenes de lugares/superficies.
- **Seguimos buscando** usa recorridos y frames de traversal; puede renderizar videos a 1920 px / 24 fps por defecto.

### 2.3. IA / visión computacional

La obra no depende de modelos generativos para crear rostros. El núcleo actual usa:

- OpenCV/NumPy para filtros locales no identificatorios;
- fragmentos no superpuestos;
- descriptor manual de seis dimensiones: RGB medio, contraste de luminancia y energía de borde horizontal/vertical;
- búsqueda determinista L2 de vecino más cercano;
- límites de reutilización de fragmentos y contribución por fuente;
- sidecars JSON con metadatos de generación y procedencia.

Esta formulación debe usarse en la carpeta de postulación. Deben evitarse expresiones como “restauración por IA”, “reconstrucción generativa de rostros” o “deepfake”.

---

## 3. Lenguaje obsoleto detectado

### 3.1. Límite por fuente

Lenguaje obsoleto encontrado en documentos de trabajo:

- “default ceiling of 240 fragments per source image”
- “normalises zero or unset values to a default cap of 240”

Estado actual del código:

- `DEFAULT_MAX_CONTRIBUTION_PER_SOURCE = 1`.
- `Stage1Settings.max_contribution_per_source` usa ese valor por defecto.
- `0` significa uso ilimitado sólo cuando se lo especifica explícitamente.
- La generación con fuentes `people` rechaza `max_contribution_per_source = 0`.

Lenguaje corregido para usar en postulación:

> El sistema permite limitar cuántos fragmentos puede aportar una misma imagen fuente. En la configuración por defecto, cada fuente aporta como máximo un fragmento al retrato final; el uso ilimitado sólo existe como opción explícita para pruebas con imágenes de lugares y no se admite en la generación con fuentes de personas.

### 3.2. Videos de proceso y candidatos rechazados

Lenguaje obsoleto encontrado en documentos de trabajo:

- “local crawl candidates that do not contribute are flashed quickly”
- “candidate rejection” como imagen mostrada en el video final

Estado actual del código:

- Los candidatos rechazados o no contribuyentes no se muestran como imágenes crudas en los videos activos.
- Los videos muestran fuentes aprobadas que sí contribuyen.
- En `people`, el modo actual muestra sólo la región de rostro revisada, no la fotografía completa.
- El sidecar registra conteos de candidatos, selección y omisión sin mostrar imágenes rechazadas.

Lenguaje corregido para usar en postulación:

> Los videos de proceso muestran únicamente fuentes revisadas y contribuyentes. Los candidatos rechazados o no utilizados quedan registrados en metadatos internos, pero no aparecen como imágenes en la versión expositiva.

---

## 4. Riesgos para la postulación

### 4.1. Derechos de imagen en **Todos somos familiares**

Riesgo: el modo actual de video para fuentes `people` puede revelar la región de rostro revisada de una persona contemporánea antes de fragmentarla. Aunque el sistema no identifica ni clasifica a esa persona, la exhibición pública de una región de rostro podría activar problemas de derecho de imagen, consentimiento, contexto sensible o datos personales.

Mitigaciones recomendadas antes de generar el loop final:

1. usar sólo imágenes de personas con autorización explícita; o
2. modificar/generar la versión expositiva para que no revele rostros fuente reconocibles, sino sólo fragmentos; o
3. reemplazar ese canal por una versión en la que las fuentes humanas sean propias, consentidas, institucionalmente autorizadas o visualmente no identificables.

Este punto debe resolverse antes de cerrar el PDF y antes de exportar el video final de **Todos somos familiares**.

### 4.2. Fuentes de lugares y recorridos

Riesgo: imágenes de lugares, Mapillary u otras fuentes pueden tener términos de uso, atribución o restricciones de redistribución.

Mitigaciones:

- preferir material propio, autorizado, de dominio público, CC compatible o institucionalmente reusable;
- mantener atribución y procedencia en sidecars;
- no depender de URLs temporales en la exhibición;
- exportar videos finales como archivos autónomos;
- revisar si los términos de Mapillary permiten el tipo de uso expositivo/documental previsto.

### 4.3. Declaración de IA

Las bases exigen declarar si se usó inteligencia artificial y especificar herramientas/base de datos o insumos. La formulación más segura es declarar uso de IA/visión computacional en sentido restringido, con software propio, sin IA generativa de rostros, sin síntesis de identidad, sin deepfake y sin entrenamiento de modelos con los insumos.

---

## 5. Viabilidad del montaje propuesto

El montaje de tres pantallas verticales es adecuado para la convocatoria porque:

- presenta una unidad conceptual clara;
- no exige interacción ni mantenimiento de software en sala;
- puede adaptarse a pantallas, monitores o proyecciones;
- es compatible con dimensiones variables;
- permite itinerancia si los tres videos se entregan como archivos reproducibles;
- reduce la dependencia de hardware específico, red o ejecución local.

Recomendación técnica para carpeta:

- proponer tres pantallas verticales de 55–75 pulgadas;
- declarar dimensiones variables;
- entregar videos MP4/H.264;
- sonido opcional o muy bajo;
- no exigir internet;
- no presentar la GUI como parte necesaria de la obra.

---

## 6. Pendientes técnicos antes de envío

1. Exportar un loop final por cada pantalla.
2. Definir duración exacta de cada loop.
3. Confirmar resolución final: idealmente 1080×1920 o superior si las pantallas son verticales.
4. Revisar manualmente los tres videos completos antes de usarlos en la postulación.
5. Seleccionar stills representativos comprimidos para el PDF.
6. Generar un enlace externo estable para ver los videos completos si la plataforma lo permite.
7. Asegurar que el canal **Todos somos familiares** no exponga rostros fuente reconocibles sin autorización.
8. Confirmar derechos/términos de todas las fuentes usadas para los videos finales.

---

## 7. Verificación realizada

Esta auditoría se realizó por inspección estática del repositorio mediante lectura de documentación y archivos de código relevantes. No se ejecutaron tests, builds ni renderizados en esta sesión.

Archivos inspeccionados directamente:

- `README.md`
- `AGENTS.md`
- `STATUS.md`
- `pyproject.toml`
- `frontend/package.json`
- `src/desaparecidos/pipeline.py`
- `src/desaparecidos/api.py`
- `src/desaparecidos/cli.py`
- `src/desaparecidos/traversals.py`
- `doc/desaparecidos-uy-project-description.md`

Comandos recomendados para verificación local antes de cerrar la carpeta:

```bash
.venv/bin/python -m compileall src tests scripts
.venv/bin/python -m pytest -q
npm --prefix frontend run build
zsh -n start.sh
git diff --check
```
