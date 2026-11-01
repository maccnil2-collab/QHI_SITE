# QHI AUTO project audit

Audit date: 2026-11-01  
Repository: `C:\Users\Asus Notebook\QHI-AUTO`  
Branch and base checkpoint: `main`, `666ff552d5bd6fb0545ceaf3fcd33ef06e4f9169` (`Secure browser sessions with CSRF-protected cookies`)

## Repository intake

- No `AGENTS.md` was found in the repository. Reviewed all project Markdown documentation under `docs/`, `backend/`, `frontend/`, `reports/`, and the root environment report.
- The working tree at intake had one untracked file, root `test.txt` (6 bytes). It was not read, changed, moved, or added to Git.
- Existing commits after the earlier feature work include the Compose starter and auth/CSRF changes; the stated checkpoint is the current `HEAD`.
- The repository contains FastAPI/SQLAlchemy/Alembic backend code, a Next.js App Router frontend, nine Alembic revisions, backend pytest tests, and a single-host Compose starter.

## Implemented surface found in source

- **Backend APIs:** public catalog/search/filter and quote calculation; login, registration, current user, profile, logout, session management, favorites and comparisons; customer orders, notifications, and visible documents; staff order/document management; CRM intake, staff lead workflows and analytics; admin vehicle, tariff, and customer-role management; health/readiness endpoints.
- **Security controls:** scrypt password hashes; opaque 14-day session cookie with SHA-256 token digest in the database; session-bound HMAC double-submit CSRF for unsafe cookie-authenticated requests; configured-origin checks on login and registration; role checks for staff; rate limits; Pydantic input schemas; SQLAlchemy expression-based queries; audit records for admin changes; bounded uploads with file-signature checks and owner/visibility checks.
- **Pricing/data:** Decimal-based tariff calculations, effective dates, explicit customs basis/rate, quote snapshots, and versioned Alembic schema through `0009_crm_analytics_indexes`.
- **Frontend source:** locale routes and screens for catalog, account, admin, customer administration, and CRM; API client; cookie-session restoration; localized RU/Tajik/EN dictionaries. The route identifier used by the project is `tg` for Tajik.
- **Deployment source:** API, web, and PostgreSQL Compose services with private DB networking, local-only host port bindings, health checks, non-root image instructions, and separate migration instructions.

## Verification run during intake

- Backend tests, run from `backend/`: **50 passed**, one Starlette/httpx deprecation warning.
- Python `compileall` for `app`, `tests`, and `alembic`: **PASS**.
- `pip check`: **PASS**, no broken requirements.
- Alembic offline PostgreSQL SQL generation through revision `0009_crm_analytics_indexes`: **PASS** when supplied a throwaway offline URL; no live database was contacted or modified.
- Frontend dependency installation: **BLOCKED**. `npm install --no-audit --no-fund` reached `registry.npmjs.org` and failed with `EACCES`; it was stopped after the repeated network error. No lockfile or `node_modules` was created.
- Next build, semantic TypeScript typecheck, lint, and Playwright: **NOT RUN** because dependencies are unavailable and the package manifest defines no lint or E2E script.
- Live API/database, applied migrations, PostgreSQL integration, and Compose: **NOT VERIFIED**. This audit did not use production credentials or change a database.

## Risks and unfinished work

1. Frontend source has not been validated by a real dependency-backed Next build or TypeScript semantic check. This is the highest immediate verification gap.
2. Migrations have only been rendered offline; a privately configured PostgreSQL database is needed for migration application and transaction/integration checks.
3. Deployment cannot be exercised here without Docker/Compose and registry access. No production readiness claim is made.
4. The current auth rate limiter is process-local, so it does not provide a shared limit across multiple API workers or replicas.
5. Email verification and account recovery are absent. Registration explicitly leaves email unverified.
6. Order document storage has no malware scanning, durable object-storage adapter, or verified retention/restore process.
7. The bootstrap admin API key remains a transitional management path; production key rotation and operational controls remain outstanding.
8. User-owned inventory, images, exchange rates, and legal tariff values are intentionally not invented.

After the intake audit, added a root `pytest.ini` so the suite can be collected from the repository root without manually changing Python paths. Re-running pytest from the root after this change produced **50 passed** (same deprecation warning).

## Follow-up mission from `3333374`

- Added a localized public vehicle detail API and frontend route. Catalog vehicle titles now link to the detail page.
- Fixed a browser/API mismatch in quote submission: signed-in quote requests now go through the cookie/CSRF-aware API client and can be attached to the current customer's quote history.
- Added opt-in PostgreSQL workflow coverage. On a separate loopback-only PostgreSQL 18.6 cluster, migrations 0001–0009 applied successfully, `alembic check` found no drift, and the integration workflow passed for auth/session/CSRF, catalog, quote history, account saved vehicles, orders, CRM, and admin access.
- Added ESLint and Playwright scripts/configuration and desktop/mobile workflow specs. npm registry access still fails at the socket layer with `EACCES`; lockfile generation, dependency resolution, typecheck, lint, Next build, and browser execution remain unverified.
- Current checkpoint is `ec0d0c2`. The detailed evidence and test database instructions are in [FRONTEND_DATABASE_READINESS.md](FRONTEND_DATABASE_READINESS.md).
