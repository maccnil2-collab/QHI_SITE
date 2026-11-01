# QHI AUTO security review — development scope

## Implemented controls observed

- Passwords use the existing password hashing service; account sessions are opaque, hashed at rest, expiring, and revocable.
- Cookie-authenticated unsafe requests require a session-bound CSRF token. Session cookies are configured by the existing auth flow as HttpOnly.
- Admin API token comparison uses the existing constant-time check; customer-facing staff routes require manager/admin roles.
- SQL access is expressed through SQLAlchemy statements and bound values. New public support input is Pydantic-validated, bounded, stripped, and rate-limited.
- Support ticket listing and status updates require staff authorization; each status change is recorded as an event.
- Security response headers include `X-Content-Type-Options`, `X-Frame-Options`, referrer and permissions policy.
- Payment adapter refuses checkout, webhook acceptance, and refund; the public site does not accept card details.

## Not verified / remaining work

- No external penetration test, dependency vulnerability scan, threat model sign-off, backup-restore drill, production secret audit, or production deployment test was performed in this development pass.
- The new schema migration is pending because the isolated loopback test PostgreSQL host is currently unreachable; no database migration was applied.
- Support mail is not configured and no email is claimed to have been sent.
- Image upload storage validation/virus scanning and production object storage have not been added.
- Rate limiting and security headers are application-level defenses and do not replace a production proxy/WAF, monitoring, and incident response plan.
- This document does not claim PCI DSS, GDPR, or other certification or legal compliance.
