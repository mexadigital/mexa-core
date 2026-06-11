from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
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
    tags=["Vales de Resguardo"],
)


# ==========================================================
# HELPERS
# ==========================================================
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
    """
    Recalcula el estado del vale con base en sus detalles.

    Estados usados:
    - abierto: se puede seguir agregando herramienta.
    - cerrado: ya no se agrega herramienta, pero puede tener pendientes.
    - parcial: ya devolvió algo, pero todavía debe.
    - devuelto: ya devolvió todo.
    - cancelado: anulado.
    """

    if vale.estado_vale == "cancelado":
        return

    if not vale.detalles:
        if vale.estado_vale not in ["cerrado"]:
            vale.estado_vale = "abierto"
            vale.fecha_cierre = None
        return

    total_entregado = 0
    total_devuelto = 0

    for d in vale.detalles:
        entregado = d.cantidad_entregada or 0
        devuelto = d.cantidad_devuelta or 0

        total_entregado += entregado
        total_devuelto += devuelto

        if devuelto <= 0:
            d.estado = "pendiente"
        elif devuelto < entregado:
            d.estado = "parcial"
        else:
            d.estado = "devuelto"

    if total_entregado <= 0:
        vale.estado_vale = "abierto"
        vale.fecha_cierre = None
        return

    if total_devuelto <= 0:
        # Si ya fue cerrado manualmente, se queda cerrado.
        # Si no, sigue abierto.
        if vale.estado_vale != "cerrado":
            vale.estado_vale = "abierto"
            vale.fecha_cierre = None

    elif total_devuelto < total_entregado:
        vale.estado_vale = "parcial"
        vale.fecha_cierre = None

    else:
        vale.estado_vale = "devuelto"
        vale.fecha_cierre = datetime.utcnow()


def obtener_vale_o_404(
    vale_id: int,
    db: Session,
    organizacion_id: int,
) -> ValeResguardo:
    vale = (
        db.query(ValeResguardo)
        .filter(ValeResguardo.id == vale_id)
        .filter(ValeResguardo.organizacion_id == organizacion_id)
        .first()
    )

    if not vale:
        raise HTTPException(status_code=404, detail="Vale no encontrado")

    return vale


def pendiente_detalle(detalle: ValeResguardoDetalle) -> int:
    entregado = detalle.cantidad_entregada or 0
    devuelto = detalle.cantidad_devuelta or 0
    pendiente = entregado - devuelto

    if pendiente < 0:
        return 0

    return pendiente


# ==========================================================
# CREAR VALE
# ==========================================================
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
                detail="La cantidad entregada debe ser mayor a 0",
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


# ==========================================================
# LISTAR VALES
# ==========================================================
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
        .filter(ValeResguardo.estado_vale.in_(["abierto", "parcial", "cerrado"]))
        .order_by(ValeResguardo.id.desc())
        .all()
    )


