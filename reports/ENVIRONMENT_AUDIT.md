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
| PostgreSQL | Service `postgresql-x64-18` is Running; pg_isready reports localhost:5432 accepting connections |
| Next.js / React / TypeScript / Tailwind | Manifest created; packages and lockfile unavailable because npm registry returns EACCES |
| Playwright | Not found in venv/project |
| VS Code / Figma / Windows build / RAM / free disk | Not checked in this project audit |

A private admin panel and guarded catalog/tariff API are implemented as source. It accepts localized car titles/descriptions and keeps the admin key in memory; the browser build is not verified.

Node and Git live under `tools/`; system PATH was not changed. A PostgreSQL 18 installer already exists in `downloads/`; it was not rerun. No new programs were installed. Existing `test.txt` remains untouched and untracked. Secrets were not stored.

## Checks performed
- Python, Node.js, npm, Git versions and venv package inventory succeeded.
- PostgreSQL service is Running and accepts TCP connections. `psql -w` without a password was rejected; no password was attempted.
- Ten API/pricing/admin-guard/CORS/translation tests passed; compileall passed; Alembic offline SQL generation/history passed.
- Uvicorn smoke test returned HTTP 200 from `/api/v1/health` and `/openapi.json`; OpenAPI contained catalog and admin routes.
- Translation dictionaries decoded as UTF-8 and contain 53 matching keys per locale.
- npm registry lookup failed with EACCES. Next.js build, DB migration against the running server, and Playwright tests were not run.

## Constraints
The execution environment previously blocked winget and pip network access. Work uses existing local tools and dependencies. No Windows system settings were changed.