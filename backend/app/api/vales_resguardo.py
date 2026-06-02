from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.vale_resguardo import ValeResguardo, ValeResguardoDetalle
from app.schemas.vale_resguardo import (
    ValeResguardoCreate,
    ValeResguardoOut,
    DevolucionVale,
    CambiarArchivoFisico,
    AgregarDetalleVale,
)
from app.api.auth import get_current_user


router = APIRouter(
    prefix="/vales-resguardo",
    tags=["Vales de Resguardo"]
)


def generar_folio_sistema(db: Session, organizacion_id: int) -> str:
    ultimo = (
        db.query(ValeResguardo)
        .filter(ValeResguardo.organizacion_id == organizacion_id)
        .order_by(ValeResguardo.id.desc())
        .first()
    )

    if not ultimo:
        siguiente = 1
    else:
        siguiente = ultimo.id + 1

    return f"A{siguiente:04d}"


def recalcular_estado_vale(vale: ValeResguardo):
    if not vale.detalles:
        vale.estado_vale = "abierto"
        vale.fecha_cierre = None
        return

    total_entregado = 0
    total_devuelto = 0

    for d in vale.detalles:
        total_entregado += d.cantidad_entregada
        total_devuelto += d.cantidad_devuelta

        if d.cantidad_devuelta <= 0:
            d.estado = "pendiente"
        elif d.cantidad_devuelta < d.cantidad_entregada:
            d.estado = "parcial"
        else:
            d.estado = "devuelto"

    if total_devuelto <= 0:
        vale.estado_vale = "abierto"
        vale.fecha_cierre = None
    elif total_devuelto < total_entregado:
        vale.estado_vale = "parcial"
        vale.fecha_cierre = None
    else:
        vale.estado_vale = "cerrado"
        vale.fecha_cierre = datetime.utcnow()


