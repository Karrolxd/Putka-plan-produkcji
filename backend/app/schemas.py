from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StoreOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    address: str


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str
    unit_price: Decimal


class OrderItemIn(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    store_id: int
    delivery_date: date
    items: list[OrderItemIn] = Field(min_length=1)

    @field_validator("items")
    @classmethod
    def products_are_unique(cls, items: list[OrderItemIn]) -> list[OrderItemIn]:
        product_ids = [item.product_id for item in items]
        if len(product_ids) != len(set(product_ids)):
            raise ValueError("Każdy produkt może wystąpić w zamówieniu tylko raz.")
        return items


class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: int
    quantity: int
    unit_price: Decimal


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    store_id: int
    delivery_date: date
    items: list[OrderItemOut]


class PlanProduct(BaseModel):
    product_id: int
    name: str
    quantity: int


class PlanCategory(BaseModel):
    category: str
    total: int
    products: list[PlanProduct]


class ProductionPlan(BaseModel):
    date: date
    categories: list[PlanCategory]
