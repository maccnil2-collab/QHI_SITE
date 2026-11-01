# QHI AUTO Master Plan

## Objective
Deliver an extensible commercial platform for electric vehicles sourced in China and delivered to Dushanbe. Publish real availability, tariffs, legal claims, prices, delivery dates, and documents only after owner verification.

## Milestones
- [x] Project, Python environment, local Node/Git, and PostgreSQL diagnostics.
- [x] Architecture, directory layout, and security baseline.
- [x] Initial API, catalog/pricing models, migration, and tariff-safe calculator.
- [x] Localized responsive catalog source (ru/tg/en); build awaits npm registry access.
- [ ] Install frontend dependencies from a lockfile, build, and typecheck (npm registry currently returns EACCES).
- [ ] Apply migrations and run integration tests with private application DB credentials. Current migration head: `0006_crm`.
- [x] Initial API-key-protected admin catalog/tariff management and audit trail.
- [x] Admin surfaces for catalog, tariffs, customer/staff role management; bootstrap-key auth remains transitional.
- [x] Customer identity, profiles, favorites, and persisted comparisons API; account UI source added but needs a real frontend build.
- [x] Backend order creation, ownership, status transitions, and event timeline.
- [ ] Order administration UI, secure document storage, and notifications; customer order request screen source exists but is unbuilt.
- [x] Backend CRM leads, interactions, manager assignments, and status counts.
- [ ] CRM management UI and sales analytics; backend API is available.
- [ ] Complete localization, accessibility, performance, and security checks.
- [ ] Deployment, backup/restore, monitoring, and operations guide.

## Working method
Deliver vertical slices. Run the relevant tests after each change, record only real results in `docs/DEVELOPMENT_STATUS.md`, and commit working checkpoints. Do not invent commercial/legal data. Keep user-owned files outside the Git checkpoint unless required.

## Current blockers
npm registry access returns EACCES. PostgreSQL is running but requires a private password. Keep implementation moving on tasks that do not depend on either blocker.