from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime


class ProductCreate(BaseModel):
    sku: str
    name: str
    unit: str = "pz"
    description: Optional[str] = None


class Product(ProductCreate):
    id: int
    created_at: datetime


class WarehouseCreate(BaseModel):
    code: str
    name: str


class Warehouse(WarehouseCreate):
    id: int
    created_at: datetime


class StockSet(BaseModel):
    warehouse_id: int
    product_id: int
    quantity: int


class StockAdjust(BaseModel):
    warehouse_id: int
    product_id: int
    delta: int


class StockMove(BaseModel):
    from_warehouse_id: int
    to_warehouse_id: int
    product_id: int
    quantity: int


class StockSnapshot(BaseModel):
    warehouse_id: int
    product_id: int
    quantity: int


class InventorySummary(BaseModel):
    product_id: int
    total: int
    by_warehouse: Dict[int, int]

