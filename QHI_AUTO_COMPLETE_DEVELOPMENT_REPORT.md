# QHI AUTO — development report

Date: 2026-11-01

## Summary

This pass added a base for categorized vehicle specifications, public/staff support tickets, an explicitly disabled provider-neutral payments boundary, localized support/legal pages, and responsive refinements. The existing account, order, quote, CRM and admin authorization flows were left in place.

**This is not a complete commercial platform and is not ready for public commercial launch.** Important requested scope remains unfinished: there is no seeded 50-car catalog or licensed vehicle photo set, no live currency conversion, no outgoing mail integration, and no functioning payment processing or transaction/refund/webhook workflow. The new database migration is not yet applied because the isolated test PostgreSQL server is unreachable.

## Implemented

- Added vehicle category, engine, volume, transmission, mileage, color, equipment, specifications, fuel consumption, and explicit `is_demo` data fields. Existing catalog API now accepts category and sorting filters; the catalog UI offers category/sort selectors. Detail pages show the new available facts and mark demo records.
- Added an admin form for the extended vehicle fields and demo flag; existing admin token protection and publication controls remain active.
- Added support ticket API with input validation, rate limiting, generated reference number, statuses, event history, and staff-only listing/status updates.
- Added customer support form in RU/TG/EN and staff workspace at `/admin/support`. Requests are persisted only; no email is reported or implied as sent.
- Support contact address is `t24339984@gmail.com`.
- Added seven RU/TG/EN legal information pages: privacy, terms, cookies, refunds, payment information, contact, and about. They avoid inventing a registered company and include draft/launch cautions in the text.
- Added provider-neutral payment contract (`create_session`, webhook verification, refund) whose only current provider always refuses operations. Added an additive payment-attempt model/migration with unique idempotency and provider references; there is no checkout, successful transaction, card collection, webhook endpoint, refund execution, or payment administration UI.
- Detail page text that previously appeared mojibaked was replaced with localized RU/TG/EN copy. Added small-screen and tablet fixes for legal headings and contact layout.

## Catalog and data

