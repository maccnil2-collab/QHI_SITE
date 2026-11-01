# QHI AUTO Architecture

## Services
- `frontend/`: Next.js App Router, React, TypeScript, Tailwind CSS; locale routes `/ru`, `/tg`, `/en`.
- `backend/`: FastAPI, Pydantic, SQLAlchemy 2; versioned API under `/api/v1`.
- PostgreSQL 18: transactional catalog, users, orders, quotes, and CRM data.
- Alembic: versioned schema migrations.

## Domain boundaries
Catalog (makes, models, trims, specifications, images, availability); Pricing (versioned tariffs and immutable quote snapshots); Identity (customers, staff roles, sessions); Orders and Logistics (orders, events, documents, notifications); CRM (leads, contacts, interactions, assignments); Admin (permissions, dictionaries, audit); i18n (complete interface dictionaries and translated entity fields).

## Decisions
- Store money as Decimal with currency and exchange-rate source/date.
- Customs rates, customs calculation basis, and other legal/commercial tariffs have no defaults and carry an effective date. Incomplete tariffs prevent quoting.
- A quote stores its input, tariff version, and date so future tariff edits do not rewrite a prior quote.
- PostgreSQL is required in production. SQLite is allowed only for isolated unit tests when a driver is available.
- Public APIs never expose private CRM notes. Administrative operations require authorization and audit.
- Images use external/object-storage URLs and metadata, not large database blobs.
- Payment, customs, courier, and notification providers sit behind adapters. No real payments or outbound messages are enabled by default.