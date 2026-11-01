# QHI AUTO Master Plan

## Objective
Deliver an extensible commercial platform for electric vehicles sourced in China and delivered to Dushanbe. Publish real availability, tariffs, legal claims, prices, delivery dates, and documents only after owner verification.

## Milestones
- [x] Project, Python environment, local Node/Git, and PostgreSQL diagnostics.
- [x] Architecture, directory layout, and security baseline.
- [x] Initial API, catalog/pricing models, migration, and tariff-safe calculator.
- [x] Localized responsive catalog and public cost-quote/enquiry forms (ru/tg/en source); build awaits npm registry access.
- [ ] Install frontend dependencies from a lockfile, build, and typecheck (npm registry currently returns EACCES).
- [ ] Apply migrations and run integration tests after `DATABASE_URL` is configured privately. Current migration head: `0009_crm_analytics_indexes`.
- [x] Initial API-key-protected admin catalog/tariff management and audit trail.
- [x] Public itemized tariff-backed quote and rate-limited CRM enquiry API/UI source.
- [x] Admin surfaces for catalog, tariffs, customer/staff role management; bootstrap-key auth remains transitional.
- [x] Customer identity, profiles, favorites, and persisted comparisons API; account and catalog controls are wired in source but need a real frontend build.
- [x] Backend order creation, ownership, status transitions, and event timeline.
- [x] Staff order/logistics status management and persistent customer in-app notifications linked to public order events; account UI source exists but awaits frontend build.
- [x] Staff document upload and owner/visibility-checked download API, with bounded local storage, type validation, and integrity metadata.
- [ ] Production object storage, malware scanning, retention, and restore verification for order documents.
- [x] Backend CRM leads, interactions, manager assignments, and status counts.
- [x] Localize the initial CRM management UI and provide active manager selection.
- [x] Add staff-only date-bounded CRM analytics for lead cohort conversion, sources, manager workload, order statuses, and quote estimates.
- [ ] Verify CRM analytics in a browser and add event-time attribution where business definitions require conversion-date reporting.
- [ ] Review localization quality across all screens, accessibility, performance, and security checks. Admin catalog/tariff/customer-role screens now have ru/tg/en dictionaries; browser verification remains pending.
- [ ] Deployment, backup/restore, monitoring, and operations guide.

## Working method
Deliver vertical slices. Run the relevant tests after each change, record only real results in `docs/DEVELOPMENT_STATUS.md`, and commit working checkpoints. Do not invent commercial/legal data. Keep user-owned files outside the Git checkpoint unless required.

## Current blockers
npm registry access returns EACCES. PostgreSQL service is running, but `DATABASE_URL` and `backend/.env` are absent. Keep implementation moving on tasks that do not depend on these blockers.
