from fastapi import APIRouter

from resources import product, user

api_router = APIRouter()
api_router.include_router(product.router)
api_router.include_router(user.router)
