from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.movimiento import Movimiento
from app.models.producto import Producto
from app.models.usuario import Usuario
from app.schemas.movimiento import MovimientoCreate
from app.api.auth import get_current_user

router = APIRouter(prefix="/movimientos", tags=["Movimientos"])


# 🔹 CREAR MOVIMIENTO
@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_movimiento(
    data: MovimientoCreate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    producto = (
        db.query(Producto)
        .filter(
            Producto.id == data.producto_id,
            Producto.organizacion_id == user.organizacion_id
        )
        .first()
    )

    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    if data.tipo not in ["entrada", "salida"]:
        raise HTTPException(status_code=400, detail="Tipo inválido")

    if data.cantidad <= 0:
        raise HTTPException(status_code=400, detail="Cantidad debe ser mayor a 0")

    if data.tipo == "salida" and producto.cantidad < data.cantidad:
        raise HTTPException(status_code=400, detail="Stock insuficiente")

    # 🔹 Ajuste de stock
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


# 🔹 LISTAR MOVIMIENTOS (CON NOMBRE DE PRODUCTO)
@router.get("/")
def listar_movimientos(
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    movimientos = (
        db.query(Movimiento, Producto)
        .join(Producto, Movimiento.producto_id == Producto.id)
        .filter(Movimiento.organizacion_id == user.organizacion_id)
        .order_by(Movimiento.id.desc())
        .all()
    )

    resultado = []

    for mov, prod in movimientos:
        resultado.append({
            "id": mov.id,
            "producto": prod.nombre,
            "tipo": mov.tipo,
            "cantidad": mov.cantidad,
            "usuario": mov.usuario,
            "recibe": mov.recibe,
            "empleado": mov.empleado,
            "nota": mov.nota,
            "created_at": mov.created_at
        })

    return resultado


# 🔹 HERRAMIENTAS PRESTADAS (QUIÉN TIENE QUÉ)
@router.get("/prestadas")
def herramientas_prestadas(
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    movimientos = (
        db.query(Movimiento, Producto)
        .join(Producto, Movimiento.producto_id == Producto.id)
        .filter(Movimiento.organizacion_id == user.organizacion_id)
        .order_by(Movimiento.created_at.desc())
        .all()
    )

    estado = {}

    for mov, prod in movimientos:
        key = mov.producto_id

        if key not in estado:
            if mov.tipo == "salida":
                estado[key] = {
                    "producto": prod.nombre,
                    "cantidad": mov.cantidad,
                    "recibe": mov.recibe,
                    "empleado": mov.empleado,
                    "fecha": mov.created_at
                }
            elif mov.tipo == "entrada":
                estado[key] = None

    resultado = [v for v in estado.values() if v is not None]

    return resultado
