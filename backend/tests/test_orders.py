from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy import func, select

from app.main import app, get_now
from app.models import Order, Product, Store

WAW = ZoneInfo("Europe/Warsaw")


@pytest.fixture
def set_now():
    """Ustawia „teraz” widziane przez endpoint. Domyślnie 14.01.2027 10:00 w Warszawie."""

    def _set(now: datetime) -> None:
        app.dependency_overrides[get_now] = lambda: now

    _set(datetime(2027, 1, 14, 10, 0, tzinfo=WAW))
    yield _set
    app.dependency_overrides.clear()


def product(db, name: str) -> Product:
    return db.scalar(select(Product).where(Product.name == name))


def order_payload(db, delivery_date: str = "2027-01-15", products=("Kajzerka",)) -> dict:
    return {
        "store_id": db.scalar(select(Store.id).where(Store.name == "Putka Mokotów")),
        "delivery_date": delivery_date,
        "items": [{"product_id": product(db, name).id, "quantity": 10} for name in products],
    }


def test_valid_order_is_created_with_current_prices(db, client, set_now):
    response = client.post("/orders", json=order_payload(db, products=("Kajzerka", "Bagietka")))

    assert response.status_code == 201
    prices = {item["product_id"]: item["unit_price"] for item in response.json()["items"]}
    assert prices == {product(db, "Kajzerka").id: "0.90", product(db, "Bagietka").id: "4.50"}


def test_order_for_today_is_rejected(db, client, set_now):
    response = client.post("/orders", json=order_payload(db, delivery_date="2027-01-14"))

    assert response.status_code == 422
    assert "najwcześniej jutro" in response.json()["detail"]


def test_order_after_cutoff_is_rejected(db, client, set_now):
    set_now(datetime(2027, 1, 14, 14, 0, tzinfo=WAW))

    response = client.post("/orders", json=order_payload(db))

    assert response.status_code == 422
    assert "14:00" in response.json()["detail"]


def test_order_with_inactive_product_is_rejected_and_nothing_is_saved(db, client, set_now):
    payload = order_payload(db, products=("Kajzerka", "Chleb razowy"))

    response = client.post("/orders", json=payload)

    assert response.status_code == 422
    assert "Chleb razowy" in response.json()["detail"]
    assert db.scalar(select(func.count()).select_from(Order)) == 0


def test_store_can_place_second_order_for_same_day(db, client, set_now):
    assert client.post("/orders", json=order_payload(db)).status_code == 201

    response = client.post("/orders", json=order_payload(db, products=("Bagietka",)))

    assert response.status_code == 201
    assert db.scalar(select(func.count()).select_from(Order)) == 2
