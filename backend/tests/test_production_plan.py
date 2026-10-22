from datetime import date

from sqlalchemy import select

from app.models import Order, OrderItem, Product, Store

DAY = date(2027, 1, 15)


def product(db, name: str) -> Product:
    return db.scalar(select(Product).where(Product.name == name))


def add_order(db, store: str, delivery_date: date, items: dict[str, int]) -> None:
    """Zapisuje zamówienie bezpośrednio w bazie – bez cutoffu i zegara z POST /orders."""
    order = Order(
        store_id=db.scalar(select(Store.id).where(Store.name == store)),
        delivery_date=delivery_date,
    )
    for name, quantity in items.items():
        p = product(db, name)
        order.items.append(
            OrderItem(product_id=p.id, quantity=quantity, unit_price=p.unit_price)
        )
    db.add(order)
    db.commit()


def get_plan(client, day: date = DAY) -> dict:
    response = client.get("/production-plan", params={"date": day.isoformat()})
    assert response.status_code == 200
    return response.json()


def quantities(plan: dict) -> dict[str, int]:
    return {p["name"]: p["quantity"] for c in plan["categories"] for p in c["products"]}


def totals(plan: dict) -> dict[str, int]:
    return {c["category"]: c["total"] for c in plan["categories"]}


def test_day_without_orders_lists_all_active_products_with_zero(db, client):
    plan = get_plan(client)

    assert plan["date"] == "2027-01-15"
    assert totals(plan) == {"Bułki": 0, "Cukiernia": 0, "Pieczywo": 0}
    assert len(quantities(plan)) == 13
    assert set(quantities(plan).values()) == {0}


def test_quantities_are_summed_across_orders(db, client):
    add_order(db, "Putka Mokotów", DAY, {"Kajzerka": 50, "Bagietka": 10})
    add_order(db, "Putka Wola", DAY, {"Kajzerka": 30})
    add_order(db, "Putka Mokotów", DAY, {"Kajzerka": 20})  # drugie zamówienie tego sklepu

    plan = get_plan(client)

    assert quantities(plan)["Kajzerka"] == 100
    assert quantities(plan)["Bagietka"] == 10
    assert quantities(plan)["Grahamka"] == 0
    assert totals(plan) == {"Bułki": 110, "Cukiernia": 0, "Pieczywo": 0}


def test_orders_for_other_days_are_not_counted(db, client):
    add_order(db, "Putka Mokotów", DAY, {"Kajzerka": 50})
    add_order(db, "Putka Mokotów", date(2027, 1, 16), {"Kajzerka": 999, "Croissant": 5})

    plan = get_plan(client)

    assert quantities(plan)["Kajzerka"] == 50
    assert quantities(plan)["Croissant"] == 0


def test_inactive_product_is_listed_only_when_ordered(db, client):
    add_order(db, "Putka Mokotów", DAY, {"Bułka maślana": 12})
    product(db, "Bułka maślana").active = False
    db.commit()

    plan = get_plan(client)

    assert quantities(plan)["Bułka maślana"] == 12
    assert "Rogal z makiem" not in quantities(plan)  # nieaktywny, bez zamówień
