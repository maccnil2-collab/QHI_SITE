import asyncio
import hashlib
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api import auth_routes
from app.core.auth import AuthContext, get_auth_context, require_staff
from app.core.config import Settings
from app.db import base, session as db_session
from app.main import app
from app.models import Car, Customer, VehicleOrder
from app.services.documents import DocumentValidationError, read_upload, resolve_document, store_document


def test_order_document_is_stored_under_random_key_with_checksum_and_safe_name(tmp_path):
    content = b"%PDF-1.7\nQHI test document"
    key, filename, checksum, size = store_document(tmp_path, 42, r"C:\fakepath\invoice.pdf", "application/pdf", content)

    assert filename == "invoice.pdf"
    assert key.startswith("42/") and key.endswith(".pdf")
    assert resolve_document(tmp_path, key).read_bytes() == content
    assert checksum == hashlib.sha256(content).hexdigest()
    assert size == len(content)


def test_document_storage_rejects_type_mismatch_and_traversal(tmp_path):
    with pytest.raises(DocumentValidationError):
        store_document(tmp_path, 42, "invoice.png", "image/png", b"%PDF-1.7")
    with pytest.raises(DocumentValidationError):
        resolve_document(tmp_path, "../private.pdf")
    with pytest.raises(DocumentValidationError):
        resolve_document(tmp_path, "42/../../private.pdf")
    with pytest.raises(DocumentValidationError):
        store_document(Path("uploads"), 42, "valid.pdf", "application/pdf", b"%PDF-1.7")


def test_upload_stream_enforces_size_and_rejects_empty_content():
    async def chunks(*values):
        for value in values:
            yield value

    assert asyncio.run(read_upload(chunks(b"a", b"b"), 2)) == b"ab"
    with pytest.raises(DocumentValidationError):
        asyncio.run(read_upload(chunks(b"ab", b"c"), 2))
    with pytest.raises(DocumentValidationError):
        asyncio.run(read_upload(chunks(), 2))


@pytest.fixture
def document_api(tmp_path, monkeypatch):
    engine = create_engine("sqlite+pysqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    base.Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    monkeypatch.setattr(db_session, "SessionLocal", session_factory)
    monkeypatch.setattr(auth_routes, "settings", Settings(database_url="sqlite+pysqlite://", cors_origins=[], admin_api_key=None, document_storage_path=tmp_path / "private"))

    with session_factory() as db:
        customer = Customer(email_normalized="owner@example.test", password_hash="not-used", full_name="Owner")
        other = Customer(email_normalized="other@example.test", password_hash="not-used", full_name="Other")
        staff = Customer(email_normalized="staff@example.test", password_hash="not-used", full_name="Staff", role="manager")
        car = Car(slug="doc-test-ev", brand="Test", model="EV", year=2026, price_cny=Decimal("10000"))
        db.add_all([customer, other, staff, car])
        db.flush()
        order = VehicleOrder(order_number="QHI-2026-DOC001", customer_id=customer.id, car_id=car.id, status="requested")
        other_order = VehicleOrder(order_number="QHI-2026-DOC002", customer_id=other.id, car_id=car.id, status="requested")
        db.add_all([order, other_order])
        db.commit()
        customer_context = AuthContext(customer=customer, session=SimpleNamespace(id=1))
        staff_context = AuthContext(customer=staff, session=SimpleNamespace(id=2))
        order_id, other_order_id = order.id, other_order.id

    monkeypatch.setitem(app.dependency_overrides, get_auth_context, lambda: customer_context)
    monkeypatch.setitem(app.dependency_overrides, require_staff, lambda: staff_context)
    with TestClient(app) as client:
        yield client, order_id, other_order_id, tmp_path / "private"
    app.dependency_overrides.pop(get_auth_context, None)
    app.dependency_overrides.pop(require_staff, None)
    engine.dispose()


def test_document_api_enforces_customer_visibility_and_staff_access(document_api):
    client, order_id, other_order_id, storage_path = document_api
    content = b"%PDF-1.7\nQHI order document"
    first = client.post(
        f"/api/v1/auth/staff/orders/{order_id}/documents?visible_to_customer=true",
        content=content,
        headers={"X-File-Name": "delivery%20paper.pdf", "Content-Type": "application/pdf"},
    )
    private = client.post(
        f"/api/v1/auth/staff/orders/{order_id}/documents",
        content=content,
        headers={"X-File-Name": "staff-only.pdf", "Content-Type": "application/pdf"},
    )

    assert first.status_code == 201
    assert first.json()["filename"] == "delivery paper.pdf"
    assert private.status_code == 201
    assert private.json()["visible_to_customer"] is False
    assert len(list(storage_path.rglob("*.pdf"))) == 2

    visible = client.get(f"/api/v1/auth/me/orders/{order_id}/documents")
    assert visible.status_code == 200
    assert [item["id"] for item in visible.json()] == [first.json()["id"]]
    download = client.get(f"/api/v1/auth/me/orders/{order_id}/documents/{first.json()['id']}")
    assert download.status_code == 200
    assert download.content == content
    assert download.headers["content-disposition"].startswith("attachment;")
    assert client.get(f"/api/v1/auth/me/orders/{order_id}/documents/{private.json()['id']}").status_code == 404
    assert client.get(f"/api/v1/auth/me/orders/{other_order_id}/documents").status_code == 404

    staff_list = client.get(f"/api/v1/auth/staff/orders/{order_id}/documents")
    assert staff_list.status_code == 200
    assert len(staff_list.json()) == 2
    staff_download = client.get(f"/api/v1/auth/staff/orders/{order_id}/documents/{private.json()['id']}")
    assert staff_download.status_code == 200
    assert staff_download.content == content
