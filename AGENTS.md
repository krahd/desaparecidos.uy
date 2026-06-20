# AGENTS.md

Repository instructions for AI coding agents working in this project.

This file is the durable source of truth for GitHub Copilot, OpenAI Codex, Claude Code, and other compatible coding agents. Read it before making changes. Follow the most specific applicable instruction when several instruction files exist.

## 1:  Non-negotiable rules

- Keep `STATUS.md` accurate at all times.
- `STATUS.md` must exist in the repository root. If it is missing, create it before finishing any task that changes the project.
- Do not finish a task that changes the project without reviewing and, when needed, updating `STATUS.md`.
- Do not invent project facts. Inspect the repository and record uncertainty explicitly.
- Do not overwrite user work or unrelated changes.
- Do not commit secrets, credentials, tokens, private keys, local environment files, database dumps, saved user data, or generated sensitive data.
- Do not add new production dependencies without a clear need and without documenting why.
- Prefer small, focused changes over broad rewrites.
- Preserve existing project style unless the task explicitly asks for a style change.
- Verify meaningful changes with the narrowest reliable test, lint, type-check, build, or run command available.
- If verification cannot be run, document the reason in the final response and in `STATUS.md` when relevant.
- Do not claim that tests, builds, smoke tests, linters, type-checkers, or manual checks passed unless they were actually run.

## 2:  Communication style

Use terse, factual, technical communication.

Do not use playful, whimsical, cute, decorative, or filler progress phrases.

Do not say things like:

- "combobulating"
- "cooking"
- "thinking..."
- "working on it"
- "let me dive in"
- "I'll get started"
- "working my magic"

Allowed status-update style:

- "Reading files."
- "Found the issue."
- "Applying patch."
- "Tests passed."
- "Tests failed: <reason>."

Rules:

- No decorative progress messages.
- No jokes, metaphors, or playful status words.
- No anthropomorphising the process.
- No fake enthusiasm.
- No "I'm going to..." unless asking for confirmation.
- Prefer concise present-tense technical updates.
- Use British English for prose documentation unless the repository already uses another variant consistently.
- When using tools, report only meaningful findings, blockers, or completed changes.
- Provide the result directly for short tasks.
- For long tasks, provide only terse factual status updates.

Bad:

- "Combobulating the codebase..."
- "Let me cook."
- "Working my magic."

Good:

- "Inspecting the failing test."
- "Found one failing import."
- "Updated the config."

## 3:  Standard work loop

For every task:

1. Read this file and any more specific `AGENTS.md` files that apply to the files being edited.
2. Inspect the repository before changing files.
3. Read `STATUS.md` early to understand current project state, risks, validation status, and next steps.
4. Identify the smallest safe change that satisfies the request.
5. Search for all relevant call sites before changing public functions, routes, schemas, commands, or configuration keys.
6. Make focused edits.
7. Run relevant verification when possible.
8. Update documentation when behaviour, setup, architecture, commands, or public APIs change.
9. Update `STATUS.md` if the project state changed.
10. Report changed files, verification performed, and any remaining issues.

For complex work:

- Explore first, then plan, then edit.
- Keep the plan short and operational.
- Re-check assumptions against files, tests, and documentation.
- Prefer incremental patches that can be reviewed independently.
- Do not continue broad refactors when a narrow fix is sufficient.

## 4:  Repository discovery

When the project structure is not yet known:

- List top-level files and directories.
- Read `README.md`, `STATUS.md`, package/build files, and existing docs before editing.
- Identify the language, framework, package manager, test runner, formatter, lint/type-check tools, and CI workflows from repository files.
- Prefer fast search tools such as `rg` when available.
- Do not assume commands from other repositories apply here.
- Treat generated files, build outputs, local caches, virtual environments, and release artifacts as non-source unless the repository clearly tracks them intentionally.

Common files to inspect when present:

- `README.md`
- `STATUS.md`
- `pyproject.toml`, `requirements.txt`, `Pipfile`, `environment.yml`, `pytest.ini`, `tox.ini`, `noxfile.py`
- `package.json`, `pnpm-lock.yaml`, `yarn.lock`, `package-lock.json`
- `Cargo.toml`, `go.mod`, `pom.xml`, `build.gradle`, `settings.gradle`
- `Makefile`, `justfile`, `Taskfile.yml`
- `.github/workflows/*`
- Docker and compose files
- `docs/`, `examples/`, `scripts/`, `tests/`
- release files such as `CHANGELOG.md`, `RELEASE.md`, `VERSION`, release notes, or package metadata