- The system can store the requested additional structured car properties and each record can be explicitly marked DEMO.
- **The requested 50 demonstration vehicles have not been populated.** No suitable vehicle images with verified file-level commercial-use licenses were present in the repository. Wikimedia Commons search confirms that individual vehicle photographs have different authors and licenses; images must be checked and attributed per file. For example, [Toyota Camry Front.jpg](https://commons.wikimedia.org/wiki/File:Toyota_Camry_Front.jpg) and [Tesla Model 3.jpg](https://commons.wikimedia.org/wiki/File:Tesla_Model_3.jpg) have separate CC BY-SA terms. No photos were copied or mislabeled as exact inventory. A vetted photo set and an explicit demo-data import must be completed before advertising a 50-car demo catalog.
- The extended schema and admin editor are code-ready, but the local database is behind the new migration. No migration was applied.
- Image upload, local image storage, image attribution editor, and license ledger UI are not implemented.

## Payments, support, currency, admin

- **Payments:** disabled, no money movement. The code is only an adapter boundary and schema groundwork. Required company, bank, provider, signature/replay checks, reconciliation, and legal tasks are documented in [docs/PAYMENTS_PRELAUNCH.md](docs/PAYMENTS_PRELAUNCH.md).
- **Support:** ticket creation and staff status updates are implemented at the API/UI layer. Persistent production behavior requires applying migration 0011. SMTP/provider configuration is absent; mail is not sent.
- **Currency:** vehicle display and quote calculator still use CNY/TJS tariff inputs. USD/EUR/TJS selection, live or dated demo FX rates, and rate-source timestamps have not been implemented. No rate has been invented.
- **Administration:** existing catalog/tariff, customer, and CRM/order workspaces remain. Extended vehicle editing and support ticket management were added. Dedicated categories management, image upload, payment history/refunds, FX/site settings, and audit UI for new support actions remain incomplete. Role-protected staff APIs were used for support; the `/admin/support` page itself relies on the staff authorization enforced by the backend.

## Security review

- Existing password hashing, opaque sessions, session-bound CSRF for cookie-authenticated writes, rate limiting, token-protected admin API, and staff-role guards were retained.
- New support payloads are validated and size-bounded, rate-limited, and staff data routes use the existing `require_staff` dependency.
- No card data or provider secret is added to frontend code; payment provider always returns disabled/rejected behavior.
- Review details and remaining checks are in [docs/SECURITY_REVIEW.md](docs/SECURITY_REVIEW.md). No PCI DSS, GDPR, or other compliance certification is claimed.
- Production secrets review, dependency vulnerability scanning, external security testing, and a backup restore drill were not performed.

## Database and backend state

- Existing configured DSN was inspected without printing credentials: it targets loopback port `55439` and a test-named database. TCP to that PostgreSQL port is currently unavailable.
- `/api/v1/health` at `127.0.0.1:8000` returned `{"status":"ok","database":"configured"}`; `/api/v1/ready` was unavailable/timed out. Do not interpret `health` as proof of database readiness.
- Alembic migration `0011_demo_inventory_support_payments` is pending. No application or production database was modified.
- SQLite-backed API test covers support ticket persistence, reference generation, and staff-only listing. It does not substitute for a PostgreSQL migration run.

## Verification results

- Backend: `56 passed, 1 skipped, 1 warning` (`Starlette TestClient`/httpx deprecation warning).
- Frontend: `npm run typecheck` passed.
- Frontend: `npm run lint` passed with `--max-warnings=0`.
- Frontend: isolated production `npm run build` passed after the final code changes (output directory `.next-release`, kept separate from the dev server).
- Browser: 63 page/viewport checks across RU/TG/EN home, support, and privacy pages at 320, 375, 390, 430, 768, 1024, and 1440 px had HTTP 200, no horizontal overflow, and no page exceptions. This excludes database-backed catalog/API workflows and all account/admin workflows.
- PostgreSQL readiness and migration: the isolated PostgreSQL TCP endpoint was unreachable; no online migration was applied. Offline Alembic SQL generation through revision 0011 passed.
- API registration/login, catalog persistence, calculator against PostgreSQL, order workflows, admin workflows, backups, and mail delivery were not end-to-end tested in this pass.

## Files changed

- Backend: `app/main.py`, `app/api/admin_routes.py`, `app/api/routes.py`, `app/api/support_routes.py`, `app/models/car.py`, `app/models/__init__.py`, `app/models/payment.py`, `app/models/support.py`, `app/schemas/admin.py`, `app/schemas/car.py`, `app/schemas/support.py`, `app/services/payment_providers.py`, Alembic `0011_demo_inventory_support_payments.py`, and `tests/test_platform_foundations.py`.
- Frontend: `app/globals.css`, `app/[lang]/support/page.tsx`, `app/[lang]/legal/[slug]/page.tsx`, `app/admin/support/page.tsx`, `components/admin-panel.tsx`, `components/catalog-page.tsx`, `components/crm-panel.tsx`, `components/vehicle-detail.tsx`, `components/support-admin-panel.tsx`, `lib/admin-i18n.ts`, `lib/api.ts`, `next.config.ts`.
- Docs: `docs/PAYMENTS_PRELAUNCH.md`, `docs/SECURITY_REVIEW.md`, this report, and `.gitignore` for isolated Next build output.

## Required owner actions before commercial launch

1. Restore/start the isolated test PostgreSQL cluster, confirm its test-only database identity, then apply and verify migration 0011.
2. Supply or approve a vetted vehicle-photo library with commercial rights and per-image attribution/license details; approve clearly labeled demo specifications/prices before a seed set is created.
3. Decide if USD, TJS, and EUR should be presentation-only; select and approve an FX source and staleness policy before showing conversion values.
4. Provide mail-service choice and credentials through backend-only secret configuration; verify SPF/DKIM/DMARC and delivery handling. Do not put credentials in the frontend.
5. Register the company, open its business bank account, select a supported provider, complete underwriting, and have counsel approve commercial legal terms before payment activation.
6. Have local counsel review privacy, cookies, terms, refunds, consumer/import representations, company identity disclosures, and cross-border data handling.
7. Configure production database backup/restore, secret rotation, monitoring, rate limits/proxy controls, security scans, and separately approved production deployment.

## Local commands

From `C:\Users\Asus Notebook\QHI-AUTO`:

```powershell
cd backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

In a second terminal:

```powershell
cd frontend
$env:NEXT_DIST_DIR=".next-qa"
..\tools\nodejs\npm.cmd run dev -- --port 3002
```

Open `http://localhost:3002/ru`, `/tg`, or `/en`. The current isolated visual-review dev server uses `NEXT_DIST_DIR=.next-qa`; standard production commands use the default `.next` output. The API must be configured against a reachable local/test database for database-backed functions. Never run migrations against production without a reviewed backup and explicit deployment procedure.
