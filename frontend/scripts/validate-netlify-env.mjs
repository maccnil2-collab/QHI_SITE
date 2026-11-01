const apiUrl = process.env.NEXT_PUBLIC_API_URL;

if (!apiUrl) {
  console.error("Set NEXT_PUBLIC_API_URL in the Netlify site environment before deploying (HTTPS FastAPI base URL ending in /api/v1).");
  process.exit(1);
}

let parsed;
try {
  parsed = new URL(apiUrl);
} catch {
  console.error("NEXT_PUBLIC_API_URL must be an absolute HTTPS URL.");
  process.exit(1);
}

if (parsed.protocol !== "https:" || ["localhost", "127.0.0.1", "::1"].includes(parsed.hostname)) {
  console.error("Production NEXT_PUBLIC_API_URL must use HTTPS and must not point to localhost.");
  process.exit(1);
}

if (!parsed.pathname.replace(/\/$/, "").endsWith("/api/v1")) {
  console.error("NEXT_PUBLIC_API_URL must end with /api/v1.");
  process.exit(1);
}
