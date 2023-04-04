from fastapi import APIRouter, Depends
from starlette.requests import Request

from domain.commands import product_commands
from schemas.product import ProductSchema
from service_layer import messagebus
from service_layer.auth import oauth2_scheme, is_admin_or_super_admin
from service_layer.unit_of_work import SqlalchemyUnitOfWork
from views import product_views

router = APIRouter(prefix="/product", tags=["products"])


@router.post(
    "/create_product",
    dependencies=[Depends(oauth2_scheme), Depends(is_admin_or_super_admin)],
    status_code=201,
)
def create_product(product: ProductSchema):
    """
    create product
    """
    cmd = product_commands.CreateProduct(**product.dict())
    messagebus.handle(cmd, SqlalchemyUnitOfWork())
    return {"message": "Product created successfully"}


@router.get(
    "/get_product/{sku}",
    response_model=ProductSchema,
    dependencies=[Depends(oauth2_scheme)],
)
def get_product(sku: str, request: Request):
    """
    get product by sku
    """
    product = product_views.get_product(
        sku, user_email=request.state.user.email, uow=SqlalchemyUnitOfWork()
    )
    return product


@router.put(
    "/update_product/{sku}",
    dependencies=[Depends(oauth2_scheme), Depends(is_admin_or_super_admin)],
)
def update_product(sku: str, product: ProductSchema):
    """
    update product by sku
    """
    cmd = product_commands.UpdateProduct(sku, product)
    messagebus.handle(cmd, SqlalchemyUnitOfWork())
    return {"message": "Product updated successfully"}


# endpoint for delete product
@router.delete(
    "/delete_product/{sku}",
    dependencies=[Depends(oauth2_scheme), Depends(is_admin_or_super_admin)],
    status_code=204,
)
def delete_product(sku: str):
    """
    delete product by sku
    """
    cmd = product_commands.DeleteProduct(sku)
    messagebus.handle(cmd, SqlalchemyUnitOfWork())
    return {"message": "Product deleted successfully"}
