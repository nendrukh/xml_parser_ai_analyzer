from pydantic import BaseModel


class Product(BaseModel):
    id: int
    name: str
    quantity: int
    price: float
    category: str
