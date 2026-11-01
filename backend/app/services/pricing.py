from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP


CENT = Decimal("0.01")


def money(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class Tariff:
    name: str
    effective_on: date
    cny_to_tjs: Decimal | None
    shipping_tjs: Decimal | None
    customs_rate: Decimal | None
    customs_basis: str | None
    additional_tjs: Decimal | None
    paperwork_tjs: Decimal | None

    def missing(self) -> list[str]:
        return [field for field in ("cny_to_tjs", "shipping_tjs", "customs_rate", "customs_basis", "additional_tjs", "paperwork_tjs") if getattr(self, field) is None]


def calculate_quote(price_cny: Decimal, tariff: Tariff) -> dict[str, Decimal | date | str]:
    missing = tariff.missing()
    if missing:
        raise ValueError(f"Tariff is incomplete: {', '.join(missing)}")
    if price_cny <= 0 or tariff.cny_to_tjs <= 0 or tariff.customs_rate < 0:
        raise ValueError("Price, exchange rate, and customs rate are outside allowed limits")
    car = money(price_cny * tariff.cny_to_tjs)
    shipping = money(tariff.shipping_tjs)
    if tariff.customs_basis not in {"vehicle_value", "vehicle_plus_shipping"}:
        raise ValueError("Customs basis is not supported")
    customs_base = car if tariff.customs_basis == "vehicle_value" else car + shipping
    customs = money(customs_base * tariff.customs_rate)
    additional = money(tariff.additional_tjs)
    paperwork = money(tariff.paperwork_tjs)
    return {
        "car_tjs": car,
        "shipping_tjs": shipping,
        "customs_tjs": customs,
        "customs_basis": tariff.customs_basis,
        "additional_tjs": additional,
        "paperwork_tjs": paperwork,
        "total_tjs": money(car + shipping + customs + additional + paperwork),
        "effective_on": tariff.effective_on,
        "tariff_name": tariff.name,
    }
