from fastapi import APIRouter, HTTPException
from typing import List
from .schemas import (
    ProductCreate, Product,
    WarehouseCreate, Warehouse,
    StockSet, StockAdjust, StockSnapshot
)
from .store import InventoryStore

router = APIRouter(prefix="/inventory", tags=["inventory"])
store = InventoryStore()

# -------- Products --------
@router.post("/products", response_model=Product)
def create_product(payload: ProductCreate):
    try:
        return store.create_product(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/products", response_model=List[Product])
def list_products():
    return store.list_products()

# -------- Warehouses --------
@router.post("/warehouses", response_model=Warehouse)
def create_warehouse(payload: WarehouseCreate):
    try:
        return store.create_warehouse(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/warehouses", response_model=List[Warehouse])
def list_warehouses():
    return store.list_warehouses()

# -------- Stock --------
@router.post("/stock/set", response_model=StockSnapshot)
def set_stock(payload: StockSet):
    try:
        qty = store.set_stock(
            payload.warehouse_id,
            payload.product_id,
            payload.quantity
        )
        return {
            "warehouse_id": payload.warehouse_id,
            "product_id": payload.product_id,
            "quantity": qty
        }
    except (KeyError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/stock/adjust", response_model=StockSnapshot)
def adjust_stock(payload: StockAdjust):
    try:
        qty = store.adjust_stock(
            payload.warehouse_id,
            payload.product_id,
            payload.delta
        )
        return {
            "warehouse_id": payload.warehouse_id,
            "product_id": payload.product_id,
            "quantity": qty
        }
    except (KeyError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))
