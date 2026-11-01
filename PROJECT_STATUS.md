# QHI AUTO project status

Updated: 2026-11-01

## Current checkpoint

- Git branch: `main`
- Intake commit: `666ff552d5bd6fb0545ceaf3fcd33ef06e4f9169`
- Existing user file: untracked root `test.txt`; preserve unchanged.

## Working and implemented

- FastAPI backend with catalog, quote snapshots, identity/sessions, customer account data, orders/events/notifications, CRM, admin APIs, and readiness endpoints.
- Browser session cookies are HttpOnly and host-only; session tokens are stored as SHA-256 digests and unsafe cookie requests require a session-bound CSRF value.
- RU/Tajik/EN source localization (`ru`, `tg`, `en`) and screens for catalog, account, CRM, and admin areas.
- Nine Alembic revisions, ending at `0009_crm_analytics_indexes`.
- Compose deployment starter with PostgreSQL, API, and frontend services.

## Verified in this takeover

- Backend tests: **50 passed** (one dependency deprecation warning).
- Python compileall: **PASS**.
- pip check: **PASS**.
- Alembic offline PostgreSQL SQL generation through head: **PASS** with an offline-only URL.
- Root-level pytest invocation: **PASS** after adding `pytest.ini` (`50 passed`).
- Frontend npm installation: **BLOCKED** by `EACCES` reaching `registry.npmjs.org`.

## Not verified

- Next.js production build, TypeScript semantic check, frontend lint, and Playwright.
- Live API against PostgreSQL, migration application, PostgreSQL integration tests, and migration rollback/restore behavior.
- Docker image builds, Compose health checks, TLS proxy behavior, and production deployment.

## Release blockers

- Restore permitted npm registry access and commit a reviewed frontend lockfile after checking the dependency graph.
- Configure a private test `DATABASE_URL`; apply migrations to a disposable/test database and test database-backed workflows.
- Add browser tests for registration/login/session restore/logout/CSRF, catalog/quote flows, customer ownership, CRM roles, and mobile layouts.
- Before production: email verification/recovery, shared rate limiting, durable scanned document storage, backups and restore drills, monitoring, secret/key rotation, and deployment review.

See [PROJECT_AUDIT.md](PROJECT_AUDIT.md) for the intake audit and [DEVELOPMENT_ROADMAP.md](DEVELOPMENT_ROADMAP.md) for the ordered next work.
