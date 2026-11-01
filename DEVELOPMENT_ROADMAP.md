# QHI AUTO development roadmap

Priorities are ordered by dependency and risk. Do not publish legal, tariff, inventory, or delivery claims without owner-provided values.

## Progress at checkpoint `92f9ea4`

- Completed: isolated PostgreSQL test cluster; all ten migrations applied; schema/model comparison clean; PostgreSQL API workflow test passes, including concurrent shared rate-limit requests.
- Completed: localized vehicle detail route, catalog navigation, and authenticated quote persistence; ESLint and desktop/mobile Playwright source configuration added.
- Completed: migration `0010_shared_rate_limit_buckets`; authentication, quote, lead, and document limits are backed by atomic PostgreSQL counters, verified across independent limiter instances.
- Pending: the owner reports working Node 26.13.0/npm 11.20.0 and registry `PONG` in their terminal, while the Codex execution shell cannot locate those executables. Connect that runtime to the worktree, then generate the lockfile and run semantic typecheck, lint, Next build, and browser E2E.
- Fixed TypeScript issues found by the bundled compiler: duplicate CRM dictionary keys, missing CRM loading/error labels, and the admin car `published` field omitted from the API response. The isolated locale-dictionary typecheck passes; full app check still cannot resolve absent dependencies.
- Fixed admin vehicle edits failing with a PostgreSQL unique violation: existing locale rows are now updated in place. The live integration workflow now verifies edit and publish/unpublish round trips.
- Customer sessions now have explicit PostgreSQL integration assertions returning 403 on CRM lead/overview and staff order routes; the workflow passes on both the source and restored test database.
- Reapplied all ten migrations to a newly created UTF-8 database from an empty schema; `alembic check` and the end-to-end PostgreSQL workflow passed there.

## 1. Establish reproducible frontend verification — in progress

- Restore approved npm registry access.
- Resolve and review the Next/React/tooling dependency graph, generate `package-lock.json`, and use `npm ci` thereafter.
- Run TypeScript semantic checking and production build; fix all compiler/build failures.
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
