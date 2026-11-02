# Payment provider activation checklist

## Current state

Real payment processing is disabled. No checkout URL can be created, no real payment can be approved, and no card data is collected by the application. `DemoProviderDisabled` refuses all real financial operations. `TestPaymentSimulator` records only explicitly requested simulated outcomes and contacts no network. Its routes require both `QHI_TEST_PAYMENTS_ENABLED=true`, a non-production `APP_ENV`, and a connected PostgreSQL database whose name ends in `_test`. DEMO payments are rejected. Refund simulations require an admin role and create idempotent ledger events; no funds are transferred.

This is a TEST workflow, not a provider integration. The additive `0013_order_payment_ledger` migration links saved vehicle estimates to orders, snapshots the quoted amount/currency, and records simulated payment/refund events. Customer and staff API history is available; no Visa, Mastercard, PayPal, Stripe, regional gateway, signed webhook, or real checkout is configured.

## Required before real payments

1. Register the legal business and obtain its legal name, jurisdiction, registration/tax identifiers, and business address.
2. Open a business bank account in that entity's name and decide the settlement currencies and supported markets.
3. Have counsel approve merchant terms, refund/cancellation rules, privacy/cookie notices, and the customer checkout flow.
4. Choose a provider available to the business in its jurisdiction; complete its underwriting and obtain production credentials directly from that provider.
5. Add server-only secret storage, key rotation, TLS-only signed webhooks, signature timestamp/replay checks, provider event idempotency, immutable payment events, reconciliation, refund authorization, and operational alerts.
6. Add sandbox contract tests and accounting/reconciliation review before a separately approved production activation.

Never collect card number, CVV, or magnetic-stripe data in QHI AUTO forms. Use provider-hosted checkout or provider-approved tokenization. No PCI DSS compliance claim is made.
