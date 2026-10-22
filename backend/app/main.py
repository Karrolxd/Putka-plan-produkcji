import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.cutoff import WARSAW, is_before_cutoff
from app.db import Base, SessionLocal, engine, get_db
from app.models import Order, OrderItem, Product, Store
from app.schemas import OrderCreate, OrderOut, ProductOut, StoreOut
from app.seed import seed


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed(db)
    yield


app = FastAPI(title="Putka – plan produkcji", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/stores", response_model=list[StoreOut])
def list_stores(db: Session = Depends(get_db)):
    return db.scalars(select(Store).order_by(Store.name)).all()


@app.get("/products", response_model=list[ProductOut])
def list_products(db: Session = Depends(get_db)):
    stmt = (
        select(Product)
        .where(Product.active.is_(True))
        .order_by(Product.category, Product.name)
    )
    return db.scalars(stmt).all()


def get_now() -> datetime:
    """Aktualny czas – jako zależność, żeby testy mogły go podmienić."""
    return datetime.now(timezone.utc)


@app.post("/orders", status_code=201, response_model=OrderOut)
def create_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    now: datetime = Depends(get_now),
):
    if db.get(Store, payload.store_id) is None:
        raise HTTPException(422, f"Sklep o id {payload.store_id} nie istnieje.")

    if payload.delivery_date <= now.astimezone(WARSAW).date():
        raise HTTPException(422, "Data dostawy musi być najwcześniej jutro.")

    if not is_before_cutoff(payload.delivery_date, now):
        raise HTTPException(
            422,
            f"Zamówienia na {payload.delivery_date} przyjmujemy do 14:00 dnia poprzedniego.",
        )

    product_ids = [item.product_id for item in payload.items]
    products = {
        p.id: p for p in db.scalars(select(Product).where(Product.id.in_(product_ids)))
    }
    missing = [pid for pid in product_ids if pid not in products]
    if missing:
        raise HTTPException(422, f"Nie ma produktów o id: {missing}.")
    inactive = [p.name for p in products.values() if not p.active]
    if inactive:
        raise HTTPException(422, f"Produkty niedostępne: {', '.join(inactive)}.")

    order = Order(
        store_id=payload.store_id,
        delivery_date=payload.delivery_date,
        items=[
            OrderItem(
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=products[item.product_id].unit_price,
            )
            for item in payload.items
        ],
    )
    db.add(order)
    db.commit()
    return order
