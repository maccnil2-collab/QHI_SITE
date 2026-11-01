# QHI AUTO development roadmap

Priorities are ordered by dependency and risk. Do not publish legal, tariff, inventory, or delivery claims without owner-provided values.

## 1. Establish reproducible frontend verification

- Restore approved npm registry access.
- Resolve and review the Next/React/tooling dependency graph, generate `package-lock.json`, and use `npm ci` thereafter.
- Run TypeScript semantic checking and production build; fix all compiler/build failures.
- Add a lint script/toolchain and Playwright E2E coverage for authentication, catalog, quotes, account/orders, CRM/admin authorization, and responsive layouts.

## 2. Verify persistence against PostgreSQL

- Configure a private disposable test database without committing credentials.
- Apply all migrations through `0009_crm_analytics_indexes`; verify schema constraints, indexes, and expected revision state.
- Run API integration and concurrency/transaction tests for sessions, quote snapshots, order transitions, CRM ownership, and document metadata.
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
