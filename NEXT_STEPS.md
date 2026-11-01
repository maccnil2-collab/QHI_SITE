# QHI AUTO next steps

1. **Frontend build gate:** restore npm registry access, create/review the lockfile, then run `npm ci`, `npm run typecheck`, and `npm run build` from `frontend/`. Add lint and Playwright tooling after the dependency source is available.
2. **Database gate:** provision a disposable PostgreSQL database and set `DATABASE_URL` privately in the shell; run `alembic upgrade head` and database-backed integration tests. Do not target a user or production database for exploratory checks.
3. **Browser gate:** run the app against that test database and exercise cookie restoration, CSRF-protected mutations, catalog quotes, customer ownership, CRM roles, and mobile layouts.
4. **Then continue feature work:** implement verified email plus recovery and replace the in-memory limiter before multi-worker deployment; complete durable malware-scanned order-document storage before accepting real customer files.
5. **Production gate:** perform reviewed image builds, staging Compose checks, TLS/proxy verification, secret rotation, backup/restore drills, and monitoring setup. Do not expose the service publicly until these are complete and approved.

Current local frontend commands are `npm run typecheck` and `npm run build`, but they cannot run until dependencies are installed. Backend tests can now run from the repository root with `.\.venv\Scripts\python.exe -m pytest -q`.
