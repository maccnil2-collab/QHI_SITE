"""Provider-neutral payment contracts. Real charging is deliberately disabled."""
from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol


@dataclass(frozen=True)
class PaymentSession:
    provider_reference: str
    redirect_url: str
    status: str


class PaymentProvider(Protocol):
    name: str
    def create_session(self, *, order_reference: str, amount: Decimal, currency: str, idempotency_key: str) -> PaymentSession: ...
    def verify_webhook(self, *, payload: bytes, signature: str) -> bool: ...
    def request_refund(self, *, provider_reference: str, amount: Decimal, idempotency_key: str) -> str: ...


class DemoProviderDisabled:
    """Safe placeholder: it never opens checkout or reports success."""
    name = "demo"
    def create_session(self, *, order_reference: str, amount: Decimal, currency: str, idempotency_key: str) -> PaymentSession:
        raise RuntimeError("Payment processing is disabled; no transaction was created")
    def verify_webhook(self, *, payload: bytes, signature: str) -> bool:
        return False
    def request_refund(self, *, provider_reference: str, amount: Decimal, idempotency_key: str) -> str:
        raise RuntimeError("Refund processing is disabled; no transaction was created")
