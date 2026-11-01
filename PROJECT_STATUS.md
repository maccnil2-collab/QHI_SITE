# QHI AUTO project status

Updated: 2026-11-01

## Current checkpoint

- Git branch: `main`
- Latest code checkpoint: `1c9cd11` (`Load local environment for Alembic commands`)
- Existing user file: untracked root `test.txt`; preserve unchanged.

## Working and implemented

- FastAPI backend with catalog, quote snapshots, identity/sessions, customer account data, orders/events/notifications, CRM, admin APIs, and readiness endpoints.
- Browser session cookies are HttpOnly and host-only; session tokens are stored as SHA-256 digests and unsafe cookie requests require a session-bound CSRF value.
- RU/Tajik/EN source localization (`ru`, `tg`, `en`) and screens for catalog, account, CRM, and admin areas.
- Localized vehicle detail page/API added; catalog links to detail pages. Quote calculation now uses the session-aware CSRF client so signed-in estimates are associated with the customer's history.
- ESLint flat config and Playwright desktop/mobile tests configured for locale/detail, registration/session restore, quote/order, CRM, and admin flows.
- Ten Alembic revisions, ending at `0010_shared_rate_limit_buckets`.
- Compose deployment starter with PostgreSQL, API, and frontend services.

## Verified in this takeover

- Backend tests: **52 passed, 1 opt-in PostgreSQL test skipped** (one dependency deprecation warning).
- Python compileall: **PASS**.
- TypeScript/TSX syntax transpilation: **PASS (22 files)** using the VS Code-bundled compiler; this is syntax-only, not a semantic typecheck.
- pip check: **PASS**.
- Isolated PostgreSQL 18.6 test database `qhi_auto_test` on loopback port 55439: **PASS**; ten migrations applied, head is `0010_shared_rate_limit_buckets`, schema check clean.
- `alembic check`: **PASS**, no model/schema differences.
- Alembic now reads ignored `backend/.env` for local commands; `alembic current` and `alembic check` both pass without exporting `DATABASE_URL` manually.
- PostgreSQL-backed API workflows: **1 passed** (auth/session/CSRF, catalog/search/detail, quote/history, favorites/comparison, order, CRM/admin access, and shared rate-limit checks across independent instances and concurrent requests).
- Local API startup from ignored `backend/.env`: **PASS**; uvicorn is running on `127.0.0.1:8000`, readiness reports the test DB connected.
- Root-level pytest invocation: **PASS** from repository root.
- Frontend npm installation: **BLOCKED** by `EACCES` reaching `registry.npmjs.org`.

## Not verified

- Next.js production build, TypeScript semantic check, frontend lint, and Playwright. Tooling is configured, but attempted commands fail because `tsc`, `next`, `eslint`, and `playwright` are not installed.
- Browser E2E, migration rollback, and backup/restore behavior.
- Docker image builds, Compose health checks, TLS proxy behavior, and production deployment.

The detailed current network/PostgreSQL diagnosis and journey matrix are in [FRONTEND_DATABASE_READINESS.md](FRONTEND_DATABASE_READINESS.md).

## Release blockers

- Restore permitted npm registry access; create/review the lockfile, resolve dependency peers, and run the existing lint/typecheck/build/E2E scripts.
- Run the configured browser journeys against the isolated PostgreSQL test database.
- Authentication, quote, lead, and document limits now use atomic PostgreSQL counters shared across API workers; hashed keys are stored in migration 0010. Still required before production: email verification/recovery, durable scanned document storage, backups and restore drills, monitoring, secret/key rotation, and deployment review.

See [PROJECT_AUDIT.md](PROJECT_AUDIT.md) for the intake audit and [DEVELOPMENT_ROADMAP.md](DEVELOPMENT_ROADMAP.md) for the ordered next work.
