from pydantic import BaseModel


class EPP(BaseModel):
    id: int
    name: str
    description: str
    price: float


class Consumable(BaseModel):
    id: int
    name: str
    quantity: int
    price_per_unit: float
    total_price: float
