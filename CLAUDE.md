# Claude Code Instructions

Read [AGENTS.md](AGENTS.md) before making changes. Keep [STATUS.md](STATUS.md) accurate after meaningful project changes. Use [doc/desaparecidos-uy-project-description.md](doc/desaparecidos-uy-project-description.md) as the conceptual reference for the triptych, ethics, and visual method.

This repository is a local-first computational memorial artwork prototype. Do not commit raw imagery, downloaded source files, generated outputs, credentials, caches, or local environment files. Crawled images and the crawler cache are persisted on disk under ignored `data/raw/crawl/` (intentional, so the crawler does not re-download and videos can replay the search) but are still not committed. The curated source portraits in `doc/fotos-desaparecidos/` are the one intentional exception and remain tracked. Do not add identity matching, biometric identification, or face/name matching for contemporary people images.
