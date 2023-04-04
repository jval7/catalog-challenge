from sqlalchemy import (
    Table,
    Column,
    Integer,
    String,
    Enum,
    Float,
    DateTime,
    func,
    ForeignKey,
    event,
)
from sqlalchemy.orm import registry

from domain.models import Product, User, ProductSeen
from schemas.enums import Roles

mapper_registry = registry()
products = Table(
    "products",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("sku", String, nullable=False, unique=True),
    Column("name", String, nullable=False),
    Column("price", Float, nullable=False),
    Column("brand", String, nullable=False),
    Column("quantity", Float, nullable=False),
)

users = Table(
    "users",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("role", Enum(Roles), nullable=False, server_default=Roles.anonymous.name),
    Column("username", String, nullable=False),
    Column("password", String, nullable=False),
    Column("email", String, nullable=False, unique=True),
)

product_seen = Table(
    "product_seen",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("product_sku", ForeignKey("products.id"), nullable=False),
    Column("date", DateTime, nullable=False, server_default=func.now()),
    Column("user_email", ForeignKey("users.id"), nullable=False),
    Column("role", Enum(Roles), nullable=False, server_default=Roles.anonymous.name),
)


def start_mappers():
    """Configure the SQLAlchemy mappers"""
    mapper_registry.map_imperatively(
        Product,
        products,
    )
    mapper_registry.map_imperatively(
        User,
        users,
    )
    mapper_registry.map_imperatively(
        ProductSeen,
        product_seen,
    )


@event.listens_for(Product, "load")
def receive_load(product, _):
    product.events = []


@event.listens_for(User, "load")
def receive_load(user, _):
    user.events = []


@event.listens_for(ProductSeen, "load")
def receive_load(prod_seen, _):
    prod_seen.events = []
