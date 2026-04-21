from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.movimiento import Movimiento
from app.models.producto import Producto
from app.models.usuario import Usuario
from app.schemas.movimiento import MovimientoCreate, MovimientoOut
from app.api.auth import get_current_user

router = APIRouter(prefix="/movimientos", tags=["Movimientos"])


@router.post("/", response_model=MovimientoOut, status_code=status.HTTP_201_CREATED)
def crear_movimiento(
    data: MovimientoCreate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    producto = (
        db.query(Producto)
        .filter(
            Producto.id == data.producto_id,
            Producto.organizacion_id == user.organizacion_id,
        )
        .first()
    )

    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    if data.tipo not in ["entrada", "salida"]:
        raise HTTPException(status_code=400, detail="Tipo de movimiento inválido")

    if data.cantidad <= 0:
        raise HTTPException(status_code=400, detail="La cantidad debe ser mayor a cero")

    if data.tipo == "salida" and producto.cantidad < data.cantidad:
        raise HTTPException(status_code=400, detail="Stock insuficiente")

    if data.tipo == "entrada":
        producto.cantidad += data.cantidad
    else:
        producto.cantidad -= data.cantidad

    nuevo_movimiento = Movimiento(
        organizacion_id=user.organizacion_id,
        producto_id=data.producto_id,
        tipo=data.tipo,
        cantidad=data.cantidad,
        usuario=data.usuario,
        recibe=data.recibe,
        empleado=data.empleado,
        nota=data.nota,
    )

    db.add(nuevo_movimiento)
    db.commit()
    db.refresh(nuevo_movimiento)

    return nuevo_movimiento


@router.get("/", response_model=list[MovimientoOut])
def listar_movimientos(
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    movimientos = (
        db.query(Movimiento)
        .filter(Movimiento.organizacion_id == user.organizacion_id)
        .order_by(Movimiento.id.desc())
        .all()
    )

    return movimientos
