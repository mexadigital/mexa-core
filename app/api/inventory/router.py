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

# -------- Demo helpers (RESET / SEED) --------
@router.post("/demo/reset")
def demo_reset():
    """
    Reinicia el inventario en memoria (borra productos/almacenes/stock).
    Útil cuando te hiciste bolas o quieres empezar limpio.
    """
    global store
    store = InventoryStore()
    return {"ok": True, "message": "Inventory reset (in-memory)."}


@router.post("/demo/seed")
def demo_seed():
    """
    Crea un escenario de prueba en 1 clic:
    - Almacén Central (ALM-01)
    - Producto Varilla 7018 (SKU-001)
    - Stock = 100
    """
    # 1) Crear almacén (si no existe)
    try:
        w = store.create_warehouse(WarehouseCreate(code="ALM-01", name="Almacén Central"))
    except ValueError:
        # Ya existe con ese code: lo buscamos en la lista
        w = next((x for x in store.list_warehouses() if x.code == "ALM-01"), None)
        if w is None:
            raise HTTPException(status_code=500, detail="Warehouse exists but could not be retrieved")

    # 2) Crear producto (si no existe)
    try:
        p = store.create_product(ProductCreate(
            sku="SKU-001",
            name="Varilla 7018",
            unit="pz",
            description="Electrodo 7018"
        ))
    except ValueError:
        # Ya existe con ese sku: lo buscamos en la lista
        p = next((x for x in store.list_products() if x.sku == "SKU-001"), None)
        if p is None:
            raise HTTPException(status_code=500, detail="Product exists but could not be retrieved")

    # 3) Set stock
    store.set_stock(w.id, p.id, 100)

    return {
        "ok": True,
        "warehouse": {"id": w.id, "code": w.code, "name": w.name},
        "product": {"id": p.id, "sku": p.sku, "name": p.name},
        "stock": {"warehouse_id": w.id, "product_id": p.id, "quantity": 100}
    }