# ==========================================================
# REPORTE DÍA 12 — BAJAS / PENDIENTES POR EMPLEADO
# IMPORTANTE:
# Esta ruta va antes de "/{vale_id}" para que FastAPI no confunda
# "reporte-empleado" con un ID.
# ==========================================================
@router.get("/reporte-empleado")
def reporte_pendientes_por_empleado(
    q: str = Query(..., description="Nombre, número de empleado, folio o vale físico"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    organizacion_id = current_user.organizacion_id
    like = f"%{q}%"

    # Primero encontramos un vale que coincida con la búsqueda.
    vale_base = (
        db.query(ValeResguardo)
        .filter(ValeResguardo.organizacion_id == organizacion_id)
        .filter(
            (ValeResguardo.empleado_recibe.ilike(like))
            | (ValeResguardo.numero_empleado.ilike(like))
            | (ValeResguardo.folio_sistema.ilike(like))
            | (ValeResguardo.numero_vale_fisico.ilike(like))
        )
        .order_by(ValeResguardo.id.desc())
        .first()
    )

    if not vale_base:
        return {
            "encontrado": False,
            "puede_salir": True,
            "estado_liberacion": "SIN_REGISTROS",
            "mensaje": "No se encontraron vales para esa búsqueda.",
            "empleado": None,
            "total_pendientes": 0,
            "vales_pendientes": [],
        }

    # Si tiene número de empleado, usamos ese dato como llave principal.
    # Si no, usamos el nombre.
    query_vales = db.query(ValeResguardo).filter(
        ValeResguardo.organizacion_id == organizacion_id
    )

    if vale_base.numero_empleado:
        query_vales = query_vales.filter(
            ValeResguardo.numero_empleado == vale_base.numero_empleado
        )
    else:
        query_vales = query_vales.filter(
            ValeResguardo.empleado_recibe.ilike(f"%{vale_base.empleado_recibe}%")
        )

    vales = query_vales.order_by(ValeResguardo.id.desc()).all()

    total_pendientes = 0
    vales_pendientes = []

    for vale in vales:
        herramientas_pendientes = []

        for d in vale.detalles:
            pendiente = pendiente_detalle(d)

            if pendiente > 0:
                total_pendientes += pendiente

                herramientas_pendientes.append(
                    {
                        "detalle_id": d.id,
                        "herramienta_nombre": d.herramienta_nombre,
                        "item_code": d.item_code,
                        "medida_size": d.medida_size,
                        "unidad": d.unidad,
                        "marca": d.marca,
                        "modelo": d.modelo,
                        "serie": d.serie,
                        "cantidad_entregada": d.cantidad_entregada,
                        "cantidad_devuelta": d.cantidad_devuelta,
                        "cantidad_pendiente": pendiente,
                        "estado": d.estado,
                        "observacion": d.observacion,
                    }
                )

        if herramientas_pendientes:
            vales_pendientes.append(
                {
                    "vale_id": vale.id,
                    "folio_sistema": vale.folio_sistema,
                    "numero_vale_fisico": vale.numero_vale_fisico,
                    "estado_vale": vale.estado_vale,
                    "fecha_creacion": vale.fecha_creacion,
                    "fecha_cierre": vale.fecha_cierre,
                    "ubicacion_origen": vale.ubicacion_origen,
                    "ubicacion_fisica_vale": vale.ubicacion_fisica_vale,
                    "estado_archivo_fisico": vale.estado_archivo_fisico,
                    "area_frente": vale.area_frente,
                    "responsable": vale.usuario_creador,
                    "herramientas": herramientas_pendientes,
                }
            )

    puede_salir = total_pendientes == 0

    if puede_salir:
        estado_liberacion = "LIBRE"
        mensaje = "El empleado no tiene herramientas pendientes por devolver."
    else:
        estado_liberacion = "NO_LIBERAR"
        mensaje = "El empleado tiene herramientas pendientes por devolver."

    return {
        "encontrado": True,
        "puede_salir": puede_salir,
        "estado_liberacion": estado_liberacion,
        "mensaje": mensaje,
        "empleado": {
            "empleado_recibe": vale_base.empleado_recibe,
            "numero_empleado": vale_base.numero_empleado,
            "puesto": vale_base.puesto,
            "area_frente": vale_base.area_frente,
        },
        "total_pendientes": total_pendientes,
        "vales_pendientes": vales_pendientes,
    }


# ==========================================================
# OBTENER VALE
# ==========================================================
@router.get("/{vale_id}", response_model=ValeResguardoOut)
def obtener_vale_resguardo(
    vale_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    vale = obtener_vale_o_404(
        vale_id=vale_id,
        db=db,
        organizacion_id=current_user.organizacion_id,
    )

    return vale


# ==========================================================
# AGREGAR HERRAMIENTA A VALE ABIERTO
# ==========================================================
@router.post("/{vale_id}/detalles", response_model=ValeResguardoOut)
def agregar_herramienta_a_vale(
    vale_id: int,
    data: AgregarDetalleVale,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    vale = obtener_vale_o_404(
        vale_id=vale_id,
        db=db,
        organizacion_id=current_user.organizacion_id,
    )

    if vale.estado_vale in ["cerrado", "devuelto", "cancelado"]:
        raise HTTPException(
            status_code=400,
            detail="No puedes agregar herramientas a un vale cerrado, devuelto o cancelado",
        )

    if data.cantidad_entregada <= 0:
        raise HTTPException(
            status_code=400,
            detail="La cantidad entregada debe ser mayor a 0",
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

    if vale.estado_vale not in ["parcial"]:
        vale.estado_vale = "abierto"

    db.commit()
    db.refresh(vale)

    return vale


# ==========================================================
# CERRAR VALE MANUALMENTE
# ==========================================================
@router.post("/{vale_id}/cerrar", response_model=ValeResguardoOut)
def cerrar_vale_resguardo(
    vale_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    vale = obtener_vale_o_404(
        vale_id=vale_id,
        db=db,
        organizacion_id=current_user.organizacion_id,
    )

    if vale.estado_vale == "cancelado":
        raise HTTPException(
            status_code=400,
            detail="No puedes cerrar un vale cancelado",
        )

    if vale.estado_vale == "devuelto":
        raise HTTPException(
            status_code=400,
            detail="El vale ya está devuelto completamente",
        )

    # Cerrar aquí significa:
    # "Ya no se pueden agregar más herramientas a este vale físico".
    # Todavía puede tener pendientes por devolver.
    vale.estado_vale = "cerrado"
    vale.fecha_cierre = datetime.utcnow()

    db.commit()
    db.refresh(vale)

    return vale


# ==========================================================
# REABRIR VALE
# ==========================================================
@router.post("/{vale_id}/reabrir", response_model=ValeResguardoOut)
def reabrir_vale_resguardo(
    vale_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    vale = obtener_vale_o_404(
        vale_id=vale_id,
        db=db,
        organizacion_id=current_user.organizacion_id,
    )

    if vale.estado_vale == "cancelado":
        raise HTTPException(
            status_code=400,
            detail="No puedes reabrir un vale cancelado",
        )

    if vale.estado_vale == "devuelto":
        raise HTTPException(
            status_code=400,
            detail="No puedes reabrir un vale devuelto completamente",
        )

    vale.estado_vale = "abierto"
    vale.fecha_cierre = None

    db.commit()
    db.refresh(vale)

    return vale


# ==========================================================
# CANCELAR VALE
# ==========================================================
@router.post("/{vale_id}/cancelar", response_model=ValeResguardoOut)
def cancelar_vale_resguardo(
    vale_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    vale = obtener_vale_o_404(
        vale_id=vale_id,
        db=db,
        organizacion_id=current_user.organizacion_id,
    )

    if vale.estado_vale == "devuelto":
        raise HTTPException(
            status_code=400,
            detail="No puedes cancelar un vale que ya fue devuelto completamente",
        )

    vale.estado_vale = "cancelado"
    vale.fecha_cierre = datetime.utcnow()

    for d in vale.detalles:
        d.estado = "cancelado"

    db.commit()
    db.refresh(vale)

    return vale


# ==========================================================
# REGISTRAR DEVOLUCIÓN
# ==========================================================
@router.post("/{vale_id}/devolver", response_model=ValeResguardoOut)
def registrar_devolucion(
    vale_id: int,
    data: DevolucionVale,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    vale = obtener_vale_o_404(
        vale_id=vale_id,
        db=db,
        organizacion_id=current_user.organizacion_id,
    )

    if vale.estado_vale == "cancelado":
        raise HTTPException(
            status_code=400,
            detail="No puedes registrar devolución en un vale cancelado",
        )

    if vale.estado_vale == "devuelto":
        raise HTTPException(
            status_code=400,
            detail="Este vale ya fue devuelto completamente",
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
                detail=f"Detalle {dev.detalle_id} no encontrado",
            )

        if dev.cantidad_devuelta <= 0:
            raise HTTPException(
                status_code=400,
                detail="La devolución debe ser mayor a 0",
            )

        nueva_cantidad = (detalle.cantidad_devuelta or 0) + dev.cantidad_devuelta

        if nueva_cantidad > detalle.cantidad_entregada:
            raise HTTPException(
                status_code=400,
                detail=f"No puedes devolver más de lo entregado en: {detalle.herramienta_nombre}",
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


# ==========================================================
# CAMBIAR UBICACIÓN DEL ARCHIVO FÍSICO
# ==========================================================
@router.patch("/{vale_id}/archivo-fisico", response_model=ValeResguardoOut)
def cambiar_ubicacion_archivo_fisico(
    vale_id: int,
    data: CambiarArchivoFisico,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    vale = obtener_vale_o_404(
        vale_id=vale_id,
        db=db,
        organizacion_id=current_user.organizacion_id,
    )

    vale.ubicacion_fisica_vale = data.ubicacion_fisica_vale
    vale.estado_archivo_fisico = data.estado_archivo_fisico

    db.commit()
    db.refresh(vale)

    return vale
