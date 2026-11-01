# Development Environment Audit

Date: 2026-11-01. Project: `C:\Users\Asus Notebook\QHI-AUTO`.

| Component | Result |
|---|---|
| Python / venv | Python 3.11.9; project `.venv` works |
| FastAPI | 0.162.0 |
| SQLAlchemy | 2.1.6 |
| Alembic | 1.20.1 |
| Pydantic | 2.14.2 |
| psycopg / binary | 3.3.6 / 3.3.6 |
| pytest | 9.2.0 |
| Node.js / npm | Project-local 26.13.0 / 11.20.0 |
| Git | Portable 2.56.0.windows.4 |
| PostgreSQL | PostgreSQL/pg_ctl client version 18.6; service `postgresql-x64-18` is Running; pg_isready reports localhost:5432 accepting connections |
| Next.js / React / TypeScript / Tailwind | Manifest created; packages and lockfile unavailable because npm registry returns EACCES |
| Playwright | Not found in venv/project |
| VS Code / Figma / Windows build / RAM / free disk | Not checked in this project audit |

Admin catalog/tariff and customer-role panel source exists. Customer account/order, public quote/enquiry, catalog favorite/comparison controls, and initial CRM screen source has been added. CRM loads active manager choices from a staff-only API. No frontend dependency installation or compiled build has succeeded; CRM localization and manager lookup UI remain pending.

Node and Git live under `tools/`; system PATH was not changed. A PostgreSQL 18 installer already exists in `downloads/`; it was not rerun. No new programs were installed; added-program disk usage is 0 bytes. Existing `test.txt` remains untouched and untracked. Secrets were not stored.

## Checks performed
- Python, Node.js, npm, Git versions and venv package inventory succeeded; `pip check` reports no broken requirements.
- PostgreSQL service is Running and accepts TCP connections. `psql -w` without a password was rejected; no password was attempted.
- 27 API, pricing, auth, order, CRM, quote calculator/rate-limit, admin-guard, and CORS tests passed; compileall passed; Alembic offline SQL generated through head `0006_crm`.
- Uvicorn smoke test returned OpenAPI with 29 paths, including auth, customer orders, CRM, and admin routes.
- Base locale dictionaries match; account dictionaries have 29 matching keys per locale and execute under Node 26 strip-types. JSON package/TypeScript manifests parse. All 17 TypeScript/TSX files pass TypeScript syntax transpilation using the compiler bundled with VS Code; this does not replace semantic typechecking or a Next build.
- npm registry lookup failed with EACCES. Next.js build/typecheck, DB migration against the running server, and Playwright tests were not run. PostgreSQL was TCP-ready but password authentication was rejected when tested without credentials; no secret was guessed or emitted.

## Constraints
The execution environment previously blocked winget and pip network access. Work uses existing local tools and dependencies. No Windows system settings were changed.