## 5:  Project-specific map

Each repository should keep this section useful. Replace the placeholders below with real project information as soon as it is known.

### 5.1:  Project shape

- Purpose: `desaparecidos.uy` is a computational memorial artwork triptych about detained-disappeared persons connected to Uruguay: **Todos somos familiares** (internal face-fragment work), **Están en todas partes** (current place-fragment prototype), and **Seguimos buscando** (search/traversal work).
- Main runtime surfaces: localhost-only web GUI, FastAPI backend, reusable Python pipeline, and CLI entry points.
- Primary languages/frameworks: Python, FastAPI, Pillow, NumPy, OpenCV for optional MP4 writing, React, Vite, and TypeScript.
- Supported platforms: local development on macOS first; the Python pipeline should remain portable where practical.

### 5.2:  Important paths

- `README.md`: human-facing overview and start-here documentation.
- `STATUS.md`: complete current project status report; mandatory upkeep.
- `docs/`: user-facing and maintainer-facing documentation, when present.
- `tests/`: automated verification, when present.
- `scripts/`: development, validation, release, or maintenance helpers, when present.

- `pyproject.toml`: Python package metadata, dependencies, and CLI entry point.
- `src/desaparecidos/`: Python pipeline, CLI, and local API.
- `frontend/`: React/Vite localhost GUI.
- `data/manifests/`: tracked manifest templates and examples only.
- `data/manifests/people.csv`: tracked empty template for internal Stage 2 contemporary people-source review.
- `data/manifests/crawled-*.csv`: ignored crawler-produced review manifests, including `crawled-places.csv` and `crawled-people.csv`.
- `data/persons/disappeared.json`: canonical disappeared-person target corpus store, tracked after review; it drives the target administration GUI and derived target manifest export.
- `data/persons/metadata-overrides.csv`: tracked, reviewed per-field metadata corrections with source ids and references; apply it with `scripts/apply_person_metadata_overrides.py --write`.
- `data/raw/`: ignored downloaded or local source imagery.
- `data/raw/crawl/`: ignored crawler cache — content-addressed image store under `store/` plus a SQLite index (`cache.sqlite`).
- `data/processed/`: ignored processed local derivatives, including 3:4 target portrait copies generated from `doc/fotos-desaparecidos/`.
- `doc/fotos-desaparecidos/`: curated source portraits of the disappeared, tracked intentionally as foundational material for the work (the redundant `doc/fotos-desaparecidos.zip` archive is ignored).
- `data/raw/crawl/runs/`: ignored JSONL crawl-trail exports used by generated process videos.
- `assets/targets/disappeared/selected/`: reviewed selected 3:4 portrait derivatives for the target corpus; raw downloads and generated candidates remain ignored.
- `data/persons/disappeared-sitios-de-memoria.*`, `assets/targets/disappeared/raw/`, `assets/targets/disappeared/processed/`, and `data/manifests/targets-sitios-de-memoria.csv`: ignored legacy/importer working outputs.
- `data/sources.json`: tracked registry of authoritative sources and review-only candidate corpora; person records reference authoritative ids in their `field_sources` provenance map.
- `outputs/stage1/`: ignored generated stills, videos, and sidecar metadata.
- `scripts/`: local helper scripts.
- `scripts/audit_target_corpus.py`: target-corpus audit command for selected-portrait coverage, portrait-review needs, missing fields, portrait source counts, and unresolved person records.
- `scripts/apply_person_metadata_overrides.py`: applies reviewed metadata corrections from `data/persons/metadata-overrides.csv`, preserving `field_sources`, `field_source_refs`, and source paths.
- `scripts/suggest_local_portrait_matches.py`: review-only matcher from `data/manifests/local-targets.csv` / `doc/fotos-desaparecidos` to canonical person records; it may append candidates but must not auto-select portraits.
- `start.sh`: launcher script for the local GUI.

### 5.3:  Safety invariants

