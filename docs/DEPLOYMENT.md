# Deployment starter

`compose.yaml` is a single-host deployment starter for review and controlled staging. It runs PostgreSQL, FastAPI, and the standalone Next.js server. PostgreSQL is reachable only on the private Compose network and does not claim the host's port 5432. API and web ports bind to loopback; place a maintained TLS reverse proxy in front before external access. This configuration is not a production launch approval.

## Prerequisites and secrets

- Docker Engine with the Compose plugin and outbound access to official Python, Node, and PostgreSQL images and the npm registry.
- The API image uses Python 3.11 and installs only `requirements-prod.txt`; pytest stays in the development requirements. The web image uses [Node 24 LTS](https://nodejs.org/en/about/previous-releases), which is also compatible with the installed Next.js 15 line.
- Before a real release, replace mutable major/minor image tags with reviewed immutable digests and define a scheduled patch process.
- A committed frontend `package-lock.json`. The repository currently has none; `npm ci` in the image intentionally fails until one is generated and reviewed.
- A private root `.env` copied from `.env.compose.example`. Generate unique random values for `POSTGRES_PASSWORD` and `ADMIN_API_KEY` in a password manager or approved secret manager. Use URL-safe characters for the database password because it is embedded in `DATABASE_URL`. Do not commit `.env` or paste secret values into logs or support messages.
- Set `NEXT_PUBLIC_API_URL` to the public API base URL including `/api/v1`, and set `CORS_ORIGINS` to the exact public website origin. These values are embedded in the frontend at build time.
- Set `FORWARDED_ALLOW_IPS` to the exact network address(es) of trusted reverse proxies that connect to the API. Keep the default loopback-only trust when no proxy forwarding is configured; never trust arbitrary clients.

## First deployment

1. Review the compose file, image tags, firewall, TLS proxy, and secret values for the target host. Keep PostgreSQL off public interfaces.
2. Start the database and wait until it reports healthy:

   ```sh
   docker compose up -d db
   docker compose ps
   ```

3. Apply migrations as a separate, reviewable release action:

   ```sh
   docker compose run --build --rm api alembic upgrade head
   ```

4. Build and start the API and web services:

   ```sh
   docker compose up --build -d api web
   docker compose ps
   ```

5. Verify `/api/v1/health`, `/api/v1/ready`, and the website through the TLS proxy. Production mode disables FastAPI Swagger, ReDoc, and OpenAPI routes. Confirm proxy headers are accepted only from the configured trusted proxy addresses.
6. Establish encrypted, off-host database and private document backups; perform restore drills before customer data is accepted. Define retention, malware scanning, monitoring, alerting, incident response, and patch ownership.

The compose configuration uses named volumes for PostgreSQL and uploaded order documents. Docker named volumes alone are not a backup strategy. Migration rollback is not automatic: take and verify a database backup before schema changes, and follow a tested forward-repair procedure.

## Current release blockers

- The frontend lockfile and all Next.js build/browser verification are still missing because npm registry access has failed in this environment.
- Docker is not installed on the development machine, so image builds and Compose health checks have not been executed here.
- No private database credentials are configured, so migrations have only been validated as offline SQL and not applied to PostgreSQL.
- Email verification/recovery, production cookie-based session restoration, durable scanned document storage, distributed rate limiting, operational backups, and production monitoring still need implementation and verification.
