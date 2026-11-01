# Development Status

Updated: 2026-11-01

## Implemented
- Verified Python 3.11.9 and project environment: FastAPI 0.162.0, SQLAlchemy 2.1.6, Alembic 1.20.1, Pydantic 2.14.2, psycopg 3.3.6, pytest 9.2.0; `pip check` is clean.
- Project-local Node.js 26.13.0/npm 11.20.0 and portable Git 2.56.0 are available; global PATH is unchanged. PostgreSQL 18.6 service is running and accepts connections.
- Catalog, localized car translations, filters, comparison/favorites API, configurable tariff calculator, and persisted quote snapshots. The public catalog now includes a localized itemized quote form, CRM enquiry form, and authenticated favorites/persisted-comparison controls. Anonymous quote creation is rate-limited. Customs rates and calculation basis have no defaults; incomplete tariff drafts cannot activate.
- Admin API and web surfaces for cars, customer/staff roles, and tariff versions. Admin key is required, constant-time compared, kept in browser memory, and role changes are audited. The final active administrator cannot be removed.
- Customer API and localized account screen source: registration/login, scrypt password hashes, hashed bearer-session storage, expiry/revocation, profile edits, quote history, favorites, saved comparisons, order requests and cancellation. The UI is wired to the API but cannot be built until npm dependencies are available. Customers cannot set their own role.
- Orders API: create/list/detail/cancel within the customer's own scope; staff status changes use explicit transitions and row locks. Customer responses omit internal staff notes.
- CRM API and initial staff workspace source: public rate-limited lead intake, staff-only lead and interaction views/edits, manager assignment, status workflow, aggregate lead/order counts, and a staff login/lead management page. UI is currently English-only and uncompiled; manager assignment uses the staff-only active manager directory.
- Alembic migration head `0006_crm` covers catalog, pricing, quote snapshots, identity, favorites/comparison, orders/events/doc metadata, and CRM.
- 27 pytest tests pass; compileall passes; all six migrations generate PostgreSQL offline DDL. A real Uvicorn process serves OpenAPI with 29 routes, including auth, order, CRM, and admin endpoints.

## Not complete or not verified
- npm registry returns EACCES. Next/React/Tailwind are only manifests/source; there is no lockfile, build, or typecheck evidence. Playwright is absent. Locale dictionaries execute under Node strip-types and have matching 29-key account dictionaries; this is not a frontend build.
- PostgreSQL TCP readiness is confirmed, but authentication needs a private password. Migrations have not been applied to the running DB; SQLAlchemy CRUD, transaction, and PostgreSQL integration tests remain unverified.
- Registration does not verify email yet. No outbound mail/SMS, password recovery, payment, or push-notification provider is configured; do not send transactional notices to unverified addresses.
- Order-document table is metadata only; secure object storage/upload/download is not integrated.
- Customer account/profile/order, public quote/enquiry, and initial CRM screens have source but no compiled browser verification. CRM translations, TypeScript semantic typecheck, Next production build, Playwright end-to-end checks, accessibility, and production performance/security checks remain. Source syntax was transpiled with the TypeScript compiler bundled in VS Code; this is not a typecheck.
- Staff role guards exist, but auth/admin currently use separate bearer sessions and bootstrap API key; production hardening, key rotation, distributed edge rate limiting, and audit retention need follow-up.
- There are no owner-confirmed inventory records, photos, exchange rates, or legal tariff values. None were fabricated.

## Next tasks
1. Connect to PostgreSQL using credentials stored privately in `backend/.env`, apply migrations, and run real DB integration/transaction/ownership tests.
2. Restore npm registry access, install and lock frontend dependencies, then build/typecheck and repair reported issues.
3. Localize the CRM UI, install frontend dependencies when registry access is restored, then run typecheck/build and Playwright flows.
4. Implement email verification/recovery, staff session management, secure document storage, production rate limits, deployment/backup/restore/monitoring.
