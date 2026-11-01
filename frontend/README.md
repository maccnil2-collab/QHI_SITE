# QHI AUTO web

This is the Next.js App Router application. Locale routes are `/ru`, `/tg`, and `/en`; public vehicle detail routes are `/{locale}/cars/{slug}`.

## Install and verify

The project currently has no `package-lock.json` because access to the configured npm registry was denied by the development environment. Once approved registry/mirror access is available:

```powershell
npm install --no-audit --no-fund
npm ci
npm run typecheck
npm run lint
npm run build
```

Commit and review the generated lockfile. `npm ci` is the repeatable install for later builds.

## Playwright

Playwright E2E tests require a disposable local PostgreSQL database migrated to head and seeded by `backend/tests/test_postgres_workflows.py`. The Playwright config checks that its DSN uses a loopback host and a database name ending in `_test`; it starts the API and web servers on loopback ports 18000 and 13000.

```powershell
$env:QHI_TEST_DATABASE_URL = 'postgresql+psycopg://postgres@127.0.0.1:55439/qhi_auto_test'
npm run test:e2e
```

The suite covers locale/detail navigation, customer registration and session restoration, quote history, order creation, CRM status management, and admin catalog access on desktop and mobile Chromium. Dependencies and browser binaries must first be installed. These browser tests have not yet run in this environment.

Set `NEXT_PUBLIC_API_URL` to the API base URL (default `http://localhost:8000/api/v1`). For local development, start the backend with a disposable test `DATABASE_URL`; never point the E2E setup at production.
