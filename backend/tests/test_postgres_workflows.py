"""Opt-in end-to-end API checks against a disposable, migrated PostgreSQL database.

Run only with QHI_TEST_DATABASE_URL pointing to a loopback database whose name
ends in `_test`. This deliberately refuses remote or ambiguously named targets.
"""

import os
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.engine import make_url


_TEST_DATABASE_URL = os.getenv("QHI_TEST_DATABASE_URL")
if _TEST_DATABASE_URL:
    _parsed_url = make_url(_TEST_DATABASE_URL)
    if _parsed_url.host not in {"127.0.0.1", "localhost", "::1"}:
        raise RuntimeError("QHI_TEST_DATABASE_URL must point to a loopback-only test database")
    if not (_parsed_url.database or "").endswith("_test"):
        raise RuntimeError("QHI_TEST_DATABASE_URL database name must end in _test")
    os.environ["DATABASE_URL"] = _TEST_DATABASE_URL
    os.environ.setdefault("APP_ENV", "development")
    os.environ.setdefault("ADMIN_API_KEY", "integration-test-admin-key-not-for-production-0001")


@pytest.mark.skipif(not _TEST_DATABASE_URL, reason="Set QHI_TEST_DATABASE_URL to a disposable loopback *_test database")
def test_postgres_backed_customer_catalog_quotes_orders_crm_and_admin():
    from fastapi.testclient import TestClient
    from sqlalchemy import select, update

    from app.core.passwords import hash_password
    from app.db.session import SessionLocal
    from app.main import app
    from app.core.rate_limit import SlidingWindowLimiter
    from app.models import Car, CarTranslation, Customer, PricingTariff

    assert SessionLocal is not None
    marker = uuid4().hex[:10]
    slug = f"integration-ev-{marker}"
    email = f"integration-{marker}@example.test"

    with SessionLocal() as db:
        current_database = db.scalar(text("SELECT current_database()"))
        revision = db.scalar(text("SELECT version_num FROM alembic_version"))
        assert current_database == make_url(_TEST_DATABASE_URL).database
        assert revision == "0010_shared_rate_limit_buckets"

        car = Car(
            slug=slug, brand="Integration", model="EV", trim="Test", year=2026,
            price_cny=Decimal("10000.00"), range_km=500, battery_kwh=Decimal("70.00"),
            power_kw=200, drivetrain="AWD", availability="available", published=True,
        )
        car.translations = [
            CarTranslation(locale="ru", title="Test vehicle", description="PostgreSQL check"),
            CarTranslation(locale="tg", title="Мошини санҷишӣ", description="Санҷиши PostgreSQL"),
            CarTranslation(locale="en", title="Integration vehicle", description="PostgreSQL check"),
        ]
        tariff = db.scalar(select(PricingTariff).where(PricingTariff.active.is_(True)))
        db.add(car)
        if tariff is None:
            db.add(PricingTariff(
                name=f"Integration test {marker}", currency="TJS", effective_on=date.today(),
                cny_to_tjs=Decimal("1.250000"), shipping_tjs=Decimal("500.00"),
                customs_rate=Decimal("0.100000"), customs_basis="vehicle_plus_shipping",
                additional_tjs=Decimal("100.00"), paperwork_tjs=Decimal("50.00"), active=True,
            ))
        db.flush()
        car_id = car.id
        db.commit()

    # Distinct limiter instances model separate application workers. The
    # PostgreSQL counter must enforce the same cap across both instances.
    limiter_key = f"integration-limit:{marker}"
    with SessionLocal() as db:
        SlidingWindowLimiter(max_requests=1, window_seconds=60).check(limiter_key, db)
    with SessionLocal() as db, pytest.raises(HTTPException) as limited:
        SlidingWindowLimiter(max_requests=1, window_seconds=60).check(limiter_key, db)
    assert getattr(limited.value, "status_code", None) == 429

    concurrent_key = f"integration-concurrent-limit:{marker}"

    def attempt_limited_request() -> bool:
        with SessionLocal() as db:
            try:
                SlidingWindowLimiter(max_requests=3, window_seconds=60).check(concurrent_key, db)
            except HTTPException as error:
                if error.status_code == 429:
                    return False
                raise
            return True

    with ThreadPoolExecutor(max_workers=8) as workers:
        accepted = list(workers.map(lambda _: attempt_limited_request(), range(8)))
    assert sum(accepted) == 3

    with TestClient(app) as client:
        registered = client.post("/api/v1/auth/register", json={
            "email": email,
            "password": "Integration-Password-1234!",
            "full_name": "Integration Customer",
            "preferred_locale": "tg",
        })
        assert registered.status_code == 201, registered.text
        csrf = registered.json()["csrf_token"]

        restored = client.get("/api/v1/auth/me")
        assert restored.status_code == 200
        assert restored.json()["email_normalized"] == email
        assert restored.headers.get("x-csrf-token") == csrf

        assert client.patch("/api/v1/auth/me", json={"full_name": "No CSRF"}).status_code == 403
        updated = client.patch("/api/v1/auth/me", json={"full_name": "Updated Customer"}, headers={"X-CSRF-Token": csrf})
        assert updated.status_code == 200, updated.text

        signed_out = client.post("/api/v1/auth/logout", headers={"X-CSRF-Token": csrf})
        assert signed_out.status_code == 204
        logged_in = client.post("/api/v1/auth/login", json={"email": email, "password": "Integration-Password-1234!"})
        assert logged_in.status_code == 200, logged_in.text
        csrf = logged_in.json()["csrf_token"]
        assert client.get("/api/v1/auth/me").status_code == 200

        catalog = client.get("/api/v1/cars", params={"locale": "tg", "q": "Integration", "min_price_cny": "9000", "min_range_km": "400"})
        assert catalog.status_code == 200, catalog.text
        assert any(item["id"] == car_id and item["localized_title"] == "Мошини санҷишӣ" for item in catalog.json())
        detail = client.get(f"/api/v1/cars/{slug}", params={"locale": "en"})
        assert detail.status_code == 200
        assert detail.json()["localized_title"] == "Integration vehicle"

        quote = client.post("/api/v1/quotes", json={"price_cny": "10000.00"}, headers={"X-CSRF-Token": csrf})
        assert quote.status_code == 200, quote.text
        quote_id = quote.json()["id"]
        result = quote.json()
        assert Decimal(result["total_tjs"]) == sum(Decimal(result[key]) for key in ("car_tjs", "shipping_tjs", "customs_tjs", "additional_tjs", "paperwork_tjs"))
        history = client.get("/api/v1/auth/me/quotes")
        assert history.status_code == 200 and any(row["id"] == quote_id for row in history.json())

        favorite = client.put(f"/api/v1/auth/me/favorites/{car_id}", headers={"X-CSRF-Token": csrf})
        assert favorite.status_code == 200, favorite.text
        comparison = client.put("/api/v1/auth/me/comparison", json={"car_ids": [car_id]}, headers={"X-CSRF-Token": csrf})
        assert comparison.status_code == 200, comparison.text

        order = client.post("/api/v1/auth/me/orders", json={"car_id": car_id, "customer_note": "Integration order"}, headers={"X-CSRF-Token": csrf})
        assert order.status_code == 201, order.text
        assert order.json()["status"] == "requested"
        assert len(client.get("/api/v1/auth/me/orders").json()) == 1

        lead = client.post("/api/v1/leads", json={
            "name": "Integration Lead", "email": f"lead-{marker}@example.test",
            "preferred_locale": "en", "message": "Integration enquiry",
        }, headers={"X-CSRF-Token": csrf})
        assert lead.status_code == 201, lead.text
        lead_id = lead.json()["id"]

        with SessionLocal() as db:
            db.execute(update(Customer).where(Customer.email_normalized == email).values(role="admin"))
            db.commit()

        headers = {"X-Admin-Token": os.environ["ADMIN_API_KEY"]}
        admin_catalog = client.get("/api/v1/admin/cars", headers=headers)
        assert admin_catalog.status_code == 200, admin_catalog.text
        admin_car = next(item for item in admin_catalog.json() if item["id"] == car_id)
        assert admin_car["published"] is True
        update_payload = {
            key: admin_car[key]
            for key in (
                "slug", "brand", "model", "trim", "year", "price_cny", "range_km",
                "battery_kwh", "power_kw", "drivetrain", "availability", "published",
            )
        }
        update_payload["image_urls"] = admin_car["images"]
        update_payload["translations"] = admin_car["translations"]
        updated_car = client.put(f"/api/v1/admin/cars/{car_id}", json=update_payload, headers=headers)
        assert updated_car.status_code == 200, updated_car.text
        assert updated_car.json()["published"] is True
        unpublished = client.patch(f"/api/v1/admin/cars/{car_id}/publication?published=false", headers=headers)
        assert unpublished.status_code == 200 and unpublished.json()["published"] is False
        republished = client.patch(f"/api/v1/admin/cars/{car_id}/publication?published=true", headers=headers)
        assert republished.status_code == 200 and republished.json()["published"] is True
        staff_leads = client.get("/api/v1/crm/leads")
        assert staff_leads.status_code == 200, staff_leads.text
        changed = client.patch(f"/api/v1/crm/leads/{lead_id}", json={"status": "contacted"}, headers={"X-CSRF-Token": csrf})
        assert changed.status_code == 200, changed.text
        interaction = client.post(f"/api/v1/crm/leads/{lead_id}/interactions", json={"kind": "note", "summary": "Integration follow-up"}, headers={"X-CSRF-Token": csrf})
        assert interaction.status_code == 201, interaction.text
        analytics = client.get("/api/v1/crm/analytics")
        assert analytics.status_code == 200, analytics.text

    with SessionLocal() as db:
        assert db.scalar(select(Customer.id).where(Customer.email_normalized == email)) is not None
