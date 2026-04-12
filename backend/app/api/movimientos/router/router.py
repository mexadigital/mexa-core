from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.db.database import get_db
from app.models.movimiento import Movimiento
from app.models.producto import Producto
from app.schemas.movimiento import MovimientoCreate, MovimientoOut

router = APIRouter(prefix="/movimientos", tags=["Movimientos"])


@router.post("/", response_model=MovimientoOut)
def crear_movimiento(
    payload: MovimientoCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    producto = (
        db.query(Producto)
        .filter(
            Producto.id == payload.producto_id,
            Producto.organizacion_id == user["organizacion_id"],
        )
        .first()
    )

    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    if payload.tipo not in ["entrada", "salida"]:
        raise HTTPException(status_code=400, detail="Tipo de movimiento inválido")

    if payload.cantidad <= 0:
        raise HTTPException(status_code=400, detail="Cantidad inválida")

    if payload.tipo == "entrada":
        producto.cantidad += payload.cantidad
    else:
        if producto.cantidad < payload.cantidad:
            raise HTTPException(status_code=400, detail="Stock insuficiente")
        producto.cantidad -= payload.cantidad

    movimiento = Movimiento(
        organizacion_id=user["organizacion_id"],
        producto_id=payload.producto_id,
        tipo=payload.tipo,
        cantidad=payload.cantidad,
        usuario=payload.usuario,
        recibe=payload.recibe,
        empleado=payload.empleado,
        nota=payload.nota,
    )

    db.add(movimiento)
    db.commit()
    db.refresh(movimiento)

    return movimiento


@router.get("/", response_model=list[MovimientoOut])
def listar_movimientos(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    movimientos = (
        db.query(Movimiento)
        .filter(Movimiento.organizacion_id == user["organizacion_id"])
        .order_by(Movimiento.id.desc())
        .all()
    )
    return movimientos


@router.get("/{movimiento_id}", response_model=MovimientoOut)
def obtener_movimiento(
    movimiento_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    movimiento = (
        db.query(Movimiento)
        .filter(
            Movimiento.id == movimiento_id,
            Movimiento.organizacion_id == user["organizacion_id"],
        )
        .first()
    )

    if not movimiento:
        raise HTTPException(status_code=404, detail="Movimiento no encontrado")

    return movimiento
