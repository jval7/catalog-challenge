from typing import Optional

from pydantic import BaseModel


class Event:
    ...


class ProductModified(Event, BaseModel):
    sku: str = None
    name: str = None
    price: float = None
    brand: str = None
    quantity: float = None


class ProductViewed(Event, BaseModel):
    sku: str
    user_email: Optional[str]


class ProductCreated(Event, BaseModel):
    sku: str
    name: str
    price: float
    brand: str
    quantity: float


class ProductDeleted(Event, BaseModel):
    sku: str
