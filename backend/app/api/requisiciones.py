from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.api.auth import get_current_user
from app.db.database import get_db
from app.models.movimiento import Movimiento
from app.models.producto import Producto
from app.models.requisicion import Requisicion
from app.models.requisicion_detalle import RequisicionDetalle
from app.schemas.requisicion import (
    RequisicionCreate,
    RequisicionOut,
    RequisicionSurtir,
)

router = APIRouter(prefix="/requisiciones", tags=["Requisiciones"])


def generar_folio() -> str:
    return f"REQ-{datetime.now().strftime('%Y%m%d%H%M%S')}"


@router.post("/", response_model=RequisicionOut, status_code=201)
def crear_requisicion(
    data: RequisicionCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    nueva = Requisicion(
        organizacion_id=user["organizacion_id"],
        folio=generar_folio(),
        solicitante=data.solicitante,
        estado="pendiente",
        nota=data.nota,
        extra_data=data.extra_data or {},
    )

    db.add(nueva)
    db.flush()

    for item in data.detalles:
        detalle = RequisicionDetalle(
            requisicion_id=nueva.id,
            producto_id=item.producto_id,
            producto_nombre=item.producto_nombre,
            cantidad_solicitada=item.cantidad_solicitada,
            cantidad_surtida=0,
            estado="pendiente",
            nota=item.nota,
        )
        db.add(detalle)

    db.commit()

    requisicion = (
        db.query(Requisicion)
        .options(joinedload(Requisicion.detalles))
        .filter(
            Requisicion.id == nueva.id,
            Requisicion.organizacion_id == user["organizacion_id"],
        )
        .first()
    )

    return requisicion


@router.get("/", response_model=list[RequisicionOut])
def listar_requisiciones(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    items = (
        db.query(Requisicion)
        .options(joinedload(Requisicion.detalles))
        .filter(Requisicion.organizacion_id == user["organizacion_id"])
        .order_by(Requisicion.id.desc())
        .all()
    )
    return items


@router.get("/{requisicion_id}", response_model=RequisicionOut)
def obtener_requisicion(
    requisicion_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    item = (
        db.query(Requisicion)
        .options(joinedload(Requisicion.detalles))
        .filter(
            Requisicion.id == requisicion_id,
            Requisicion.organizacion_id == user["organizacion_id"],
        )
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Requisición no encontrada")

    return item


@router.put("/{requisicion_id}/surtir", response_model=RequisicionOut)
def surtir_requisicion(
    requisicion_id: int,
    data: RequisicionSurtir,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    requisicion = (
        db.query(Requisicion)
        .options(joinedload(Requisicion.detalles))
        .filter(
            Requisicion.id == requisicion_id,
            Requisicion.organizacion_id == user["organizacion_id"],
        )
        .first()
    )

    if not requisicion:
        raise HTTPException(status_code=404, detail="Requisición no encontrada")

    detalles_map = {d.id: d for d in requisicion.detalles}

    for item in data.detalles:
        detalle = detalles_map.get(item.detalle_id)

        if not detalle:
            raise HTTPException(
                status_code=404,
                detail=f"Detalle {item.detalle_id} no encontrado",
            )

        if item.cantidad_surtida <= 0:
            raise HTTPException(status_code=400, detail="Cantidad inválida")

        if detalle.cantidad_surtida + item.cantidad_surtida > detalle.cantidad_solicitada:
            raise HTTPException(
                status_code=400,
                detail="No puedes surtir más de lo solicitado",
            )

        producto = (
            db.query(Producto)
            .filter(
                Producto.id == detalle.producto_id,
                Producto.organizacion_id == user["organizacion_id"],
            )
            .first()
        )

        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        if producto.cantidad < item.cantidad_surtida:
            raise HTTPException(
                status_code=400,
                detail=f"Stock insuficiente para {producto.nombre}",
            )

        producto.cantidad -= item.cantidad_surtida

        movimiento = Movimiento(
            organizacion_id=user["organizacion_id"],
            producto_id=producto.id,
            tipo="salida",
            cantidad=item.cantidad_surtida,
            usuario=user["email"],
            recibe=requisicion.solicitante,
            nota=f"Surtido requisición {requisicion.folio}",
        )
        db.add(movimiento)

        detalle.cantidad_surtida += item.cantidad_surtida

        if detalle.cantidad_surtida == 0:
            detalle.estado = "pendiente"
        elif detalle.cantidad_surtida < detalle.cantidad_solicitada:
            detalle.estado = "parcial"
        else:
            detalle.estado = "surtido"

    estados = [d.estado for d in requisicion.detalles]

    if all(e == "surtido" for e in estados):
        requisicion.estado = "surtida"
    elif any(e in ("parcial", "surtido") for e in estados):
        requisicion.estado = "parcial"
    else:
        requisicion.estado = "pendiente"

    if data.nota:
        requisicion.nota = data.nota

    db.commit()

    requisicion = (
        db.query(Requisicion)
        .options(joinedload(Requisicion.detalles))
        .filter(
            Requisicion.id == requisicion_id,
            Requisicion.organizacion_id == user["organizacion_id"],
        )
        .first()
    )

    return requisicion
