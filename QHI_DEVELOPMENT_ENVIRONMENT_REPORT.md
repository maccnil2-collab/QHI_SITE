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
- Backend tests: 27 passed; one Starlette/httpx deprecation warning remains.
- Python `compileall`: passed.
- Alembic generated offline PostgreSQL SQL through migration head `0006_crm`.
- Uvicorn served OpenAPI with 29 paths, including auth, customer orders, CRM, and admin routes.
- Frontend package and TypeScript JSON manifests parse. Three account locale dictionaries have matching 29-key schemas and execute under Node's TypeScript stripping mode. All 17 TypeScript/TSX files pass compiler syntax transpilation using VS Code's bundled TypeScript.
- `git diff --check`: passed before the latest checkpoint commits.

## Outstanding issues

- npm registry requests fail with EACCES and the local npm cache has no usable Next.js packages. Therefore Next build, TypeScript typecheck, and Playwright runs have not been performed.
- PostgreSQL accepts TCP connections, but password authentication was not available without private credentials. No password was guessed, printed, or written. Migrations have only been generated offline, not applied to the running instance.
- RAM and free disk are point-in-time measurements. Figma version was not queried. The Windows registry identity/build combination is recorded verbatim and should be checked in Settings if the exact Windows edition is operationally important.
- See `reports/ENVIRONMENT_AUDIT.md` and `docs/DEVELOPMENT_STATUS.md` for implementation and security status.

## Recommended next steps

1. Restore approved npm registry access, install from a lockfile, then run Next build and typecheck before browser tests.
2. Use the existing private PostgreSQL credentials locally to apply migrations and run database integration tests; keep credentials out of command output and repository files.
3. Add Playwright to the locked frontend toolchain and exercise registration, order lifecycle, staff access, CRM, and mobile layouts.
4. Complete CRM translations, email verification/recovery, secure document storage, production rate limiting, backup/restore drills, and deployment configuration before a public launch.
