# Development Status

Updated: 2026-11-01

## Implemented
- Verified Python 3.11.9 and project environment: FastAPI 0.162.0, SQLAlchemy 2.1.6, Alembic 1.20.1, Pydantic 2.14.2, psycopg 3.3.6, pytest 9.2.0; `pip check` is clean.
- Project-local Node.js 26.13.0/npm 11.20.0 and portable Git 2.56.0 are available; global PATH is unchanged. PostgreSQL 18.6 service is running and accepts connections.
- Catalog, localized car translations, filters, comparison/favorites API, configurable tariff calculator, and persisted quote snapshots. The public catalog now includes a localized itemized quote form, CRM enquiry form, and authenticated favorites/persisted-comparison controls. Anonymous quote creation is rate-limited. Customs rates and calculation basis have no defaults; incomplete tariff drafts cannot activate.
- Admin catalog, tariff, and customer/staff role screens now include Russian, Tajik, and English UI dictionaries with an in-panel language selector. Admin locale dictionary check: 73 matching non-empty keys in ru/tg/en. Frontend TS/TSX parser check: 18 files, zero syntax errors; backend pytest: 46 passed. Next build and browser behavior still require dependency installation.
- Admin API and web surfaces for creating/editing/publishing cars with enforced ru/tg/en translations, customer/staff roles, and tariff versions. Admin key is required, constant-time compared, kept in browser memory, and role changes are audited. The final active administrator cannot be removed.
- Customer API and localized account screen source: registration/login, scrypt password hashes, hashed bearer-session storage, expiry/revocation, profile edits, active-session listing and revocation, quote history, favorites, saved comparisons, order requests and cancellation. Session APIs expose no token material and enforce owner-only revocation. The UI is wired to the API but cannot be built until npm dependencies are available. Customers cannot set their own role.
- Orders API: create/list/detail/cancel within the customer's own scope; staff status changes use explicit transitions and row locks. Customer responses omit internal staff notes. Customer-visible order events create persistent in-app notifications with owner-scoped listing and read controls.
- CRM API and staff workspace source: public rate-limited lead intake, staff-only lead and interaction management, manager assignment, status workflow, and date-bounded analytics for lead cohorts/sources, manager workload, orders, and cost estimates. CRM UI supports ru/tg/en, order/logistics transitions, documents, and timelines. Conversion reports current status of leads created in the selected period; quote totals are estimates, not revenue. Browser build remains unverified.
- Order documents: staff-only upload/list/download and customer download limited to explicitly visible documents. Local filesystem storage requires explicit `DOCUMENT_STORAGE_PATH`; uploads stream with a 10 MiB size cap, per-order quotas, PDF/JPEG/PNG signature checks, opaque storage keys, SHA-256 metadata, and private attachment downloads. Object storage and malware scanning remain for production.
- Alembic migration head `0009_crm_analytics_indexes` covers catalog, pricing, quote snapshots, identity, favorites/comparison, orders/events/doc metadata, CRM, notifications, document integrity, and date-range analytics indexes.
- 46 pytest tests pass; compileall passes; all nine migrations generate PostgreSQL offline DDL. OpenAPI exposes 40 paths including analytics, document access, liveness, database readiness, customer sessions/notifications, orders, CRM, and admin endpoints. API responses receive baseline anti-sniffing, clickjacking, referrer, and permissions headers.

## Not complete or not verified
- npm registry returns EACCES. Next/React/Tailwind are only manifests/source; there is no lockfile, build, or typecheck evidence. Playwright is absent. Locale dictionaries execute under Node strip-types; account dictionaries have matching 44-key schemas and CRM dictionaries matching 85-key schemas. This is not a frontend build.
- PostgreSQL TCP readiness is confirmed, but no `DATABASE_URL` is configured in the process or `backend/.env` (only `.env.example` is present). Migrations have not been applied to the running DB; PostgreSQL transaction and integration behavior remains unverified. SQLite API tests cover document authorization/storage flow.
- Registration does not verify email yet. No outbound mail/SMS, password recovery, payment, or push-notification provider is configured; do not send transactional notices to unverified addresses.
- Document upload uses an explicitly configured private filesystem path. Production needs durable object storage, malware scanning, retention policy, and operational restore tests before real customer documents are accepted.
- Customer account/profile/order, public quote/enquiry, and CRM screens have source but no compiled browser verification. TypeScript semantic typecheck, Next production build, Playwright end-to-end checks, accessibility, and production performance/security checks remain. Source syntax was transpiled with the TypeScript compiler bundled in VS Code; this is not a typecheck.
- Staff role guards exist, but auth/admin currently use separate bearer sessions and bootstrap API key; production hardening, key rotation, distributed edge rate limiting, and audit retention need follow-up.
- There are no owner-confirmed inventory records, photos, exchange rates, or legal tariff values. None were fabricated.

## Next tasks
1. Configure `DATABASE_URL` privately, apply migrations through `0009_crm_analytics_indexes`, and run PostgreSQL integration/transaction/ownership tests.
2. Restore npm registry access, install and lock frontend dependencies, then build/typecheck and repair reported issues.
3. Install frontend dependencies when registry access is restored, then run typecheck/build and Playwright flows.
4. Implement email verification/recovery, staff session management, object storage/malware scanning, production rate limits, deployment/backup/restore/monitoring.

- Admin catalog, tariff, and customer/staff role screens now include Russian, Tajik, and English UI dictionaries with an in-panel language selector. Admin locale dictionary check: 73 matching non-empty keys in ru/tg/en. Frontend TS/TSX parser check: 18 files, zero syntax errors; backend pytest: 46 passed. Next build and browser behavior still require dependency installation.
