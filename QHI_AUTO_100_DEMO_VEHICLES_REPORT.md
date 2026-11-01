# QHI AUTO 100 demo vehicles

Updated: 2026-11-01

## Imported catalog

- Exactly 100 published demo rows were added to the existing local `qhi_auto_test` database using the existing admin API.
- Every row has `is_demo = true`; the set contains 20 public model families with five clearly labeled QHI demo trim/year cards per family.
- Every card has RU/TG/EN title and description, an illustrative spec set, CNY plus demo USD/TJS prices, and three gallery entries with alt text, source URL, attribution, and license metadata.
- Prices, year/trim combinations, and technical variations are explicitly estimates for catalog demonstration. They do not describe actual units, sellers, availability, or sale offers.
- Images use a small rotating set of six generic Unsplash car photographs and are labeled illustrative; they are not claimed to depict the named model/trim. Unsplash says its license permits commercial use and does not require attribution, though it appreciates attribution: [Unsplash License](https://unsplash.com/license).
- Reproducible idempotent importer: [tools/seed_demo_inventory.py](tools/seed_demo_inventory.py). It uses the existing admin API and refuses to run unless `backend/.env` points to a loopback database ending in `_test`.

## Verification

- Database: **100 demo rows**, all published; **300 gallery rows**, all with photo metadata; all 100 have USD/TJS values and demo price notes.
- Public API search `q=QHI Demo`: **100 results**. Model search and category filters work; 2024/electric filters return expected subsets. Price sort and localized detail API return demo prices and three gallery items.
- Admin API returns all 100 demo entries with `is_demo=true` and image details.
- Browser: RU/TG/EN each render 100 cards; model search returns five BYD Han variants; sedan filter retains the five matches; clear restores 100. Detail route shows three gallery entries. At 320, 390, and 768 px there is no horizontal overflow; no browser page errors were observed.
- Backend: **58 passed, 1 skipped**; PostgreSQL workflow **1 passed**; Alembic head is `0012_structured_vehicle_specs`, `alembic check` is clean. Frontend typecheck, lint, and production build pass.
- Pre-import backup: `%TEMP%\qhi-auto-test-before-100-demo-6cc5ff1.dump`. Post-import backup: `%TEMP%\qhi-auto-test-after-100-demo-final-6cc5ff1.dump`.

## Image network limitation

The browser environment cannot fetch Unsplash image bytes: gallery `<img>` elements reported `naturalWidth=0` and requests failed under the current network restriction. The image URLs are stored and render as ordinary external image links; verify them from an internet-connected browser before relying on this sandbox preview. The application database stores image URLs and metadata rather than image blobs, matching the existing architecture.

The seeded database remains an isolated local test database containing integration fixtures in addition to the 100 demo rows. No production database was configured or changed, and no Netlify deployment was attempted.
