# QHI AUTO project status

Updated: 2026-11-02

## Current verified status (2026-11-02)

- Latest source checkpoint: `e4e6e81` (`Add guarded TEST password recovery flow`; PostgreSQL and browser recovery verification pending).
- Current uncommitted recovery work adds a TEST-only password reset API and localized account UI. Backend unit suite: 61 passed, 1 skipped; frontend typecheck, lint, and isolated production build passed. PostgreSQL migration/API and browser recovery verification remain pending because the ignored root `.env` is absent in this checkout, so the migration target and backup credentials cannot be safely selected.
- API is running at `http://127.0.0.1:8001/api/v1` and `/ready` returns HTTP 200. The existing frontend process on port 3000 currently returns HTTP 500 after a production build touched its shared `.next` directory. A clean development server is running at `http://127.0.0.1:3001/ru` (HTTP 200); the old port-3000 process could not be restarted under the current process-control policy.
- The isolated UTF-8 database `qhi_auto_demo` contains exactly 100 published cars with `is_demo=true`, 300 image metadata rows, and an explicitly illustrative DEMO tariff. It has no customer accounts. The separate `qhi_auto_app_test` database contains workflow/E2E test fixtures and test-generated records; backups were made to the local temp directory before those workflows. Do not copy test rows into the demo database.
- Catalog API verification returned all 100 cards in RU/TG/EN; brand search, category filtering, USD/TJS values, and three-image gallery metadata per car passed. Browser verification rendered 100 cards, opened a detail page with three gallery entries, and found no mobile horizontal overflow.
- Backend suite: 60 passed, 1 skipped. PostgreSQL workflow: 1 passed, including immutable quote amount snapshots, TEST payment idempotency, explicit production/DEMO database guards, admin-only partial/full refunds, and ledger history. Frontend typecheck, ESLint, and optimized production build passed.
- Playwright desktop/mobile: all 8 scenarios passed on a fresh isolated TEST database, including customer registration/session restore, vehicle-linked quote, order with frozen quote amount, simulated TEST payment, protected admin promotion and simulated refund, CRM/admin, and QHI CARE ticket intake/resolution. The runner needed interruption during Windows web-server teardown after all test cases had reported success.
- Migration `0013_order_payment_ledger` is applied to DEMO and the existing TEST databases only after separate backups. DEMO still has exactly 100 `is_demo=true` vehicles, 300 image rows, zero customers/orders/payment attempts. TEST and DEMO records remain separate.
- External Unsplash URLs are blocked by this browser sandbox (`ERR_NETWORK_ACCESS_DENIED`); URL/license metadata is present, but successful photo pixel rendering remains unverified here. No public deployment or real payment occurred.
- Real payment processing remains disabled. The explicit `test_simulator` can create TEST ledger entries and admin refunds only when a backend test flag is enabled and the connected database name ends in `_test`; it never contacts a provider or transfers funds. No mail sender is configured. Password recovery work only exposes an in-memory TEST outbox token when both a test feature flag and a `*_test` database are active; production is rejected. Its migration and database-backed flow still need verification before enabling that flag anywhere.

The earlier takeover snapshot below is historical and is superseded by this section.

## Historical takeover checkpoint

- Git branch: `main`
- Latest committed code checkpoint: `73a0c92` (`Fix frontend lint and document readiness results`)
- Existing user file: untracked root `test.txt`; preserve unchanged.

## Working and implemented

- FastAPI backend with catalog, quote snapshots, identity/sessions, customer account data, orders/events/notifications, CRM, admin APIs, and readiness endpoints.
- Browser session cookies are HttpOnly and host-only; session tokens are stored as SHA-256 digests and unsafe cookie requests require a session-bound CSRF value.
- RU/Tajik/EN source localization (`ru`, `tg`, `en`) and screens for catalog, account, CRM, and admin areas.
- Localized vehicle detail page/API added; catalog links to detail pages. Quote calculation now uses the session-aware CSRF client so signed-in estimates are associated with the customer's history.
- Catalog empty-state copy now reports no matching vehicles instead of claiming the collection is not open yet; the contact shortcut has a localized accessible name.
- ESLint flat config and Playwright desktop/mobile Chromium tests configured for locale/detail, registration/session restore, quote/order, CRM, and admin flows. The estimate test checks persistence without depending on a tariff label; missing DB fixtures fail clearly instead of silently skipping.
- Frontend manifest pins npm `11.20.0` and Node `>=20.9.0`; dependency installation completed and `frontend/package-lock.json` was generated.
- Ten Alembic revisions, ending at `0010_shared_rate_limit_buckets`.
- Compose deployment starter with PostgreSQL, API, and frontend services.