- Keep the GUI and API bound to localhost unless the user explicitly requests another deployment mode.
- Do not commit raw source imagery, rejected candidates, generated outputs, fragments, downloaded files, or review-sensitive crawler data. This rule targets transient crawler/download outputs (ignored under `data/raw/`) and local processed copies (ignored under `data/processed/`). The curated source portraits in `doc/fotos-desaparecidos/`, canonical metadata in `data/persons/disappeared.json`, and reviewed selected derivatives in `assets/targets/disappeared/selected/` are intentional, trackable corpus files; do not untrack or remove them without explicit instruction. Generated manifests of real people belong on ignored `data/manifests/local-*.csv` paths unless deliberately exported as the canonical `data/manifests/targets.csv`.
- Require `review_status=approved` before any source image participates in Stage 1 generation.
- Keep provenance metadata with every downloaded input and generated output.
- Treat historical target images respectfully: do not claim enhancement, recovery, or forensic reconstruction.
- Validate paths stay inside the project root for API file access.
- Keep crawling seeded by explicit user-supplied or approved preset pages, localhost-only operation, ignored raw files, pending manifest rows, depth/page/image caps, same-domain preset defaults, a per-host politeness delay, `robots.txt` by default, and manual approval before generation.
- Preserve exact and perceptual dedupe so repeated image variants do not become repeated manifest rows.
- Keep `targets` for disappeared-person portraits only. Contemporary public images of people belong in `people` manifests for internal Stage 2 review and must not be treated as disappeared-person targets.
- Keep target administration in the person store first. `targets.csv` is a generation-compatible export, not the canonical person database.
- Keep death metadata distinct from disappearance metadata. Use `date_of_death` and `place_of_death` for killed cases; only use disappearance fields when the source actually supports disappearance/detention data. Derived target manifests may fall back to death date/place for display/export compatibility.
- Treat local portrait filename matches as candidate evidence only. Raw-only candidates must not become selected portraits until reviewed and processed into `assets/targets/disappeared/selected/`.
- Do not add identity-seeking behaviour, face/name matching, or biometric identification for contemporary people images.
- Treat public availability as insufficient consent for arbitrary processing. For contemporary people imagery, exclude minors, private contexts, and sensitive contexts such as schools, hospitals, prisons, shelters, protests, funerals, religious ceremonies, political meetings, health, criminal justice, and education unless explicit permission exists.
- Computer-vision gating must require real detected faces for `targets` and `people`; do not use fallback face boxes. `places` gating must prefer photo-like non-face scene material and reject obvious graphics, logos/posters, prominent faces, and noise-like textures. CV never auto-approves rows and never identifies people.
- Crawled images, a SQLite index, image-event trails, and JSONL page-trail exports are persisted on disk under ignored `data/raw/crawl/` so the crawler does not re-download and videos can replay the search trail and fast non-contributing candidate scan. This local persistence is intentional for now; it is not committed to git, and the persistence policy may be revisited once the workflow is settled.

Do not weaken safety invariants without explicit user instruction and documentation.

## 6:  `STATUS.md` maintenance

`STATUS.md` is mandatory project state, not optional documentation.

Update `STATUS.md` whenever a meaningful project change occurs, including changes to:

- code behaviour
- architecture
- public APIs, command-line interfaces, routes, schemas, or data contracts
- dependencies or lockfiles
- configuration, settings, environment variables, or secrets handling
- setup, run, build, package, or release instructions
- tests, verification status, CI, or known test gaps
- repository structure
- documentation that affects usage or development
- known issues, risks, limitations, or residual verification gaps
- pending tasks, next steps, or long-term direction
- implementation status
- important design decisions and rationale

Do not update `STATUS.md` for purely trivial changes that do not alter project state, such as typo-only edits in comments, unless the task specifically asks for documentation maintenance.

### 6.1:  Required `STATUS.md` timestamp

`STATUS.md` must contain a `Last updated` line near the top:

```text
Last updated: YYYY-MM-DD HH:MM GMT+-X
```

Rules:

- Use exactly the format above, replacing the timestamp values.
- Use 24-hour time.
- Use the user's local timezone, specify it with a GMT+-X (e.g. GMT-3 for Montevideo)
- Get the current local time from the system or environment when possible; do not guess timestamps.
- Use hyphens between date parts and colon between hour/minute parts.
- Do not include seconds.
- Duplicate the exact same `Last updated` line as the final line at the very bottom of `STATUS.md`.
- When updating `STATUS.md`, update both the top and bottom `Last updated` lines in the same edit.
- The top and bottom `Last updated` lines must match exactly.
- Treat missing, stale, malformed, or mismatched `Last updated` lines as a blocking documentation error for any task that changes project state.

### 6.2:  Required `STATUS.md` content

`STATUS.md` must be a complete project status report, not a short changelog.

