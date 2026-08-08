# Cross-Repository Administration

Global repository registry, cross-domain status, and the master calendar are maintained in `krahd/tom-work-admin`.

This repository remains canonical for **desaparecidos.uy** as an artwork/research/software project: implementation, corpus and review decisions, provenance, generation behaviour, project-specific documentation, and technical/artistic state.

Paper manuscripts and publication artefacts remain canonical in `krahd/academic-writing`; submission-specific packages belong in `krahd/professional-opportunities`; grant/funding packages belong in `krahd/grant-applications`.

## Mandatory synchronisation rule

`krahd/tom-work-admin` **must be kept current** whenever work here materially changes the project's administratively meaningful state. Updating the administration repository is part of completing the change, not optional later cleanup.

Update this repository first for substantive project changes, then update `krahd/tom-work-admin` in the same work session when any of the following changes:

- project lifecycle state, scope, conceptual/artistic direction, or relationship among artwork components;
- release/version, deployment, dataset/corpus state, implementation milestone, public visibility, or major validation state;
- relationship to a manuscript, submission, grant, collaborator, repository, exhibition, dataset, or other cross-domain dependency;
- submission/publication/award outcome where it materially affects global project status or next actions;
- deadline, exhibition, presentation, travel, production date, or other material cross-domain date;
- current next action or major artistic/research/technical gate.

The URUCON submission does not close or supersede the artwork/research project.

## Ownership boundary

Keep substantive implementation, corpus/provenance records, generation behaviour, review decisions, and artistic/technical evidence here. `tom-work-admin` stores only the concise cross-repository view and must point back to canonical project sources rather than duplicate them.

## Completion check

Before considering a material project-state change complete, verify that:

1. this repository reflects the substantive change;
2. `krahd/tom-work-admin` reflects any resulting global status, date, relationship, or next-action change;
3. related domain repositories are updated when the change affects manuscripts, submissions, or grants;
4. no stale cross-domain status or date remains in `tom-work-admin`.
