# QHI AUTO Master Plan

## Objective
Deliver an extensible commercial platform for electric vehicles sourced in China and delivered to Dushanbe. Publish real availability, tariffs, legal claims, prices, delivery dates, and documents only after owner verification.

## Milestones
- [x] Project, Python environment, local Node/Git, and PostgreSQL diagnostics.
- [x] Architecture, directory layout, and security baseline.
- [x] Initial API, catalog/pricing models, migration, and tariff-safe calculator.
- [x] Localized responsive catalog source (ru/tg/en); build awaits npm registry access.
- [ ] Install frontend dependencies from a lockfile, build, and typecheck.
- [ ] Apply migrations and run integration tests with private application DB credentials. The current migration head includes catalog, audit, and quote snapshots.
- [x] Initial API-key-protected admin catalog/tariff management and audit trail.
- [ ] Replace bootstrap admin key with user/role based access and build the web admin panel.
- [ ] Customer identity, profiles, favorites, and persisted comparisons.
- [ ] Orders, logistics events, documents, notifications.
- [ ] CRM leads, customer interactions, manager assignments, analytics.
- [ ] Complete localization, accessibility, performance, and security checks.
- [ ] Deployment, backup/restore, monitoring, and operations guide.

## Working method
Deliver vertical slices. Run the relevant tests after each change, record only real results in `docs/DEVELOPMENT_STATUS.md`, and commit working checkpoints. Do not invent commercial/legal data. Keep user-owned files outside the Git checkpoint unless required.

## Current blockers
npm registry access returns EACCES. PostgreSQL is running but requires a private password. Keep implementation moving on tasks that do not depend on either blocker.