Include the following sections where relevant:

- Project purpose
- Current implementation state
- Active focus
- Architecture overview
- Setup and run instructions
- Configuration and environment variables
- Important files and directories
- Current capabilities
- Recent changes
- Tests and verification status
- Known issues, risks, and limitations
- Pending tasks
- Next steps
- Longer-term steps
- Decisions and rationale
- Documentation alignment notes

Keep the report current and useful for the next agent or human developer opening the repository.

## 7:  Starter `STATUS.md` policy

Prefer committing a barebones root-level `STATUS.md` when a repository is created instead of asking the first agent to invent it.

A starter `STATUS.md` should include:

- project title
- correctly formatted top `Last updated` line
- purpose placeholder
- current state placeholder
- setup/run placeholder
- architecture overview placeholder
- important files placeholder
- verification status placeholder
- known issues placeholder
- next steps placeholder
- long-term steps placeholder
- diagram placeholders or initial diagrams when meaningful
- matching final `Last updated` line at the bottom

Agents may expand the starter file after inspecting the repository, but they must preserve the timestamp contract and keep the report factual.

## 8:  Diagrams in `STATUS.md`

`STATUS.md` must include useful inline SVG diagrams when the project has enough structure for them to be meaningful.

Include, where relevant:

- at least one architecture diagram
- at least one flow chart, execution-flow diagram, or data-flow diagram

The diagrams must represent the current project accurately. Do not add generic filler diagrams.

SVG rules:

- Embed SVG directly in `STATUS.md`; do not rely on external image files for the required diagrams.
- Keep all text inside its intended box.
- Keep all text inside the SVG canvas.
- Keep arrows and connector lines out of unrelated boxes and labels.
- Ensure connected arrows terminate cleanly at shape boundaries.
- Make the SVG canvas larger when needed for spacing and legibility.
- Prefer generous spacing over compactness.
- Use simple, maintainable SVG primitives: `svg`, `g`, `rect`, `line`, `path`, `text`, `defs`, `marker`, `title`, `desc`.
- Avoid overlapping text, arrows, boxes, and labels.
- Avoid cramped labels.
- Keep labels concise.
- Include a short text explanation immediately before or after each SVG so the status report remains useful in plain-text views.
- Prefer accessible SVG structure where practical, including `<title>` and `<desc>` elements.
- Prioritise correctness, legibility, and maintainability over decoration.
- Update diagrams when architecture, module relationships, data flow, execution flow, or deployment shape meaningfully changes.
- Avoid trivial diagram edits when no relevant structural or flow change has occurred.

Before finishing diagram edits, visually inspect the SVG text positions, box sizes, arrow routing, and canvas bounds.

If the repository stores generated or large diagrams outside Markdown for human docs, `STATUS.md` may link to them too, but the required status diagrams should remain inline unless the user explicitly changes this policy.

## 9:  Coding standards

- Follow existing style, naming, layout, and architecture.
- Prefer clear, maintainable code over clever code.
- Keep functions and modules focused.
- Avoid unrelated refactors.
- Avoid formatting-only churn unless formatting is the task or required by tooling.
- Preserve public APIs unless the task explicitly requires changing them.
- Preserve data formats, route contracts, CLI flags, config keys, file formats, and public exports unless a breaking change is explicitly requested.
- Handle errors deliberately; do not hide failures with broad silent catches.
- Keep logging useful and non-noisy.
- Add comments only when they explain non-obvious decisions, constraints, or trade-offs.
- Remove dead code only when it is clearly unused and removal is within task scope.

## 10:  Tests and verification

Use the narrowest reliable verification first, then broaden when appropriate.

Preferred order:

1. Targeted unit test or focused command for the changed area.
2. Relevant lint/type-check/format check.
3. Broader test suite when change risk justifies it.
4. Build/package check for release, packaging, or distribution changes.
5. Manual run or smoke test when automated coverage is unavailable.

Rules:

- Add or update tests for behavioural changes when the repository has a test pattern.
- Do not delete failing tests to make a suite pass.
- If tests fail, distinguish failures caused by your change from pre-existing failures when possible.
- Record verification commands and outcomes in the final response.
- Do not claim that tests, linting, type-checking, builds, or smoke tests passed unless they were actually run.
- Record verification status in `STATUS.md` when it affects project state, release readiness, risk, or pending work.
- If real external validation is required but not run, record it as unverified, not as passed.

