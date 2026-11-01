# QHI AUTO Architecture

## Services
- `frontend/`: Next.js App Router, React, TypeScript, Tailwind CSS; locale routes `/ru`, `/tg`, `/en`.
- `backend/`: FastAPI, Pydantic, SQLAlchemy 2; versioned API under `/api/v1`.
- PostgreSQL 18: transactional catalog, users, orders, quotes, and CRM data.
- Alembic: versioned schema migrations.

## Domain boundaries
Catalog (makes, models, trims, specifications, images, availability); Pricing (versioned tariffs and immutable quote snapshots); Identity (customers, staff roles, hashed bearer sessions, favorites and comparisons); Orders and Logistics (orders, events, documents, notifications); CRM (leads, contacts, interactions, assignments); Admin (permissions, dictionaries, audit); i18n (complete interface dictionaries and translated entity fields).

## Decisions
- Store money as Decimal with currency and exchange-rate source/date.
- Customs rates, customs calculation basis, and other legal/commercial tariffs have no defaults and carry an effective date. Incomplete tariffs prevent quoting.
- Each issued quote is persisted with its input, tariff version, full cost-component snapshots, and timestamp, so later tariff edits do not rewrite prior calculations. Customs rates are stored as fractions (0.15 means 15%). Incomplete tariffs may be saved as drafts but cannot be activated.
- PostgreSQL is required in production. SQLite is allowed only for isolated unit tests when a driver is available.
- Public APIs never expose private CRM notes. Administrative operations require authorization and audit. Customer emails remain unverified until a mail verification flow is configured.
- Images use external/object-storage URLs and metadata, not large database blobs.
- Payment, customs, courier, and notification providers sit behind adapters. No real payments or outbound messages are enabled by default.