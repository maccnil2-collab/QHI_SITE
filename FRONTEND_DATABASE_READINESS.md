# Frontend and database readiness check

Date: 2026-11-01  
Current code checkpoint: `1c3eab3` (`Fix localized catalog empty state`)

## npm registry diagnosis

- Portable Node.js 26.13.0 and npm 11.20.0 use the official `https://registry.npmjs.org/`; `strict-ssl` is enabled.
- npm user config is `C:\Users\Asus Notebook\.npmrc`. No user, repository, or portable config file overrides registry or proxy settings. npm `proxy` and `https-proxy` are unset; no HTTP proxy environment variables are present.
- The current user has Modify access to npm cache, but `next` and `typescript` packages are not cached.
- `npm ping --fetch-retries=0 --fetch-timeout=8000` fails with system `EACCES` before HTTP response. DNS lookup also returns no addresses in this execution environment. The evidence indicates outbound socket/network access is denied by the environment, not an npm cache ACL, registry URL, proxy, or TLS problem.
- Recheck in the current shell: DNS now resolves `registry.npmjs.org`, but `curl.exe -I https://registry.npmjs.org/` fails with connection error 7. `node` and `npm` are not currently available in PATH or the standard install locations checked, and Docker is not available either. Installation, dependency resolution, and container-based fallback remain blocked here.
- No registry/proxy config was changed. `frontend/package-lock.json` and `node_modules` remain absent; a lockfile was not fabricated.

## Frontend checks

| Check | Result |
|---|---|
| npm install / lockfile | BLOCKED: registry socket `EACCES` |
| Dependency compatibility resolution | NOT TESTED |
| TypeScript semantic typecheck | BLOCKED: frontend dependencies/types are absent. Bundled compiler reports only unresolved dependency/type declarations after fixing project-local diagnostics; isolated locale dictionaries typecheck successfully. |
| TypeScript/TSX syntax transpile | PASS: 22 files via the TypeScript compiler bundled with VS Code (syntax only) |
| Next production build | BLOCKED: `next` binary not installed |
| ESLint | Configured; BLOCKED: `eslint` binary not installed |
| Playwright E2E | Configured; BLOCKED: `playwright` and browser binaries not installed |

The `typecheck`, `build`, `lint`, `test:e2e`, and `test:e2e:ui` scripts and the ESLint/Playwright configurations are committed. Dependency-backed commands cannot run because packages are missing. The available TypeScript compiler found and helped fix project-local contract issues, but cannot resolve the absent React, Next, Node, and Playwright declarations. Desktop/mobile E2E source covers locale/detail, registration/session restoration, authenticated quote history, order creation, CRM status updates, and admin catalog connection. None of these browser tests has run.

The vehicle detail route was added, and quote submission now uses the session-aware API client with credentials and CSRF. A live browser build has not yet validated these frontend changes.

## PostgreSQL checks

