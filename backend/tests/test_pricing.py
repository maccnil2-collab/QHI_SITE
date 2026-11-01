from datetime import date
from decimal import Decimal

import pytest

from app.services.pricing import Tariff, calculate_quote


def test_quote_calculates_each_cost_component_and_total():
    tariff = Tariff("test fixture", date(2026, 1, 1), Decimal("1.50"), Decimal("120"), Decimal("0.10"), "vehicle_value", Decimal("30"), Decimal("20"))
    result = calculate_quote(Decimal("10000"), tariff)
    assert result["car_tjs"] == Decimal("15000.00")
    assert result["customs_tjs"] == Decimal("1500.00")
    assert result["total_tjs"] == Decimal("16670.00")


def test_quote_refuses_unconfigured_rates_instead_of_guessing():
    tariff = Tariff("unconfigured", date(2026, 1, 1), None, None, None, None, None, None)
    with pytest.raises(ValueError, match="Tariff is incomplete"):
        calculate_quote(Decimal("10000"), tariff)


def test_quote_rejects_zero_car_price():
    tariff = Tariff("fixture", date(2026, 1, 1), Decimal("1"), Decimal("0"), Decimal("0"), "vehicle_value", Decimal("0"), Decimal("0"))
    with pytest.raises(ValueError, match="outside allowed limits"):
        calculate_quote(Decimal("0"), tariff)


def test_customs_basis_can_include_shipping_when_configured():
    tariff = Tariff("test fixture", date(2026, 1, 1), Decimal("1.50"), Decimal("120"), Decimal("0.10"), "vehicle_plus_shipping", Decimal("30"), Decimal("20"))
    result = calculate_quote(Decimal("10000"), tariff)
    assert result["customs_tjs"] == Decimal("1512.00")
    assert result["total_tjs"] == Decimal("16682.00")
