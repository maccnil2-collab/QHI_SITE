# QHI AUTO web

Install dependencies from the lockfile once the configured npm registry is reachable (`npm ci`), then run `npm run dev`. The API base URL is `NEXT_PUBLIC_API_URL` (see `.env.example`). `npm run build` and `npm run typecheck` are the frontend release checks. Current local environment has no Next.js dependency tree or lockfile, so the UI has not been built yet.
