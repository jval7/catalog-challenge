from fastapi import HTTPException
from sqlalchemy import text

from domain import events
from logger import logger
from schemas.product import ProductSchema
from service_layer import messagebus
from service_layer.unit_of_work import AbstractUnitOfWork


def get_product(
    sku: str,
    uow: AbstractUnitOfWork,
    message_bus=None,
    user_email=None,
) -> ProductSchema:
    """Get product by id"""
    logger.info(f"Getting product with sku: {sku}")
    with uow:
        try:
            product = next(
                uow.session.execute(
                    text("SELECT * FROM products WHERE sku = :sku"), {"sku": sku}
                )
            )
        except StopIteration:
            logger.error(f"Product with sku: {sku} not found")
            raise HTTPException(status_code=404, detail="Product not found")
    event = events.ProductViewed(sku=sku, user_email=user_email)
    message_bus = message_bus or messagebus
    message_bus.handle(event, uow)
    return ProductSchema.from_orm(product)
