# Development Status

Updated: 2026-11-01

## Done
- Verified Python 3.11.9, `pip check` (no broken requirements), and `.venv` packages: FastAPI 0.162.0, SQLAlchemy 2.1.6, Alembic 1.20.1, Pydantic 2.14.2, psycopg 3.3.6, pytest 9.2.0.
- Found project-local Node.js 26.13.0/npm 11.20.0 and portable Git 2.56.0; system PATH was not changed.
- PostgreSQL 18.6 service is running and accepts connections. Authentication requires a password; no secret was requested, read, or stored.
- Implemented health endpoint, SQLAlchemy catalog/image/translation/tariff/audit models, filtered catalog endpoint, tariff-safe cost calculation, initial Alembic migrations, and API-key-protected car/tariff management with change audit. A responsive web admin form can add cars with required ru/tg/en translations, manage tariff versions, publish/unpublish vehicles, and activate tariffs. Catalog responses select the requested locale and search its translated title. Administrative access fails closed unless a private 32+ character key is configured; the key remains in page memory only.
- Added localized Next.js source for ru/tg/en, responsive catalog filters, empty/error states, and in-memory comparison of up to three cars. Translation dictionary has 53 matching keys per locale and passed a runtime Unicode/newline check.
- Ten API/pricing/admin-guard/CORS/translation tests pass. Python compileall passes. Alembic offline DDL and history pass. A real Uvicorn smoke check returned HTTP 200 from `/api/v1/health` and `/openapi.json`; OpenAPI lists catalog and admin endpoints.
- Git main checkpoints: Branch `main`, head `7c86257`; prior checkpoints include `06ece56` and `23b17a2`.

## Blocked or not verified
- npm registry returns EACCES. Next/React/Tailwind are not installed; there is no lockfile. Build and typecheck have not run.
- PostgreSQL connection without a password is rejected. No migration was applied and DB integration remains untested.
- Playwright is absent; browser tests have not run.
- There are no verified vehicle listings, photos, exchange rates, customs rates, or legal pricing rules. No such data was fabricated.
- pytest emits a Starlette warning recommending httpx2 for TestClient; tests still pass.

## Next tasks
1. Restore npm registry access, resolve and lock dependencies, then build/typecheck the frontend.
2. With private DB credentials, create the application database, apply Alembic, and run integration tests.
3. Implement secured admin tariff/catalog management, then identity, orders/logistics, and CRM.
4. Install Playwright and perform browser, accessibility, and performance checks.