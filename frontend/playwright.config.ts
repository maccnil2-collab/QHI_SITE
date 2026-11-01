import { randomBytes } from "node:crypto";
import { defineConfig, devices } from "@playwright/test";

const databaseUrl = process.env.QHI_TEST_DATABASE_URL;
if (!databaseUrl) {
  throw new Error("Set QHI_TEST_DATABASE_URL to a disposable loopback PostgreSQL database ending in _test.");
}
const database = new URL(databaseUrl);
if (!new Set(["127.0.0.1", "localhost", "[::1]", "::1"]).has(database.hostname) || !database.pathname.slice(1).endsWith("_test")) {
  throw new Error("Playwright refuses to start unless QHI_TEST_DATABASE_URL targets a loopback *_test database.");
}

const apiPort = Number(process.env.QHI_E2E_API_PORT ?? "18000");
const webPort = Number(process.env.QHI_E2E_WEB_PORT ?? "13000");
const apiBase = `http://127.0.0.1:${apiPort}/api/v1`;
const webBase = `http://127.0.0.1:${webPort}`;
const adminKey = process.env.QHI_E2E_ADMIN_API_KEY ?? randomBytes(32).toString("base64url");
const npmCommand = process.env.npm_execpath
  ? `"${process.execPath}" "${process.env.npm_execpath}"`
  : "npm";
process.env.QHI_E2E_API_URL = apiBase;
process.env.QHI_E2E_ADMIN_API_KEY = adminKey;

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  forbidOnly: Boolean(process.env.CI),
  retries: 0,
  workers: 1,
  reporter: "list",
  outputDir: "./test-results",
  use: {
    baseURL: webBase,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: [
    { name: "desktop-chromium", use: { ...devices["Desktop Chrome"] } },
    { name: "mobile-chromium", use: { ...devices["iPhone 13"], browserName: "chromium" } },
  ],
  webServer: [
    {
      command: `..\\.venv\\Scripts\\python.exe -m uvicorn app.main:app --app-dir ..\\backend --host 127.0.0.1 --port ${apiPort}`,
      url: `${apiBase}/ready`,
      env: { DATABASE_URL: databaseUrl, APP_ENV: "development", CORS_ORIGINS: webBase, ADMIN_API_KEY: adminKey },
      timeout: 60_000,
      reuseExistingServer: false,
    },
    {
      command: `${npmCommand} run dev -- --hostname 127.0.0.1 --port ${webPort}`,
      url: `${webBase}/en`,
      env: { NEXT_PUBLIC_API_URL: apiBase, NEXT_TELEMETRY_DISABLED: "1" },
      timeout: 120_000,
      reuseExistingServer: false,
    },
  ],
});
