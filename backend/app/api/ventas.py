from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.database import get_db
from app.schemas.venta import VentaCreate, VentaOut
from app.models.producto import Producto
from app.models.movimiento import Movimiento
from app.models.venta import Venta, VentaDetalle
from app.models.usuario import Usuario
from app.api.deps import get_current_user

router = APIRouter(prefix="/ventas", tags=["Ventas"])


@router.post("/", response_model=VentaOut)
def crear_venta(
    data: VentaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    if not data.productos:
        raise HTTPException(status_code=400, detail="La venta debe incluir al menos un producto")

    organizacion_id = current_user.organizacion_id
    usuario_id = current_user.id

    # 🔥 FIX AQUÍ (created_at manual)
    venta = Venta(
        organizacion_id=organizacion_id,
        usuario_id=usuario_id,
        total=0,
        created_at=datetime.utcnow()
    )
    db.add(venta)
    db.flush()

    total_venta = 0

    for item in data.productos:
        if item.cantidad <= 0:
            raise HTTPException(
                status_code=400,
                detail=f"La cantidad del producto {item.producto_id} debe ser mayor a 0"
            )

        producto = (
            db.query(Producto)
            .filter(
                Producto.id == item.producto_id,
                Producto.organizacion_id == organizacion_id
            )
            .first()
        )

        if not producto:
            raise HTTPException(
                status_code=404,
                detail=f"Producto {item.producto_id} no encontrado en tu organización"
            )

        if producto.cantidad < item.cantidad:
            raise HTTPException(
                status_code=400,
                detail=f"Stock insuficiente para {producto.nombre}. Disponible: {producto.cantidad}"
            )

        precio_unitario = float(producto.precio or 0)
        subtotal = precio_unitario * item.cantidad

        # 🔻 descontar inventario
        producto.cantidad -= item.cantidad

        # 🔻 registrar movimiento
        movimiento = Movimiento(
            organizacion_id=organizacion_id,
            producto_id=producto.id,
            tipo="salida",
            cantidad=item.cantidad,
            usuario=current_user.nombre
        )
        db.add(movimiento)

        # 🔻 detalle de venta
        detalle = VentaDetalle(
            venta_id=venta.id,
            producto_id=producto.id,
            cantidad=item.cantidad,
            precio_unitario=precio_unitario,
            subtotal=subtotal
        )
        db.add(detalle)

        total_venta += subtotal

    # 🔻 total final
    venta.total = total_venta

    db.commit()
    db.refresh(venta)

    return venta
