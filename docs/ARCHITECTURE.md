# QHI AUTO Architecture

## Services
- `frontend/`: Next.js App Router, React, TypeScript, Tailwind CSS; locale routes `/ru`, `/tg`, `/en`.
- `backend/`: FastAPI, Pydantic, SQLAlchemy 2; versioned API under `/api/v1`.
- PostgreSQL 18: transactional catalog, users, orders, quotes, and CRM data.
- Alembic: versioned schema migrations.

## Domain boundaries
Catalog (makes, models, trims, specifications, images, availability); Pricing (versioned tariffs and immutable quote snapshots); Identity (customers, staff roles, hashed bearer sessions, favorites and comparisons); Orders and Logistics (orders, events, document metadata, and in-app customer notifications linked to public events); CRM (leads, contacts, interactions, assignments); Admin (permissions, dictionaries, audit); i18n (complete interface dictionaries and translated entity fields).

## Decisions
- Store money as Decimal with currency and exchange-rate source/date.
- Customs rates, customs calculation basis, and other legal/commercial tariffs have no defaults and carry an effective date. Incomplete tariffs prevent quoting.
- Each issued quote is persisted with its input, tariff version, full cost-component snapshots, and timestamp, so later tariff edits do not rewrite prior calculations. Customs rates are stored as fractions (0.15 means 15%). Incomplete tariffs may be saved as drafts but cannot be activated.
- PostgreSQL is required in production. SQLite is allowed only for isolated unit tests when a driver is available.
- Browser identity uses an opaque host-only cookie with server-side token digests and session-bound double-submit HMAC CSRF checks. Bearer authorization remains available to non-browser API clients. Cookies are `Secure` in production and `SameSite=Lax`, so the browser app/API must share a site or use same-origin proxying.
- Public APIs never expose private CRM notes. Administrative operations require authorization and audit. Customer emails remain unverified until a mail verification flow is configured.
- Customer notifications are generated from public order events and are owner-scoped; internal staff notes are never included in their response. External notification delivery remains disabled until an approved provider and verification flow are configured.
- Images use external/object-storage URLs and metadata, not large database blobs.
- Order documents use private filesystem storage only when an explicit storage path is configured. Files are served as authenticated attachments using opaque random keys; production must provide durable private object storage and malware scanning.
- CRM analytics use bounded UTC creation-date cohorts and indexed date filters. Conversion is the cohort's current lead status, and summed quote values are estimates rather than realized revenue.
- Payment, customs, courier, and notification providers sit behind adapters. No real payments or outbound messages are enabled by default.
