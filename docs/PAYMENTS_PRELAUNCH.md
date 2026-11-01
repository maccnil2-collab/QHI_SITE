# Payment provider activation checklist

## Current state

Payment processing is disabled. No checkout URL can be created, no payment can be approved, and no card data is collected by the application. `app.services.payment_providers` defines the provider-neutral create-session, webhook-verification, and refund interface; `DemoProviderDisabled` refuses all financial operations. The payment-attempt schema and idempotency constraint are present in the current local databases after migration `0011_demo_inventory_support_payments`; this is only storage groundwork and does not enable a payment flow.

This is an integration boundary, not a completed provider integration. There is no Visa, Mastercard, PayPal, Stripe, regional gateway, webhook endpoint, payment history screen, or refund workflow enabled.

## Required before real payments

1. Register the legal business and obtain its legal name, jurisdiction, registration/tax identifiers, and business address.
2. Open a business bank account in that entity's name and decide the settlement currencies and supported markets.
3. Have counsel approve merchant terms, refund/cancellation rules, privacy/cookie notices, and the customer checkout flow.
4. Choose a provider available to the business in its jurisdiction; complete its underwriting and obtain production credentials directly from that provider.
5. Add server-only secret storage, key rotation, TLS-only signed webhooks, signature timestamp/replay checks, provider event idempotency, immutable payment events, reconciliation, refund authorization, and operational alerts.
6. Add sandbox contract tests and accounting/reconciliation review before a separately approved production activation.

Never collect card number, CVV, or magnetic-stripe data in QHI AUTO forms. Use provider-hosted checkout or provider-approved tokenization. No PCI DSS compliance claim is made.
