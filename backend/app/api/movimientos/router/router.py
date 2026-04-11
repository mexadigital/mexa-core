from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.database import get_db
from app.models.movimiento import Movimiento
from app.models.producto import Producto
from app.schemas.movimiento import MovimientoCreate, MovimientoOut

router = APIRouter(prefix="/movimientos", tags=["Movimientos"])


@router.post("/", response_model=MovimientoOut)
def crear_movimiento(
    data: MovimientoCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    producto = (
        db.query(Producto)
        .filter(
            Producto.id == data.producto_id,
            Producto.organizacion_id == user["organizacion_id"]
        )
        .first()
    )

    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    if data.cantidad <= 0:
        raise HTTPException(status_code=400, detail="Cantidad inválida")

    if data.tipo == "salida":
        if producto.cantidad < data.cantidad:
            raise HTTPException(status_code=400, detail="Stock insuficiente")
        producto.cantidad -= data.cantidad

    elif data.tipo == "entrada":
        producto.cantidad += data.cantidad

    else:
        raise HTTPException(status_code=400, detail="Tipo inválido")

    movimiento = Movimiento(
        organizacion_id=user["organizacion_id"],
        producto_id=data.producto_id,
        tipo=data.tipo,
        cantidad=data.cantidad,
        usuario=user["sub"],
        recibe=data.recibe,
        empleado=data.empleado,
        nota=data.nota,
    )

    db.add(movimiento)
    db.commit()
    db.refresh(movimiento)

    return movimiento


@router.get("/", response_model=list[MovimientoOut])
def listar_movimientos(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    movimientos = (
        db.query(Movimiento)
        .filter(Movimiento.organizacion_id == user["organizacion_id"])
        .order_by(Movimiento.created_at.desc())
        .limit(200)
        .all()
    )

    return movimientos


@router.get("/producto/{producto_id}", response_model=list[MovimientoOut])
def listar_movimientos_por_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    producto = (
        db.query(Producto)
        .filter(
            Producto.id == producto_id,
            Producto.organizacion_id == user["organizacion_id"]
        )
        .first()
    )

    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    movimientos = (
        db.query(Movimiento)
        .filter(
            Movimiento.producto_id == producto_id,
            Movimiento.organizacion_id == user["organizacion_id"]
        )
        .order_by(Movimiento.created_at.desc())
        .all()
    )

    if not movimientos:
        raise HTTPException(status_code=404, detail="No hay movimientos para este producto")

    return movimientos
