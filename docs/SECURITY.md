# Security Baseline

- Never put passwords, tokens, private keys, or real personal data in source, fixtures, logs, or Git. `.env` files are ignored; production secrets belong in a secret manager.
- Validate inputs with Pydantic and use SQLAlchemy parameterized queries.
- Store passwords only with a modern password KDF; limit token lifetime and support session revocation.
- Enforce least-privilege roles and server-side authorization. The bootstrap admin API currently uses a private random 32+ character environment key and constant-time comparison; replace it with staff accounts/roles before multi-admin production. Never store this key in browser storage; the current panel keeps it in page memory. Audit administrative changes and rate-limit authentication.
- Restrict CORS to known origins. Session cookies should be HttpOnly, Secure, and SameSite, with CSRF protection when cookies authenticate requests.
- Order uploads are restricted to bounded PDF/JPEG/PNG payloads with signature checks, sanitized display names, opaque storage keys, owner/visibility checks, and attachment-only responses. The local filesystem adapter is disabled until an explicit private path is configured. Production still requires malware scanning, durable private object storage, and retention/restore controls. Do not trust user-provided filenames or URLs.
- Email is unverified on registration; no password recovery, mail, SMS, or payment adapter is active. Do not send transactional messages to unverified addresses. Do not perform payments, legal actions, or outbound notifications without an explicit approved business flow.
- Client errors must not expose SQL, secrets, local paths, or stack traces.
- Production requires TLS, monitored backups with restore drills, dependency updates, and operational monitoring.
