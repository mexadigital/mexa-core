from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.core.deps import get_current_user

from app.models.producto import Producto
from app.models.ubicacion import Ubicacion
from app.models.traspaso import Traspaso
from app.models.inventario_ubicacion import InventarioUbicacion

from app.schemas.traspaso import TraspasoCreate, TraspasoOut

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


@router.get("/", response_model=list[TraspasoOut])
def listar_traspasos(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return (
        db.query(Traspaso)
        .filter(Traspaso.organizacion_id == current_user.organizacion_id)
        .order_by(Traspaso.id.desc())
        .all()
    )


@router.post("/", response_model=TraspasoOut, status_code=201)
def crear_traspaso(
    payload: TraspasoCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if payload.cantidad <= 0:
        raise HTTPException(status_code=400, detail="La cantidad debe ser mayor a 0")

    if payload.ubicacion_origen_id == payload.ubicacion_destino_id:
        raise HTTPException(status_code=400, detail="Origen y destino no pueden ser iguales")

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

    origen = (
        db.query(Ubicacion)
        .filter(
            Ubicacion.id == payload.ubicacion_origen_id,
            Ubicacion.organizacion_id == current_user.organizacion_id,
        )
        .first()
    )
    if not origen:
        raise HTTPException(status_code=404, detail="Ubicación origen no encontrada")

    destino = (
        db.query(Ubicacion)
        .filter(
            Ubicacion.id == payload.ubicacion_destino_id,
            Ubicacion.organizacion_id == current_user.organizacion_id,
        )
        .first()
    )
    if not destino:
        raise HTTPException(status_code=404, detail="Ubicación destino no encontrada")

    inventario_origen = obtener_o_crear_inventario(
        db=db,
        organizacion_id=current_user.organizacion_id,
        producto_id=payload.producto_id,
        ubicacion_id=payload.ubicacion_origen_id,
    )

    inventario_destino = obtener_o_crear_inventario(
        db=db,
        organizacion_id=current_user.organizacion_id,
        producto_id=payload.producto_id,
        ubicacion_id=payload.ubicacion_destino_id,
    )

    if inventario_origen.cantidad < payload.cantidad:
        raise HTTPException(
            status_code=400,
            detail=f"Stock insuficiente en origen. Disponible: {inventario_origen.cantidad}"
        )

    inventario_origen.cantidad -= payload.cantidad
    inventario_destino.cantidad += payload.cantidad

    traspaso = Traspaso(
        organizacion_id=current_user.organizacion_id,
        producto_id=payload.producto_id,
        ubicacion_origen_id=payload.ubicacion_origen_id,
        ubicacion_destino_id=payload.ubicacion_destino_id,
        cantidad=payload.cantidad,
        usuario_id=current_user.id,
    )

    db.add(traspaso)
    db.commit()
    db.refresh(traspaso)

    return traspaso
