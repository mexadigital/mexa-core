from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.database import SessionLocal
from app.models.producto import Producto
from app.schemas.producto import ProductoCreate, ProductoOut


router = APIRouter(
    prefix="/productos",
    tags=["Productos"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=ProductoOut)
def crear_producto(producto: ProductoCreate, db: Session = Depends(get_db)):
    nuevo_producto = Producto(**producto.model_dump())
    db.add(nuevo_producto)
    db.commit()
    db.refresh(nuevo_producto)
    return nuevo_producto


@router.get("/", response_model=List[ProductoOut])
def listar_productos(db: Session = Depends(get_db)):
    return db.query(Producto).all()
