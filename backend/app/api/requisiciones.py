from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.db.database import get_db
from app.models.requisicion import Requisicion
from app.models.requisicion_detalle import RequisicionDetalle
from app.schemas.requisicion import RequisicionCreate, RequisicionOut
from app.api.auth import get_current_user


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
