from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.core.deps import get_current_user

from app.models.producto import Producto
from app.models.ubicacion import Ubicacion
from app.models.inventario_ubicacion import InventarioUbicacion

from app.schemas.inventario_ubicacion import (
    InventarioUbicacionAsignar,
    InventarioUbicacionOut,
)

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def obtener_o_crear_inventario(
    db: Session,
    organizacion_id: int,
    producto_id: int,
    ubicacion_id: int,
):
    inventario = (
        db.query(InventarioUbicacion)
        .filter(
            InventarioUbicacion.organizacion_id == organizacion_id,
            InventarioUbicacion.producto_id == producto_id,
            InventarioUbicacion.ubicacion_id == ubicacion_id,
        )
        .first()
    )

    if not inventario:
        inventario = InventarioUbicacion(
            organizacion_id=organizacion_id,
            producto_id=producto_id,
            ubicacion_id=ubicacion_id,
            cantidad=0,
        )
        db.add(inventario)
        db.flush()

    return inventario


@router.get("/", response_model=list[InventarioUbicacionOut])
def listar_inventario_ubicaciones(
    producto_id: int | None = Query(default=None),
    ubicacion_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = db.query(InventarioUbicacion).filter(
        InventarioUbicacion.organizacion_id == current_user.organizacion_id
    )

    if producto_id is not None:
        query = query.filter(InventarioUbicacion.producto_id == producto_id)

    if ubicacion_id is not None:
        query = query.filter(InventarioUbicacion.ubicacion_id == ubicacion_id)

    return query.order_by(InventarioUbicacion.id.asc()).all()


@router.post("/asignar", response_model=InventarioUbicacionOut, status_code=201)
def asignar_stock_a_ubicacion(
    payload: InventarioUbicacionAsignar,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if payload.cantidad <= 0:
        raise HTTPException(status_code=400, detail="La cantidad debe ser mayor a 0")

    producto = (
        db.query(Producto)
        .filter(
            Producto.id == payload.producto_id,
            Producto.organizacion_id == current_user.organizacion_id,
        )
        .first()
    )
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    ubicacion = (
        db.query(Ubicacion)
        .filter(
            Ubicacion.id == payload.ubicacion_id,
            Ubicacion.organizacion_id == current_user.organizacion_id,
        )
        .first()
    )
    if not ubicacion:
        raise HTTPException(status_code=404, detail="Ubicación no encontrada")

    total_asignado = (
        db.query(func.coalesce(func.sum(InventarioUbicacion.cantidad), 0))
        .filter(
            InventarioUbicacion.organizacion_id == current_user.organizacion_id,
            InventarioUbicacion.producto_id == payload.producto_id,
        )
        .scalar()
    )

    disponible_sin_asignar = producto.cantidad - total_asignado

    if payload.cantidad > disponible_sin_asignar:
        raise HTTPException(
            status_code=400,
            detail=f"No hay stock global suficiente sin asignar. Disponible: {disponible_sin_asignar}"
        )

    inventario = obtener_o_crear_inventario(
        db=db,
        organizacion_id=current_user.organizacion_id,
        producto_id=payload.producto_id,
        ubicacion_id=payload.ubicacion_id,
    )

    inventario.cantidad += payload.cantidad

    db.commit()
    db.refresh(inventario)

    return inventario
