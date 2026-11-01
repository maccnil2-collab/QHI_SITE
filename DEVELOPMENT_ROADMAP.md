# QHI AUTO development roadmap

Priorities are ordered by dependency and risk. Do not publish legal, tariff, inventory, or delivery claims without owner-provided values.

## Progress through frontend readiness work (latest commit `38cbe16`)

- Completed: isolated PostgreSQL test cluster; all ten migrations applied; schema/model comparison clean; PostgreSQL API workflow test passes, including concurrent shared rate-limit requests.
- Completed: localized vehicle detail route, catalog navigation, and authenticated quote persistence; ESLint and desktop/mobile Playwright source configuration added.
- Completed: migration `0010_shared_rate_limit_buckets`; authentication, quote, lead, and document limits are backed by atomic PostgreSQL counters, verified across independent limiter instances.
- Frontend dependencies and `package-lock.json` are installed/generated. Typecheck, lint and production build pass. npm audit is blocked by registry `EACCES`; installed PostCSS and minimatch advisory paths require lockfile-safe upgrades and a subsequent audit.
- Added a frontend `packageManager` pin and engine constraints for Node/npm; this documents the expected toolchain but does not replace a generated lockfile or installation verification.
- Fixed TypeScript issues found by the bundled compiler: duplicate CRM dictionary keys, missing CRM loading/error labels, and the admin car `published` field omitted from the API response. The isolated locale-dictionary typecheck passes; full app check still cannot resolve absent dependencies.
- Fixed admin vehicle edits failing with a PostgreSQL unique violation: existing locale rows are now updated in place. The live integration workflow now verifies edit and publish/unpublish round trips.
- Customer sessions now have explicit PostgreSQL integration assertions returning 403 on CRM lead/overview and staff order routes; the workflow passes on both the source and restored test database.
- Reapplied all ten migrations to a newly created UTF-8 database from an empty schema; `alembic check` and the end-to-end PostgreSQL workflow passed there.

## 1. Establish reproducible frontend verification — in progress

- DONE: Install dependencies and generate the npm v3 lockfile in the owner CMD.
- DONE: TypeScript semantic check, ESLint, and Next.js production build pass.
- PARTIAL: E2E desktop/mobile locale/detail and CRM/admin flows pass; registration/session restoration runs, but quote calculation and persistence are blocked by an empty numeric form field at submit. Diagnose and repair this scenario.
- BLOCKED: npm audit registry access and Playwright browser CDN downloads return EACCES from the Codex shell. Analyze and remediate current advisories after network access is available.
- Verify lockfile via clean `npm ci` and review/escalate flagged transitive dependency versions.
- Typecheck, lint and production build now pass; retain these in CI.
- Run the configured lint and Playwright coverage for authentication, catalog, quotes, account/orders, CRM/admin authorization, and responsive layouts.

## 2. Verify persistence against PostgreSQL — basic workflows verified

- Configure a private disposable test database without committing credentials.
- Applied all migrations through `0010_shared_rate_limit_buckets` on an isolated test database; `alembic check` reports no schema drift. PostgreSQL rate limits are atomic and shared between workers.
- One API integration workflow covers sessions, quotes, orders, CRM, and admin. Add targeted concurrency/transaction tests for order transitions, document metadata, and ownership.
- A custom-format backup of populated test data restored into a fresh UTF-8 database at migration head; all 18 table row counts and deterministic row-content hashes matched. Define encrypted backup retention and recovery ownership before production use.
- Establish forward-repair procedures before production data.

## 3. Close identity and security gaps

- Design email verification and password recovery, with token expiry, single-use semantics, rate limits, and an approved mail adapter.
- Add automated retention/observability for rate-limit buckets and tune limits behind a production reverse proxy.
- Review staff session lifecycle, admin bootstrap-key migration/rotation, audit retention, proxy trust, CORS, and security headers.
- Add browser-level CSRF and cross-origin regression coverage.

## 4. Complete operational customer workflows

- Confirm localized account, order, document, and notification flows in a real browser.
- Add accessible loading/error/empty states and verify keyboard/small-screen behavior.
- Use owner-approved vehicle data, localized copy, images, exchange rates, and tariff inputs only.

## 5. Production deployment readiness

- Add durable private object storage, malware scanning, retention controls, and tested restore for documents.
- Pin reviewed container image digests, configure TLS/reverse-proxy trust, monitoring, alerting, encrypted backups, and incident ownership.
- Build images and exercise Compose health and migration release steps in a controlled staging environment.

## Completion bar

Each release slice needs repeatable checks and a Git checkpoint. A source-level implementation is not considered browser-, database-, or production-verified until those environments have actually been exercised.
