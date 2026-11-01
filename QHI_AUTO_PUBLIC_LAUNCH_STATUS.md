# QHI AUTO public launch status — 2026-11-01

## Work completed at checkpoint `626ca1d`

- Added reversible Alembic revision `0012_structured_vehicle_specs` for fuel type, torque, 0–100 km/h time, maximum speed, seating, doors, dimensions, key advantages, specification-source URL, optional USD/TJS prices, price note, and price-source URL.
- Added API filtering by year range, engine type, and fuel type. The frontend now requests up to 100 rows and exposes localized RU/TG/EN controls for those filters.
- Extended the admin form for the additional specifications and optional sourced USD/TJS values. Omitted nullable fields from older clients are preserved on update.
- Added structured per-photo alt text, author, license, and source metadata to the admin write path and catalog response. The detail gallery can show the photo credit.
- Added a publication gate: a new publication requires at least three credited/licensed/source-linked photos, a technical source, and a price source (or an explicitly noted DEMO price).
- Added Netlify build configuration for the Next.js frontend and a build-time guard that rejects missing, insecure, or localhost production API URLs. Backend and PostgreSQL remain separate services.
- Added `DEPLOYMENT_NETLIFY.md` with the service split and outstanding production steps.

## Verification recorded at checkpoint `626ca1d` (historical)

- Frontend: `npm run typecheck` and `npm run lint` pass.
- Backend unit/API tests: 58 passed, 1 PostgreSQL integration test skipped.
- Alembic: offline SQL generation through revision `0012_structured_vehicle_specs` succeeds. No database was changed.
- Production frontend build: succeeds; Next.js reports the localized route at 8.28 kB, First Load JS 128 kB.
- Browser smoke checks: RU/TG/EN home pages return HTTP 200; no browser exceptions; tested widths 320, 375, 390, 430, 768, 1024, and 1440 px without horizontal overflow; the mobile menu opens.
- Netlify environment guard: accepts HTTPS API URLs ending in `/api/v1` and rejects localhost.
- Playwright E2E could not start because `QHI_TEST_DATABASE_URL` is not configured. The test harness deliberately requires a disposable loopback PostgreSQL database ending in `_test`.

## Not completed / no unsupported claims

- At checkpoint `626ca1d`, there was no loaded 100-card set. This takeover added exactly 100 published DEMO rows to the isolated local `qhi_auto_test` database (20 model families × 5 illustrative year/trim cards), each with `is_demo=true`; no production database was accessed.
- Each demo row has three Unsplash-licensed illustrative image URLs and credits, RU/TG/EN titles/descriptions, technical fields, and USD/TJS demo prices. The photos are explicitly labeled illustrative, and model/year/trim specifications and prices are demo estimates, not actual inventory or offers. `frontend/public/images/` remains the existing QHI brand artwork; vehicle images are external Unsplash URLs in the database.
- The connected database is the local test database `qhi_auto_test`; it now contains the 100 demo cards and integration fixtures. No production database was configured, accessed, or backed up.
- Unsplash image URLs and license metadata are present, but the network-restricted browser could not fetch the image bytes. Cards and galleries were checked; visual image loading must be rechecked outside this sandbox.
- Ownership/deploy access for `qhi-auto.netlify.app` is unverified. No deployment was attempted.
- Durable production image storage, a production API/database, and production CORS are not configured. Demo model/year/trim values and prices are estimates, not verified offers or production inventory.

## Required before public launch

1. Provide access to the owner's Netlify account/site so the target site's ownership and current deploy can be inspected before linking or publishing.
2. Configure a reachable production FastAPI host and managed PostgreSQL database; set `NEXT_PUBLIC_API_URL` to the HTTPS API base ending in `/api/v1` and set backend CORS for the verified frontend origin.
3. Back up that production database, review the migration, and only then apply Alembic revision `0012`.
4. For production inventory, verify 100 vehicle configurations, model-specific photos, technical references, and prices; choose durable image storage. The local demo set is illustrative and must not be presented as real inventory.
5. The disposable local `qhi_auto_test` PostgreSQL database is available for gated workflows; keep integration and Playwright tests on loopback `*_test` databases.
6. After production hosting, backups, image storage, and Netlify ownership are verified, run the production migration, deploy, and smoke-test the public site and API.

## Takeover follow-up after checkpoint `626ca1d`

- Started the existing isolated PostgreSQL cluster from `%LOCALAPPDATA%\Temp\qhi-auto-pg-test-3333374`. The ignored `backend/.env` points to `127.0.0.1:55439/qhi_auto_test`; port 55439 had been closed. The separate Windows PostgreSQL service on 5432 was left untouched.
- Created custom-format backup `qhi-auto-test-before-demo-626ca1d.dump` in the OS temp directory before schema or inventory changes, then applied revisions `0011` and `0012` to the isolated test DB. A second custom-format backup after migration is `qhi-auto-test-after-migrations-626ca1d.dump`.
- Migration `0011` initially failed because its 38-character revision ID exceeded Alembic's standard `alembic_version.version_num VARCHAR(32)`. PostgreSQL rolled back the transaction. Shortened the revision ID to `0011_demo_inventory_support`, updated `0012`'s dependency, and successfully upgraded to `0012_structured_vehicle_specs`.
- `alembic check` then exposed the migration-created `support_ticket_events.actor_id` index missing from ORM metadata. Added `index=True` to the existing model; `alembic check` now reports no drift.
- Backend verification: **58 passed, 1 skipped**. Frontend typecheck, lint, and production build pass. Local FastAPI readiness is `ready`; the existing Next dev frontend serves `/ru`, `/tg`, and `/en` on port 13000. Port 3000 is denied by this environment (`listen EACCES`).
- After the PostgreSQL workflow, the local test DB had 16 integration fixtures. The 100 DEMO cards were then added and verified; the final custom-format backup is `qhi-auto-test-after-100-demo-final-6cc5ff1.dump` in the OS temp directory. No non-demo records were altered. `qhi-auto.netlify.app` ownership, production API/database access, and durable production image storage remain unverified; no publish was attempted.
- Browser checks confirmed 100 catalog cards, 100 search results, working model search/category filters, 3 gallery entries on a detail page, RU/TG/EN pages, and mobile widths 320/390/768 without overflow. The sandbox blocked Unsplash image requests (`naturalWidth=0`); URL and metadata are present, but the actual pixels could not be verified from this network-restricted browser. The current browser therefore shows the cards and gallery entries but may show blank remote images until Unsplash is reachable.
- Re-running the PostgreSQL workflow uncovered a comparison/favorites response bug after `image_details` was added to `CarOut`: `_localized_car` attempted to read that response field from the ORM model. It now serializes image credit metadata explicitly. PostgreSQL workflow passes (**1 passed**), the backend suite passes (**58 passed, 1 skipped**), and `alembic check` reports no drift.
- The reusable, idempotent admin-API importer is [tools/seed_demo_inventory.py](tools/seed_demo_inventory.py). It creates the same 100-row demo set in the local database configured by `backend/.env`.
