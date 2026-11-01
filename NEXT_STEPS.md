# QHI AUTO next steps

1. **Frontend build gate:** restore outbound npm registry access (or provide an approved mirror), create/review the lockfile, then run `npm ci`, `npm run typecheck`, `npm run lint`, and `npm run build` from `frontend/`.
2. **Browser gate:** set `QHI_TEST_DATABASE_URL` to `postgresql+psycopg://postgres@127.0.0.1:55439/qhi_auto_test`, then run `npm run test:e2e` from `frontend/`. The config starts isolated API/web dev servers on loopback ports 18000/13000.
3. **Database gate:** the isolated PostgreSQL cluster has all nine migrations applied and a passing API integration workflow. For a fresh test database, verify its target and run `alembic upgrade head`; never target production.
4. **Then continue feature work:** implement verified email plus recovery and replace the in-memory limiter before multi-worker deployment; complete durable malware-scanned order-document storage before accepting real customer files.
5. **Production gate:** perform reviewed image builds, staging Compose checks, TLS/proxy verification, secret rotation, backup/restore drills, and monitoring setup. Do not expose the service publicly until these are complete and approved.

Frontend commands for typecheck, lint, production build, and Playwright are configured but cannot run until dependencies are installed. See [FRONTEND_DATABASE_READINESS.md](FRONTEND_DATABASE_READINESS.md) for actual network, PostgreSQL, and scenario results. Backend tests run from the repository root with `.\.venv\Scripts\python.exe -m pytest -q`; set `QHI_TEST_DATABASE_URL` to opt into the live PostgreSQL test.

The local test PostgreSQL service and API currently run on loopback (`127.0.0.1:55439` and `127.0.0.1:8000`). The backend reads the ignored `backend/.env`; stop the local processes when they are no longer needed.
