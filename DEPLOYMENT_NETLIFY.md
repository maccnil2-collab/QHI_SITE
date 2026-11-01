# Netlify production deployment

The frontend is a Next.js 15 App Router application. Netlify's managed OpenNext adapter supports the current SSR, route, and image features; `netlify.toml` keeps the repository rooted in `frontend/` and validates the public API URL before building.

## Services and data

- Netlify hosts the Next.js frontend only.
- FastAPI and PostgreSQL remain separate services. The local `compose.yaml` is not a public production database service.
- Car images currently use the URLs stored in `car_images`; a persistent, licensed image store (for example, an owner-controlled object-storage bucket) is still needed before publishing a large catalog.

## Netlify environment

Set `NEXT_PUBLIC_API_URL` in the Netlify site environment to the public HTTPS FastAPI URL ending in `/api/v1`. The build intentionally stops if this is missing, uses HTTP, or points to localhost. Configure the FastAPI `CORS_ORIGINS` with the exact frontend origin after confirming the site identity and domain. Never set database credentials or admin secrets in `NEXT_PUBLIC_*` variables.

## Remaining production prerequisites

1. Confirm the Netlify site `electro-tj` is in the owner's account and inspect its current deploys before linking or publishing. The current environment has no Netlify CLI, authenticated Netlify integration, or Netlify credentials, so it cannot verify ownership or deploy safely.
2. Choose and configure a persistent production PostgreSQL service and a separate FastAPI host. Set production secrets in the hosting provider's secret manager, not Git.
3. Back up the production database, review the Alembic migration, then apply it to the intended database.
4. Configure durable image storage, upload only licensed model-matching images, and retain each image's author, source, and license attribution.
5. Populate and verify the inventory before publishing any records. Do not publish placeholder or unverified prices/specifications.
6. Configure `NEXT_PUBLIC_API_URL`, backend CORS, and health checks; then deploy and run browser/API smoke tests against the actual public environment.
