from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.producto import Producto

router = APIRouter(prefix="/inventario", tags=["Inventario"])


@router.get("/")
def obtener_inventario(db: Session = Depends(get_db)):
    productos = db.query(Producto).all()
    return productos
