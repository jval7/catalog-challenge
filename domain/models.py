from datetime import datetime
from typing import List

from schemas.enums import Roles


class Product:
    __tablename__ = "products"

    def __init__(self, sku: str, name: str, price: float, brand: str, quantity: float):
        self.sku: str = sku
        self.name: str = name
        self.price: float = price
        self.brand: str = brand
        self.quantity: float = quantity
        self.events = []  # type: List[events.Event]


class User:
    __tablename__ = "users"

    def __init__(
        self, email: str, username: str = None, password: str = None, role: Roles = None
    ):
        self.email: str = email
        self.username: str = username
        self.password: str = password
        self.role: Roles = role
        self.events = []  # type: List[events.Event]


class ProductSeen:
    __tablename__ = "product_seen"

    def __init__(self, product_sku: str, user_email: str, role: Roles):
        self.product_sku: str = product_sku
        self.user_email: str = user_email
        self.role: Roles = role
        self.date: datetime = datetime.now()
        self.events = []  # type: List[events.Event]
