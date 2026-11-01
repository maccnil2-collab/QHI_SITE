# QHI AUTO Development Environment Report

Audit date: 2026-11-01  
Workspace: `C:\Users\Asus Notebook\QHI-AUTO`

## Existing components detected

| Component | Detected version / state |
|---|---|
| Windows | Registry reports Windows 10 Pro, display version 25H2, build 26200 |
| PowerShell | 5.1.26100.9711 |
| Python | 3.11.9; project `.venv` is active and usable |
| pip | 26.2.2; `pip check` reports no broken requirements |
| FastAPI | 0.162.0 |
| SQLAlchemy | 2.1.6 |
| Alembic | 1.20.1 |
| Pydantic | 2.14.2 |
| psycopg | 3.3.6 |
| pytest | 9.2.0 |
| Node.js / npm | 26.13.0 / 11.20.0, project-local under `tools` |
| Git | 2.56.0.windows.4, portable under `tools` |
| VS Code | 1.134.0; command available |
| Figma | Registered in Windows Start Apps; version was not queried |
| Codex CLI | 0.166.0 |
| PostgreSQL | 18.6 service `postgresql-x64-18` is running; localhost accepts TCP connections |
| Next.js / React / TypeScript / Tailwind | Manifest/source only; dependencies and lockfile are unavailable |
| Playwright | Not installed in the project or `.venv` |

## Machine capacity and PATH

- C: has 366.37 GB free of 951.97 GB at audit time.
- Available RAM measured about 5.6 GB during the read-only check, above the requested 5 GB target at that moment.
- No PATH entries or Windows settings were changed. Node.js and Git are project-local; VS Code, Codex CLI, and Python commands were already discoverable.
- Figma is registered in Start Apps but not on PATH, which is expected for a desktop app.

## Additional installations and disk use

- No programs or Python/frontend dependencies were installed during this work.
- Added installed-program disk usage: 0 bytes.
- Project source, docs, migrations, and tests were added; no installer or downloaded package cache was added.
- The user's existing `test.txt` remains unmodified and outside Git commits.

## Verification results

- Python, pip, Node.js, npm, Git, VS Code, and Codex CLI report versions.
- `pip check`: passed.
- Backend tests: 46 passed; one Starlette/httpx deprecation warning remains.
- Python `compileall`: passed.
- Alembic generated offline PostgreSQL SQL through migration head `0009_crm_analytics_indexes`.
- OpenAPI exposes 40 paths, including date-bounded CRM analytics, database readiness, customer session/notification controls, staff document upload and owner/visibility-scoped downloads, orders, and admin routes.
- API responses include baseline anti-sniffing, clickjacking, referrer, and permissions-policy headers; readiness returns a generic 503 without leaking database errors.
- Frontend package and TypeScript JSON manifests parse. Three account locale dictionaries have matching 44-key schemas and CRM dictionaries matching 85-key schemas; both execute under Node's TypeScript stripping mode. All 18 TypeScript/TSX files pass compiler syntax parsing using VS Code's bundled TypeScript, including the localized admin dictionary. Admin catalog, tariff, and customer/staff role screens provide ru/tg/en labels; their 73 translation keys match across all locales and are non-empty.
- `git diff --check`: passed before the latest checkpoint commits.

## Outstanding issues

- npm registry requests fail with EACCES and the local npm cache has no usable Next.js packages. Therefore Next build, TypeScript typecheck, and Playwright runs have not been performed.
- PostgreSQL accepts TCP connections; a read-only local query to the default `postgres` database also failed without credentials. `DATABASE_URL` is not configured and no `backend/.env` exists. No password was guessed, printed, or written. Migrations have only been generated offline, not applied to the running instance.
- RAM and free disk are point-in-time measurements. Figma version was not queried. The Windows registry identity/build combination is recorded verbatim and should be checked in Settings if the exact Windows edition is operationally important.
- See `reports/ENVIRONMENT_AUDIT.md` and `docs/DEVELOPMENT_STATUS.md` for implementation and security status.

## Recommended next steps

1. Restore approved npm registry access, install from a lockfile, then run Next build and typecheck before browser tests.
2. Configure `DATABASE_URL` privately, apply migrations through `0009_crm_analytics_indexes`, and run PostgreSQL integration tests; keep credentials out of command output and repository files.
3. Add Playwright to the locked frontend toolchain and exercise registration, order lifecycle, staff access, CRM, and mobile layouts.
4. Complete email verification/recovery, production object storage and malware scanning, production rate limiting, backup/restore drills, and deployment configuration before a public launch.
