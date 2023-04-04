from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from domain import events
from domain.commands import product_commands
from domain.models import Product
from logger import logger
from schemas.product import ProductSchema
from service_layer.unit_of_work import AbstractUnitOfWork


class ProductHandler:
    @staticmethod
    def create_product(
        cmd: product_commands.CreateProduct, uow: AbstractUnitOfWork
    ) -> ProductSchema:
        """Create a new product"""
        with uow:
            logger.info(f"Creating product with sku: {cmd.sku}")
            product = Product(
                sku=cmd.sku,
                name=cmd.name,
                price=cmd.price,
                quantity=cmd.quantity,
                brand=cmd.brand,
            )
            try:
                uow.repository.add(product)
            except IntegrityError:
                logger.error(f"Product with sku: {product.sku} already exists")
                raise HTTPException(status_code=400, detail="Product already exists")
            product.events.append(
                events.ProductCreated(
                    sku=cmd.sku,
                    name=cmd.name,
                    price=cmd.price,
                    quantity=cmd.quantity,
                    brand=cmd.brand,
                )
            )
            return ProductSchema.from_orm(product)

    @staticmethod
    def update_product(cmd: product_commands.UpdateProduct, uow: AbstractUnitOfWork):
        """Update a product"""
        with uow:
            logger.info(f"Updating product with sku: {cmd.sku}")
            try:
                product = uow.repository.get(Product, dict_to_filter={"sku": cmd.sku})
                product.events.append(
                    events.ProductModified(
                        sku=cmd.product.sku,
                        name=None
                        if cmd.product.name == product.name
                        else cmd.product.name,
                        price=None
                        if cmd.product.price == product.price
                        else cmd.product.price,
                        quantity=None
                        if cmd.product.quantity == product.quantity
                        else cmd.product.quantity,
                        brand=None
                        if cmd.product.brand == product.brand
                        else cmd.product.brand,
                    )
                )
                ProductHandler._update_product_inplace(product, cmd.product)
                uow.commit()
            except IntegrityError:
                logger.error(f"The parameters are not valid, remember sku is unique")
                raise HTTPException(
                    status_code=400,
                    detail="The parameters are not valid, remember sku is unique",
                )

    @staticmethod
    def _update_product_inplace(product: Product, product_updated: ProductSchema):
        product.name = product_updated.name
        product.price = product_updated.price
        product.quantity = product_updated.quantity
        product.brand = product_updated.brand

    @staticmethod
    def delete_product(cmd: product_commands.DeleteProduct, uow: AbstractUnitOfWork):
        """Delete a product"""
        with uow:
            logger.info(f"Deleting product with sku: {cmd.sku}")
            product = uow.repository.get(Product, dict_to_filter={"sku": cmd.sku})
            deleted_product_number = uow.repository.delete(Product, "sku", cmd.sku)
            if deleted_product_number == 0:
                logger.error("Product not found")
                raise HTTPException(status_code=404, detail="Product not found")
            product.events.append(events.ProductDeleted(sku=cmd.sku))