- The installed Windows service `postgresql-x64-18` on port 5432 remains unchanged. Anonymous/no-password authentication to it was rejected; no credentials were guessed.
- A separate PostgreSQL 18.6 cluster was created under `%LOCALAPPDATA%\Temp\qhi-auto-pg-test-3333374`, bound only to `127.0.0.1:55439`. The dedicated `qhi_auto_test` database is UTF-8 and uses loopback-only local test authentication. The cluster was started directly because `pg_ctl` could not create a restricted token inside this environment.
- DSN: `postgresql+psycopg://postgres@127.0.0.1:55439/qhi_auto_test`.
- Ignored local `backend/.env` and `frontend/.env.local` files are configured for this test DB and the local API URL. A new random development `ADMIN_API_KEY` is stored only in ignored `backend/.env`; its value was not printed or committed.
- All ten migrations applied to this fresh test database. `alembic current` reports `0010_shared_rate_limit_buckets`; `alembic check` reports no model/schema differences.
- The opt-in PostgreSQL API workflow test passed and covers registration, login/session restore, CSRF, catalog search/filter/detail, quote calculation/history, favorites/comparison, customer orders, lead intake, staff CRM status/interactions/analytics, admin edit/publication round trips, admin catalog authorization, and shared/concurrent PostgreSQL rate limits.
- The isolated database now contains generated integration fixtures and workflow records. They were left intact. No production DB was contacted.
- Populated backup/restore drill: **PASS**. A custom-format `pg_dump` of the isolated `qhi_auto_test` was restored into a new UTF-8 database `qhi_auto_restore_utf8_test` (created from `template0`). All 18 public tables matched the source in exact row counts and deterministic row-content hashes; both databases report `0010_shared_rate_limit_buckets`. Representative source/restored counts: cars 13/13, customers 13/13, quotes 14/14, orders 13/13, CRM leads 12/12. This caught a Windows client-encoding issue: an initial restore into a database created with default `WIN1251` stopped on UTF-8 Tajik text. That partial test database (`qhi_auto_restore_data_test`), the earlier empty restore target (`qhi_auto_restore_test`), and backup artifacts were preserved and must not be treated as valid restore targets. The successful restore used a fresh `template0`/UTF-8 target and `PGCLIENTENCODING=UTF8`. No production DB was contacted.
- On this Windows cluster, restore targets must be created from `template0` with UTF-8; the default template uses `WIN1251`, which cannot represent the Tajik catalog content. Set `PGCLIENTENCODING=UTF8` for `pg_dump`/`pg_restore` tools. Never reuse the preserved partial target as a valid database.
- The API was started from `backend/` using only `backend/.env` on the normal local port `127.0.0.1:8000`; live `/health` and `/ready` returned `ok`/`ready` with database connected. It is currently running for local use.
- Live HTTP checks against uvicorn returned 200 for health, readiness, localized catalog/search, vehicle detail, and quote calculation (test quote total 14,450.00 TJS).
- Docker and Compose are unavailable in PATH. Compose/image/health checks remain unverified.

## User journey verification status

| Journey | PostgreSQL API runtime | Browser runtime |
|---|---|---|
| Registration, login, session restore, CSRF/logout | PASS | NOT RUN |
| Catalog, search, filters, detail | PASS | NOT RUN |
| Quote calculation and persistence/history | PASS | NOT RUN |
| Favorites, comparison, account session | PASS | NOT RUN |
| Customer order creation/listing | PASS | NOT RUN |
| CRM lead intake/status/interaction/analytics | PASS | NOT RUN |
| Admin catalog access | PASS | NOT RUN |

These API checks do not establish frontend/browser integration.

## Local test commands

With the isolated PostgreSQL server running:

```powershell
.\.venv\Scripts\python.exe -m pytest -q

$env:DATABASE_URL = 'postgresql+psycopg://postgres@127.0.0.1:55439/qhi_auto_test'
Push-Location backend
..\.venv\Scripts\python.exe -m alembic current
Pop-Location
$env:QHI_TEST_DATABASE_URL = $env:DATABASE_URL
.\.venv\Scripts\python.exe -m pytest backend\tests\test_postgres_workflows.py -q
```

Latest isolated backend verification: **53 passed, 1 opt-in test skipped**, `compileall` and `pip check` passed; the PostgreSQL workflow passed (**1 passed**) and `alembic check` found no schema drift. The unit tests explicitly monkeypatch no-database/no-admin settings, so they remain valid with a local `.env`; the PostgreSQL workflow explicitly supplies its disposable test DSN.

After npm dependencies are installed, run Playwright from `frontend/` with `QHI_TEST_DATABASE_URL` set to the same loopback `*_test` DSN. Its config starts API/web dev servers on loopback ports 18000/13000 and refuses other database hosts/names.

## Remaining gates

1. Restore outbound HTTPS access and make Node/npm available, then generate/review the lockfile and use `npm ci`.
2. Resolve package peers, run typecheck, lint, Next build, and Playwright; fix failures based on actual output.
3. Run browser scenarios against the isolated database and record actual results.
4. Keep production deployment blocked on Docker/staging, TLS/reverse proxy, durable scanned document storage, encrypted/retained production backup policy, monitoring, email verification/recovery, and key rotation.
