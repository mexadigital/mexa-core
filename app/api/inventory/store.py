from datetime import datetime
from typing import Dict, Tuple, List
from .schemas import (
    Product, ProductCreate,
    Warehouse, WarehouseCreate
)

class InventoryStore:
    def __init__(self):
        self._product_id = 0
        self._warehouse_id = 0

        self.products: Dict[int, Product] = {}
        self.warehouses: Dict[int, Warehouse] = {}

        # (warehouse_id, product_id) -> quantity
        self.stock: Dict[Tuple[int, int], int] = {}

    # -------- Products --------
    def create_product(self, data: ProductCreate) -> Product:
        if any(p.sku == data.sku for p in self.products.values()):
            raise ValueError("SKU already exists")

        self._product_id += 1
        product = Product(
            id=self._product_id,
            created_at=datetime.utcnow(),
            **data.model_dump()
        )
        self.products[product.id] = product
        return product

    def list_products(self) -> List[Product]:
        return list(self.products.values())

    # -------- Warehouses --------
    def create_warehouse(self, data: WarehouseCreate) -> Warehouse:
        if any(w.code == data.code for w in self.warehouses.values()):
            raise ValueError("Warehouse code already exists")

        self._warehouse_id += 1
        warehouse = Warehouse(
            id=self._warehouse_id,
            created_at=datetime.utcnow(),
            **data.model_dump()
        )
        self.warehouses[warehouse.id] = warehouse
        return warehouse

    def list_warehouses(self) -> List[Warehouse]:
        return list(self.warehouses.values())

    # -------- Stock --------
    def set_stock(self, warehouse_id: int, product_id: int, quantity: int) -> int:
        if warehouse_id not in self.warehouses:
            raise KeyError("Warehouse not found")
        if product_id not in self.products:
            raise KeyError("Product not found")

        self.stock[(warehouse_id, product_id)] = quantity
        return quantity

    def adjust_stock(self, warehouse_id: int, product_id: int, delta: int) -> int:
        if warehouse_id not in self.warehouses:
            raise KeyError("Warehouse not found")
        if product_id not in self.products:
            raise KeyError("Product not found")

        key = (warehouse_id, product_id)
        current = self.stock.get(key, 0)
        new_quantity = current + delta

        if new_quantity < 0:
            raise ValueError("Insufficient stock")

        self.stock[key] = new_quantity
        return new_quantity
