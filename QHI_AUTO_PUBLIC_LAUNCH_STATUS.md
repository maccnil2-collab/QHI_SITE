# QHI AUTO public launch status — 2026-11-01

## Completed in this work session

- Added reversible Alembic revision `0012_structured_vehicle_specs` for fuel type, torque, 0–100 km/h time, maximum speed, seating, doors, dimensions, key advantages, specification-source URL, optional USD/TJS prices, price note, and price-source URL.
- Added API filtering by year range, engine type, and fuel type. The frontend now requests up to 100 rows and exposes localized RU/TG/EN controls for those filters.
- Extended the admin form for the additional specifications and optional sourced USD/TJS values. Omitted nullable fields from older clients are preserved on update.
- Added structured per-photo alt text, author, license, and source metadata to the admin write path and catalog response. The detail gallery can show the photo credit.
- Added a publication gate: a new publication requires at least three credited/licensed/source-linked photos, a technical source, and a price source (or an explicitly noted DEMO price).
- Added Netlify build configuration for the Next.js frontend and a build-time guard that rejects missing, insecure, or localhost production API URLs. Backend and PostgreSQL remain separate services.
- Added `DEPLOYMENT_NETLIFY.md` with the service split and outstanding production steps.

## Verification

- Frontend: `npm run typecheck` and `npm run lint` pass.
- Backend unit/API tests: 58 passed, 1 PostgreSQL integration test skipped.
- Alembic: offline SQL generation through revision `0012_structured_vehicle_specs` succeeds. No database was changed.
- Production frontend build: succeeds; Next.js reports the localized route at 8.28 kB, First Load JS 128 kB.
- Browser smoke checks: RU/TG/EN home pages return HTTP 200; no browser exceptions; tested widths 320, 375, 390, 430, 768, 1024, and 1440 px without horizontal overflow; the mobile menu opens.
- Netlify environment guard: accepts HTTPS API URLs ending in `/api/v1` and rejects localhost.
- Playwright E2E could not start because `QHI_TEST_DATABASE_URL` is not configured. The test harness deliberately requires a disposable loopback PostgreSQL database ending in `_test`.

## Not completed / no unsupported claims

- There is no verified, loaded set of 100 production/demo inventory records in the repository that could be safely promoted. The current database is unavailable, and there is no production backup to inspect. No vehicle rows were inserted or altered.
- `frontend/public/images/` contains QHI brand assets, not a licensed library of model-matching vehicle photographs. No shared logo or unrelated car image was reused to fabricate inventory. Therefore no vehicle is presented as a new real offer and the 100-car catalog is not complete.
- A production backup could not be made: no `DATABASE_URL`, root `.env`, or available Docker/PostgreSQL service was found. Revision `0012` was not applied to any database.
- The local FastAPI readiness endpoint on port 8000 is unavailable, so catalog data, saved state, calculator persistence, authorization, and live vehicle galleries could not be integration-tested here.
- `https://electro-tj.netlify.app/` could not be reached from this environment. No Netlify CLI, authenticated Netlify integration, `NETLIFY_AUTH_TOKEN`, or site ID is available, so site ownership/current deploys cannot be verified and no deployment was attempted.
- No external storage bucket or production API host is configured. The Next.js frontend is prepared for Netlify, but it cannot be deployed safely until the API URL, backend, database, CORS origin, and durable image storage are supplied/configured.

## Required before public launch

1. Provide access to the owner's Netlify account/site so the target site's ownership and current deploy can be inspected before linking or publishing.
2. Configure a reachable production FastAPI host and managed PostgreSQL database; set `NEXT_PUBLIC_API_URL` to the HTTPS API base ending in `/api/v1` and set backend CORS for the verified frontend origin.
3. Back up that production database, review the migration, and only then apply Alembic revision `0012`.
4. Provide/approve a durable image-storage location and a verified dataset containing exactly 100 distinct vehicle configurations, model-specific photos, image attribution/licenses, specification sources, and sourced or clearly estimated prices.
5. Configure a disposable local PostgreSQL database ending in `_test` to run the gated Playwright workflows. Do not point it at production.
6. After these are configured, run the migration, seed and validate 100 rows, run the full tests, deploy, and smoke-test the public site and API.
