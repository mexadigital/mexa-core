from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.producto import Producto
from app.models.movimiento import Movimiento
from app.schemas.movimiento import MovimientoCreate, MovimientoOut

router = APIRouter(prefix="/movimientos", tags=["Movimientos"])


@router.post("/", response_model=MovimientoOut)
def crear_movimiento(data: MovimientoCreate, db: Session = Depends(get_db)):
    producto = (
        db.query(Producto)
        .filter(
            Producto.id == data.producto_id,
            Producto.organizacion_id == data.organizacion_id
        )
        .first()
    )

    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado en esta organización")

    if data.cantidad <= 0:
        raise HTTPException(status_code=400, detail="Cantidad debe ser mayor a 0")

    if data.tipo == "salida":
        if producto.cantidad < data.cantidad:
            raise HTTPException(status_code=400, detail="Stock insuficiente")
        producto.cantidad -= data.cantidad
    elif data.tipo == "entrada":
        producto.cantidad += data.cantidad
    else:
        raise HTTPException(status_code=400, detail="Tipo inválido (usa 'entrada' o 'salida')")

    movimiento = Movimiento(**data.dict())
    db.add(movimiento)
    db.commit()
    db.refresh(movimiento)

    return movimiento


@router.get("/", response_model=list[MovimientoOut])
def listar_movimientos(db: Session = Depends(get_db)):
    return (
        db.query(Movimiento)
        .order_by(Movimiento.created_at.desc())
        .limit(200)
        .all()
    )
