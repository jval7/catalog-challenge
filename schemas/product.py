from pydantic import BaseModel


class ProductSchema(BaseModel):
    sku: str
    name: str
    price: float
    brand: str
    quantity: float

    class Config:
        orm_mode = True