## Verified in this takeover

- Backend tests: **53 passed, 1 opt-in PostgreSQL test skipped** (one dependency deprecation warning); no-database tests now explicitly isolate configuration and pass with local `.env` present. The separately invoked PostgreSQL workflow passed (**1 passed**).
- Python compileall: **PASS**.
- TypeScript/TSX syntax transpilation: **PASS (22 files)** using the VS Code-bundled compiler; this is syntax-only, not a semantic typecheck.
- Isolated TypeScript semantic check for RU/TG/EN message dictionaries: **PASS**. Full-app semantic checking through the bundled compiler remains blocked by absent React/Next/Node/Playwright declarations; after fixes, the remaining diagnostics were dependency/type-resolution errors.
- pip check: **PASS**.
- Isolated PostgreSQL 18.6 test database `qhi_auto_test` on loopback port 55439: **PASS**; ten migrations applied, head is `0010_shared_rate_limit_buckets`, schema check clean.
- Fresh UTF-8 test database `qhi_auto_migration_fresh_test`: **PASS**; all ten migrations applied from an empty schema, `alembic check` clean, PostgreSQL workflow **1 passed**.
- Populated PostgreSQL backup/restore: **PASS** into `qhi_auto_restore_utf8_test`; all 18 table row counts and deterministic content hashes match, including Tajik text. An initial restore into a Windows-default `WIN1251` target failed on UTF-8; the partial test target and artifacts were retained.
- `alembic check`: **PASS**, no model/schema differences.
- Alembic now reads ignored `backend/.env` for local commands; `alembic current` and `alembic check` both pass without exporting `DATABASE_URL` manually.
- PostgreSQL-backed API workflows: **1 passed** (auth/session/CSRF, explicit denial of customer sessions on staff routes, catalog/search/detail, quote/history, favorites/comparison, order, CRM, admin editing/publication, and shared rate-limit checks across independent instances and concurrent requests).
- The PostgreSQL workflow also passed against the populated UTF-8 restore clone, confirming the restored database serves the same API paths.
- Fresh Uvicorn process on loopback port 18001: **PASS**; readiness connected to the isolated test DB and live login requests returned eight `401` responses followed by `429` at the configured limit. Temporary process was stopped after the check.
- Isolated database readiness and integration evidence are maintained in [FRONTEND_DATABASE_READINESS.md](FRONTEND_DATABASE_READINESS.md); PostgreSQL tests are explicitly opt-in and require a loopback database with a `*_test` name.
- Local API startup from ignored `backend/.env`: **PASS**; uvicorn is running on `127.0.0.1:8000`, readiness reports the test DB connected.
- Root-level pytest invocation: **PASS** from repository root.
- Frontend npm dependencies were installed by the owner with Node 26.13.0/npm 11.20.0; `frontend/package-lock.json` and `node_modules` are present. In this shell `npm ping` and `npm audit` still fail with `EACCES` to npm registry endpoints.

## Not verified

- TypeScript typecheck, ESLint, and Next.js production build now pass. Playwright runs using installed system Chrome; locale/detail routes and CRM/admin journeys pass on desktop and mobile. Registration/session restore reaches the quote form, but the calculator E2E scenario fails because its required numeric input is empty at submit. Browser download from Playwright CDN is blocked with EACCES. `npm audit` cannot fetch advisory metadata, so dependency vulnerabilities remain to be confirmed/resolved.
- The full account quote/order E2E scenario remains failing after session restore. Migration rollback is untested. Production backup encryption, retention, and recovery procedures are also not established by the local test-database drill.
- Docker image builds, Compose health checks, TLS proxy behavior, and production deployment.

The detailed current network/PostgreSQL diagnosis and journey matrix are in [FRONTEND_DATABASE_READINESS.md](FRONTEND_DATABASE_READINESS.md).

## Release blockers

- Restore permitted npm registry access; create/review the lockfile, resolve dependency peers, and run the existing lint/typecheck/build/E2E scripts.
- Run the configured browser journeys against the isolated PostgreSQL test database.
- Authentication, quote, lead, and document limits now use atomic PostgreSQL counters shared across API workers; hashed keys are stored in migration 0010. Still required before production: email verification/recovery, durable scanned document storage, backups and restore drills, monitoring, secret/key rotation, and deployment review.

See [PROJECT_AUDIT.md](PROJECT_AUDIT.md) for the intake audit and [DEVELOPMENT_ROADMAP.md](DEVELOPMENT_ROADMAP.md) for the ordered next work.
