# QHI AUTO web

Install dependencies after npm registry access is available with `npm install`; commit the generated lockfile, then use `npm ci` for repeatable installs. Run `npm run dev` for development. The API base URL is `NEXT_PUBLIC_API_URL` (see `.env.example`). Run `npm run build` and `npm run typecheck` before release. The current local environment has no Next.js dependencies or lockfile, so the frontend has not been built.

The standalone production image and Compose release sequence are documented in [`../docs/DEPLOYMENT.md`](../docs/DEPLOYMENT.md).
