# QHI AUTO deployment

## Application shape

QHI AUTO is a three-part application: a Next.js server, a FastAPI service, and PostgreSQL. The frontend calls the API directly from the browser and customer authentication uses secure, HTTP-only cookies plus CSRF protection. Do not deploy the backend as a static Netlify site or expose PostgreSQL to the public internet.

Two hosting shapes fit the current code:

- **Single VPS:** use the root `compose.yaml` for PostgreSQL, API, and web, then put a maintained HTTPS reverse proxy in front. The Compose file binds application ports to loopback and keeps PostgreSQL on the private Compose network.
- **Managed hosting:** use a platform that supports separate Docker web services and managed PostgreSQL (for example, Render). Deploy the API as a web service, the Next.js standalone image as a web service, and PostgreSQL as a private managed database. Render documents Docker web services, private service networking, managed PostgreSQL, and public HTTPS service URLs in its [web service](https://render.com/docs/web-services), [Docker](https://render.com/docs/docker), and [PostgreSQL](https://render.com/docs/postgresql) documentation.

The current workspace does not contain a production deployment configuration for a particular provider. Choose the account, region, service plans, and backup policy before provisioning resources; managed production services can incur recurring charges.

## Required production settings

- `APP_ENV=production` on the API. This hides Swagger, ReDoc, and OpenAPI.
- `DATABASE_URL` must point to a newly provisioned production database, use the `postgresql+psycopg://` SQLAlchemy driver, and remain private. Do not reuse the local test database.
- `CORS_ORIGINS` must contain only the exact public website origin(s), including the scheme and excluding path suffixes.
- `ADMIN_API_KEY` must be independently generated and stored in the hosting provider's secret manager. Never commit it or pass it as a Docker build argument.
- `FORWARDED_ALLOW_IPS` must list only the actual trusted reverse proxy addresses. Do not use `*`; confirm the host's proxy address model before enabling forwarded client IPs.
- `NEXT_PUBLIC_API_URL` is embedded in the frontend at build time and must point to the public API origin followed by `/api/v1`.
- Keep the site and API on the same site (for example `www.example.com` and `api.example.com`) so browser cookie and CSRF protections work as intended.
- Leave `DOCUMENT_STORAGE_PATH` unset until durable private storage, backups, and file scanning are configured. Upload endpoints stay disabled in that state.

## VPS deployment with Compose

1. Provision a supported Linux host with Docker Engine and the Compose plugin. Configure a domain and firewall; allow public access only through the HTTPS reverse proxy.
2. Create a private root `.env` from `.env.compose.example`. Generate the database password and admin key in a password manager, set the exact website CORS origin, and set `NEXT_PUBLIC_API_URL` to the public API URL ending in `/api/v1`.
3. Configure `FORWARDED_ALLOW_IPS` for the proxy's exact address on the private network. Keep PostgreSQL unexposed.
4. Start PostgreSQL and verify the service is healthy:

   ```sh
   docker compose up -d db
   docker compose ps
   ```

5. Back up the new database, then apply migrations as a separate release action:

   ```sh
   docker compose run --build --rm api alembic upgrade head
   ```

6. Build and start the API and web services:

   ```sh
   docker compose up --build -d api web
   docker compose ps
   ```

7. Verify `/api/v1/health`, `/api/v1/ready`, the catalog, authentication, quote flow, and lead form through HTTPS. Confirm `/docs`, `/redoc`, and `/openapi.json` return 404. Test from mobile networks before accepting customer data.
8. Establish encrypted off-host database and private document backups, restore drills, monitoring, patch ownership, and incident procedures.

The web and API containers bind to `127.0.0.1` on the host. Configure the TLS proxy to route to those local ports. Never publish database port 5432.

## Deployment readiness observed in the development workspace

- Frontend package lockfile, TypeScript check, ESLint, production build, and desktop/mobile Chromium browser checks are available and pass for the current frontend source.
- Backend unit and security suite: 53 passed. The PostgreSQL end-to-end test is opt-in and was skipped because `QHI_TEST_DATABASE_URL` was not set.
- A local API launched in production mode returned 200 from `/api/v1/health`, 401 from the unauthenticated customer endpoint, and 404 from `/docs`; security headers were present. `/api/v1/ready` and the read-only catalog query timed out because the isolated local `*_test` PostgreSQL service was not reachable. No production database was accessed.
- Docker, a provider CLI, and a Git remote are not configured in the workspace. No cloud account, production database, domain, or deployment credentials are available here. As a result, container publishing and public HTTPS verification have not been performed.

Do not treat a successful frontend build or the API health endpoint as a completed production deployment. A release is ready only after the production database is reachable and migrated, `/api/v1/ready` succeeds, the provider deployment is live, and the browser journeys above pass against that deployment.