@router.post("/", response_model=ValeResguardoOut)
def crear_vale_resguardo(
    data: ValeResguardoCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    organizacion_id = current_user.organizacion_id

    folio = generar_folio_sistema(db, organizacion_id)

    vale = ValeResguardo(
        organizacion_id=organizacion_id,
        folio_sistema=folio,
        numero_vale_fisico=data.numero_vale_fisico,
        empleado_recibe=data.empleado_recibe,
        numero_empleado=data.numero_empleado,
        puesto=data.puesto,
        area_frente=data.area_frente,
        ubicacion_origen=data.ubicacion_origen,
        ubicacion_fisica_vale=data.ubicacion_fisica_vale,
        estado_archivo_fisico=data.estado_archivo_fisico,
        foto_url=data.foto_url,
        nota=data.nota,
        usuario_creador=getattr(current_user, "email", None),
        estado_vale="abierto",
    )

    db.add(vale)
    db.flush()

    for item in data.detalles:
        if item.cantidad_entregada <= 0:
            raise HTTPException(
                status_code=400,
                detail="La cantidad entregada debe ser mayor a 0"
            )

        detalle = ValeResguardoDetalle(
            vale_id=vale.id,
            herramienta_nombre=item.herramienta_nombre,
            item_code=item.item_code,
            medida_size=item.medida_size,
            unidad=item.unidad,
            marca=item.marca,
            modelo=item.modelo,
            serie=item.serie,
            cantidad_entregada=item.cantidad_entregada,
            cantidad_devuelta=0,
            estado="pendiente",
            observacion=item.observacion,
        )
        db.add(detalle)

    db.commit()
    db.refresh(vale)

    return vale


@router.get("/", response_model=list[ValeResguardoOut])
def listar_vales_resguardo(
    q: str | None = None,
    estado: str | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = db.query(ValeResguardo).filter(
        ValeResguardo.organizacion_id == current_user.organizacion_id
    )

    if estado:
        query = query.filter(ValeResguardo.estado_vale == estado)

    if q:
        like = f"%{q}%"
        query = query.filter(
            (ValeResguardo.empleado_recibe.ilike(like))
            | (ValeResguardo.numero_empleado.ilike(like))
            | (ValeResguardo.folio_sistema.ilike(like))
            | (ValeResguardo.numero_vale_fisico.ilike(like))
            | (ValeResguardo.area_frente.ilike(like))
        )

    return query.order_by(ValeResguardo.id.desc()).all()


@router.get("/abiertos", response_model=list[ValeResguardoOut])
def listar_vales_abiertos(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return (
        db.query(ValeResguardo)
        .filter(ValeResguardo.organizacion_id == current_user.organizacion_id)
        .filter(ValeResguardo.estado_vale.in_(["abierto", "parcial"]))
        .order_by(ValeResguardo.id.desc())
        .all()
    )


@router.get("/{vale_id}", response_model=ValeResguardoOut)
def obtener_vale_resguardo(
    vale_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    vale = (
        db.query(ValeResguardo)
        .filter(ValeResguardo.id == vale_id)
        .filter(ValeResguardo.organizacion_id == current_user.organizacion_id)
        .first()
    )

    if not vale:
        raise HTTPException(status_code=404, detail="Vale no encontrado")

    return vale


@router.post("/{vale_id}/detalles", response_model=ValeResguardoOut)
def agregar_herramienta_a_vale(
    vale_id: int,
    data: AgregarDetalleVale,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    vale = (
        db.query(ValeResguardo)
        .filter(ValeResguardo.id == vale_id)
        .filter(ValeResguardo.organizacion_id == current_user.organizacion_id)
        .first()
    )

    if not vale:
        raise HTTPException(status_code=404, detail="Vale no encontrado")

    if vale.estado_vale in ["cerrado", "cancelado"]:
        raise HTTPException(
            status_code=400,
            detail="No puedes agregar herramientas a un vale cerrado o cancelado"
        )

    if data.cantidad_entregada <= 0:
        raise HTTPException(
            status_code=400,
            detail="La cantidad entregada debe ser mayor a 0"
        )

    detalle = ValeResguardoDetalle(
        vale_id=vale.id,
        herramienta_nombre=data.herramienta_nombre,
        item_code=data.item_code,
        medida_size=data.medida_size,
        unidad=data.unidad,
        marca=data.marca,
        modelo=data.modelo,
        serie=data.serie,
        cantidad_entregada=data.cantidad_entregada,
        cantidad_devuelta=0,
        estado="pendiente",
        observacion=data.observacion,
    )

    db.add(detalle)

    # Si estaba parcial y agregas otra herramienta, sigue parcial.
    # Si estaba abierto, sigue abierto.
    if vale.estado_vale not in ["parcial"]:
        vale.estado_vale = "abierto"

    db.commit()
    db.refresh(vale)

    return vale


@router.post("/{vale_id}/devolver", response_model=ValeResguardoOut)
def registrar_devolucion(
    vale_id: int,
    data: DevolucionVale,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    vale = (
        db.query(ValeResguardo)
        .filter(ValeResguardo.id == vale_id)
        .filter(ValeResguardo.organizacion_id == current_user.organizacion_id)
        .first()
    )

    if not vale:
        raise HTTPException(status_code=404, detail="Vale no encontrado")

    if vale.estado_vale in ["cerrado", "cancelado"]:
        raise HTTPException(
            status_code=400,
            detail="No puedes registrar devolución en un vale cerrado o cancelado"
        )

    for dev in data.devoluciones:
        detalle = (
            db.query(ValeResguardoDetalle)
            .filter(ValeResguardoDetalle.id == dev.detalle_id)
            .filter(ValeResguardoDetalle.vale_id == vale.id)
            .first()
        )

        if not detalle:
            raise HTTPException(
                status_code=404,
                detail=f"Detalle {dev.detalle_id} no encontrado"
            )

        if dev.cantidad_devuelta <= 0:
            raise HTTPException(
                status_code=400,
                detail="La devolución debe ser mayor a 0"
            )

        nueva_cantidad = detalle.cantidad_devuelta + dev.cantidad_devuelta

        if nueva_cantidad > detalle.cantidad_entregada:
            raise HTTPException(
                status_code=400,
                detail=f"No puedes devolver más de lo entregado en: {detalle.herramienta_nombre}"
            )

        detalle.cantidad_devuelta = nueva_cantidad

        if dev.observacion:
            if detalle.observacion:
                detalle.observacion += f" | DEVOLUCIÓN: {dev.observacion}"
            else:
                detalle.observacion = f"DEVOLUCIÓN: {dev.observacion}"

    recalcular_estado_vale(vale)

    db.commit()
    db.refresh(vale)

    return vale


@router.patch("/{vale_id}/archivo-fisico", response_model=ValeResguardoOut)
def cambiar_ubicacion_archivo_fisico(
    vale_id: int,
    data: CambiarArchivoFisico,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    vale = (
        db.query(ValeResguardo)
        .filter(ValeResguardo.id == vale_id)
        .filter(ValeResguardo.organizacion_id == current_user.organizacion_id)
        .first()
    )

    if not vale:
        raise HTTPException(status_code=404, detail="Vale no encontrado")

    vale.ubicacion_fisica_vale = data.ubicacion_fisica_vale
    vale.estado_archivo_fisico = data.estado_archivo_fisico

    db.commit()
    db.refresh(vale)

    return vale
