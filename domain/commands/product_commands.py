from dataclasses import dataclass

from domain.commands import Command
from schemas.product import ProductSchema


@dataclass
class CreateProduct(Command):
    sku: str
    name: str
    price: float
    brand: str
    quantity: float


@dataclass
class UpdateProduct(Command):
    sku: str
    product: ProductSchema


@dataclass
class DeleteProduct(Command):
    sku: str