Project-specific validation commands:

```bash
python -m compileall src tests
python -m pytest -q
npm --prefix frontend run build
```

## 11:  Dependencies

Before adding a dependency:

- Check whether the repository already has a suitable dependency.
- Prefer standard-library or existing project utilities when reasonable.
- Confirm the package manager and lockfile in use.
- Document why the dependency is needed.
- Update lockfiles using the repository's normal package manager when possible.
- Consider security, maintenance, licence, size, and transitive impact.

Do not add dependencies only for trivial convenience.

## 12:  Security and privacy

- Never expose, print, commit, or fabricate secrets.
- Treat `.env`, credential files, private keys, tokens, database dumps, saved user data, local model caches, and user-generated content as sensitive unless the repository clearly treats them as test fixtures.
- Do not weaken authentication, authorisation, validation, sandboxing, confirmation prompts, or permission checks unless explicitly requested and justified.
- Avoid introducing command injection, path traversal, unsafe deserialisation, cross-site scripting, SQL injection, insecure random values, or insecure temporary-file handling.
- Validate external inputs at trust boundaries.
- Keep generated logs and errors free of unnecessary sensitive data.
- For tools that mutate filesystems, mailboxes, external services, DAWs, model runtimes, or user data, preserve preview, confirmation, backup, dry-run, and undo safeguards where present.

## 13:  Git and file safety

- Check worktree state before large edits when possible.
- Do not overwrite files that contain user changes unrelated to the task.
- Do not run destructive commands such as `rm -rf`, `git reset --hard`, `git clean -fd`, or force-push unless explicitly instructed.
- Do not create commits, branches, tags, releases, or pull requests unless explicitly asked.
- Keep generated files out of version control unless the project already tracks them or the task requires them.
- Respect `.gitignore` and existing repository conventions.
- Stage explicit paths only when staging is requested and the worktree is mixed.

## 14:  Documentation

Update documentation when behaviour, setup, commands, configuration, architecture, public APIs, or user-facing workflows change.

Documentation should be:

- accurate
- concise
- actionable
- consistent with the repository's terminology
- free of stale claims

Prefer linking to existing canonical docs over duplicating long explanations.

When capabilities, APIs, prompts, or workflows change, search for all affected documentation copies and keep them aligned.

## 15:  Versioning, releases, and packaging

When a task touches versioning, packaging, or release readiness:

- Identify every source of version truth before editing.
- Update package metadata, source constants, installers, changelog/release notes, docs, and `STATUS.md` consistently.
- Run or document relevant build/package checks.
- Do not create tags, releases, or publish packages unless explicitly asked.
- Record release blockers, failed publish steps, manual fallbacks, and external verification gaps in `STATUS.md`.

Project-specific version files should be listed here when known:

- `<version file>`
- `<package metadata>`
- `<release notes/changelog>`

## 16:  Compatibility with multiple agents

This repository may be edited by different coding agents.

Rules:

- Keep instructions plain Markdown and tool-agnostic where possible.
- Do not rely on one agent's private memory or proprietary feature for critical project knowledge.
- Put durable project knowledge in tracked files such as `AGENTS.md`, `STATUS.md`, `README.md`, and docs.
- If nested `AGENTS.md` files exist, apply the most specific relevant instructions for the files being changed.
- When instructions conflict, follow this priority order:
  1. Direct user request for the current task
  2. More specific nested `AGENTS.md`
  3. Root `AGENTS.md`
  4. Other repository documentation
  5. Existing code conventions

## 17:  Optional compatibility files

`AGENTS.md` should remain complete on its own.

If the repository uses tool-specific compatibility entry points such as `CLAUDE.md`, `.github/copilot-instructions.md`, `GEMINI.md`, or Cursor rules, keep them short and point back to this file unless the tool requires otherwise.

Do not allow compatibility files to drift into conflicting policy.

## 18:  Instruction-file maintenance

When maintaining this file:

- Keep it durable and repository-wide.
- Keep rules specific enough to change agent behaviour.
- Remove rules that become obsolete.
- Prefer concise bullets over long prose.
- Do not add volatile project status here; put changing status in `STATUS.md`.
- Keep project-specific details in the project map, validation, safety, and release sections.

## 19:  Final response requirements

When finishing a task, report concisely:

- what changed
- files changed
- verification commands run and results
- whether `STATUS.md` was updated
- remaining issues, blockers, or follow-up work

Do not include decorative commentary.
