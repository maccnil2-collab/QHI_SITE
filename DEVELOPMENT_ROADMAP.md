# QHI AUTO development roadmap

Priorities are ordered by dependency and risk. Do not publish legal, tariff, inventory, or delivery claims without owner-provided values.

## Progress at checkpoint `ec0d0c2`

- Completed: isolated PostgreSQL test cluster; all nine migrations applied; schema/model comparison clean; one opt-in real PostgreSQL API workflow test passes.
- Completed: localized vehicle detail route, catalog navigation, and authenticated quote persistence; ESLint and desktop/mobile Playwright source configuration added.
- Blocked: npm registry socket access (`EACCES` before HTTP), so lockfile, installed toolchain, semantic typecheck, lint, Next build, and browser execution remain outstanding.

## 1. Establish reproducible frontend verification — in progress

- Restore approved npm registry access.
- Resolve and review the Next/React/tooling dependency graph, generate `package-lock.json`, and use `npm ci` thereafter.
- Run TypeScript semantic checking and production build; fix all compiler/build failures.
- Run the configured lint and Playwright coverage for authentication, catalog, quotes, account/orders, CRM/admin authorization, and responsive layouts.

## 2. Verify persistence against PostgreSQL — basic workflows verified

- Configure a private disposable test database without committing credentials.
- Applied all migrations through `0009_crm_analytics_indexes` on an isolated fresh database; `alembic check` reports no schema drift.
- One API integration workflow covers sessions, quotes, orders, CRM, and admin. Add targeted concurrency/transaction tests for order transitions, document metadata, and ownership.
- Establish backup/restore and forward-repair procedures before production data.

## 3. Close identity and security gaps

- Design email verification and password recovery, with token expiry, single-use semantics, rate limits, and an approved mail adapter.
- Replace process-local rate limits where multi-worker deployment is required.
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
