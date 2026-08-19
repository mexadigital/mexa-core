import re
from datetime import datetime, timezone
from html import escape
from io import BytesIO
from urllib.parse import quote

import qrcode
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse, StreamingResponse
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.database import get_db
from app.models.escolar import (
    Alumno,
    Calificacion,
    GrupoEscolar,
    Materia,
    SolicitudConstancia,
)
from app.models.organizacion import Organizacion
from app.models.usuario import Usuario
from app.schemas.escolar import (
    AlumnoCreate,
    AlumnoOut,
    AlumnoUpdate,
    BoletaOut,
    CalificacionCreate,
    CalificacionOut,
    ConfiguracionEscolarOut,
    ConfiguracionEscolarUpdate,
    ConstanciaCreate,
    ConstanciaOut,
    GrupoCreate,
    GrupoOut,
    GrupoUpdate,
    MateriaCalificacionOut,
    MateriaCreate,
    MateriaOut,
    PagoConstanciaUpdate,
    VerificacionConstanciaOut,
)
from app.services.constancias import (
    construir_folio,
    nombre_protegido,
    nuevo_token_verificacion,
    validar_transicion,
)


router = APIRouter(prefix="/escolar", tags=["MEXA Escolar"])


def _texto_limpio(valor: str | None) -> str | None:
    if valor is None:
        return None
    limpio = valor.strip()
    return limpio or None


def _organizacion_actual(db: Session, user: Usuario) -> Organizacion:
    organizacion = (
        db.query(Organizacion)
        .filter(Organizacion.id == user.organizacion_id)
        .first()
    )
    if not organizacion:
        raise HTTPException(status_code=404, detail="Institución no encontrada")
    return organizacion


@router.get("/configuracion", response_model=ConfiguracionEscolarOut)
def obtener_configuracion_escolar(
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    return _organizacion_actual(db, user)


@router.patch("/configuracion", response_model=ConfiguracionEscolarOut)
def actualizar_configuracion_escolar(
    data: ConfiguracionEscolarUpdate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    if user.rol.lower() not in {"admin", "superadmin", "director", "direccion"}:
        raise HTTPException(
            status_code=403,
            detail="Sólo Dirección o Administración puede cambiar la institución",
        )

    organizacion = _organizacion_actual(db, user)
    nombre_repetido = (
        db.query(Organizacion)
        .filter(
            Organizacion.nombre == data.nombre.strip(),
            Organizacion.id != organizacion.id,
        )
        .first()
    )
    if nombre_repetido:
        raise HTTPException(
            status_code=409,
            detail="Ya existe una institución con ese nombre",
        )
    valores = data.model_dump()
    valores["nombre"] = data.nombre.strip()
    for campo, valor in valores.items():
        valor_final = _texto_limpio(valor) if campo != "nombre" else valor
        setattr(organizacion, campo, valor_final)
    db.commit()
    db.refresh(organizacion)
    return organizacion


def _propio_o_404(db: Session, model, record_id: int, user: Usuario):
    registro = (
        db.query(model)
        .filter(
            model.id == record_id,
            model.organizacion_id == user.organizacion_id,
        )
        .first()
    )
    if not registro:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    return registro


@router.post("/grupos", response_model=GrupoOut, status_code=status.HTTP_201_CREATED)
def crear_grupo(
    data: GrupoCreate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    nombre = data.nombre.strip()
    ciclo = data.ciclo_escolar.strip()
    if not nombre or not ciclo:
        raise HTTPException(status_code=422, detail="Grupo y ciclo son obligatorios")
    existente = (
        db.query(GrupoEscolar)
        .filter(
            GrupoEscolar.organizacion_id == user.organizacion_id,
            GrupoEscolar.nombre == nombre,
            GrupoEscolar.ciclo_escolar == ciclo,
        )
        .first()
    )
    if existente:
        raise HTTPException(status_code=400, detail="El grupo ya existe en ese ciclo")

    grupo = GrupoEscolar(
        organizacion_id=user.organizacion_id,
        nombre=nombre,
        grado=_texto_limpio(data.grado),
        ciclo_escolar=ciclo,
    )
    db.add(grupo)
    db.commit()
    db.refresh(grupo)
    return grupo


@router.get("/grupos", response_model=list[GrupoOut])
def listar_grupos(
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    return (
        db.query(GrupoEscolar)
        .filter(GrupoEscolar.organizacion_id == user.organizacion_id)
        .order_by(GrupoEscolar.ciclo_escolar.desc(), GrupoEscolar.nombre.asc())
        .all()
    )


@router.patch("/grupos/{grupo_id}", response_model=GrupoOut)
def actualizar_grupo(
    grupo_id: int,
    data: GrupoUpdate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    grupo = _propio_o_404(db, GrupoEscolar, grupo_id, user)
    cambios = data.model_dump(exclude_unset=True)
    if cambios.get("nombre") is None or cambios.get("ciclo_escolar") is None:
        if "nombre" in cambios or "ciclo_escolar" in cambios:
            raise HTTPException(status_code=422, detail="Grupo y ciclo no pueden quedar vacíos")
    for campo in {"nombre", "grado", "ciclo_escolar"} & cambios.keys():
        cambios[campo] = _texto_limpio(cambios[campo])
    if not cambios.get("nombre", grupo.nombre) or not cambios.get(
        "ciclo_escolar", grupo.ciclo_escolar
    ):
        raise HTTPException(status_code=422, detail="Grupo y ciclo no pueden quedar vacíos")
    nombre_final = cambios.get("nombre", grupo.nombre)
    ciclo_final = cambios.get("ciclo_escolar", grupo.ciclo_escolar)
    repetido = (
        db.query(GrupoEscolar)
        .filter(
            GrupoEscolar.organizacion_id == user.organizacion_id,
            GrupoEscolar.nombre == nombre_final,
            GrupoEscolar.ciclo_escolar == ciclo_final,
            GrupoEscolar.id != grupo.id,
        )
        .first()
    )
    if repetido:
        raise HTTPException(status_code=409, detail="El grupo ya existe en ese ciclo")
    for campo, valor in cambios.items():
        setattr(grupo, campo, valor)
    db.commit()
    db.refresh(grupo)
    return grupo


@router.post("/alumnos", response_model=AlumnoOut, status_code=status.HTTP_201_CREATED)
def crear_alumno(
    data: AlumnoCreate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    _propio_o_404(db, GrupoEscolar, data.grupo_id, user)
    matricula = data.matricula.strip()
    nombre = data.nombre_completo.strip()
    if not matricula or not nombre:
        raise HTTPException(status_code=422, detail="Matrícula y nombre son obligatorios")
    existente = (
        db.query(Alumno)
        .filter(
            Alumno.organizacion_id == user.organizacion_id,
            Alumno.matricula == matricula,
        )
        .first()
    )
    if existente:
        raise HTTPException(status_code=400, detail="La matrícula ya está registrada")

    alumno = Alumno(
        organizacion_id=user.organizacion_id,
        grupo_id=data.grupo_id,
        matricula=matricula,
        nombre_completo=nombre,
        nombre_tutor=_texto_limpio(data.nombre_tutor),
        telefono_tutor=_texto_limpio(data.telefono_tutor),
    )
    db.add(alumno)
    db.commit()
    db.refresh(alumno)
    return alumno


@router.get("/alumnos", response_model=list[AlumnoOut])
def listar_alumnos(
    grupo_id: int | None = Query(default=None),
    q: str | None = Query(default=None),
    estado: str | None = Query(default=None, pattern="^(activo|inactivo)$"),
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    query = db.query(Alumno).filter(Alumno.organizacion_id == user.organizacion_id)
    if grupo_id is not None:
        query = query.filter(Alumno.grupo_id == grupo_id)
    if q:
        like = f"%{q}%"
        query = query.filter(
            (Alumno.nombre_completo.ilike(like)) | (Alumno.matricula.ilike(like))
        )
    if estado:
        query = query.filter(Alumno.estado == estado)
    return query.order_by(Alumno.nombre_completo.asc()).all()


@router.patch("/alumnos/{alumno_id}", response_model=AlumnoOut)
def actualizar_alumno(
    alumno_id: int,
    data: AlumnoUpdate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    alumno = _propio_o_404(db, Alumno, alumno_id, user)
    cambios = data.model_dump(exclude_unset=True)

    for campo in {"grupo_id", "matricula", "nombre_completo"}:
        if campo in cambios and cambios[campo] is None:
            raise HTTPException(
                status_code=422,
                detail="Grupo, matrícula y nombre no pueden quedar vacíos",
            )

    if "grupo_id" in cambios:
        _propio_o_404(db, GrupoEscolar, cambios["grupo_id"], user)
    if "matricula" in cambios:
        matricula = cambios["matricula"].strip()
        if not matricula:
            raise HTTPException(status_code=422, detail="La matrícula no puede quedar vacía")
        repetida = (
            db.query(Alumno)
            .filter(
                Alumno.organizacion_id == user.organizacion_id,
                Alumno.matricula == matricula,
                Alumno.id != alumno.id,
            )
            .first()
        )
        if repetida:
            raise HTTPException(status_code=409, detail="La matrícula ya está registrada")
        cambios["matricula"] = matricula

    if "nombre_completo" in cambios and not cambios["nombre_completo"].strip():
        raise HTTPException(status_code=422, detail="El nombre no puede quedar vacío")
    for campo in {"nombre_completo", "nombre_tutor", "telefono_tutor"} & cambios.keys():
        cambios[campo] = _texto_limpio(cambios[campo])
    for campo, valor in cambios.items():
        setattr(alumno, campo, valor)
    db.commit()
    db.refresh(alumno)
    return alumno


@router.post("/materias", response_model=MateriaOut, status_code=status.HTTP_201_CREATED)
def crear_materia(
    data: MateriaCreate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    existente = (
        db.query(Materia)
        .filter(
            Materia.organizacion_id == user.organizacion_id,
            Materia.nombre == data.nombre,
        )
        .first()
    )
    if existente:
        raise HTTPException(status_code=400, detail="La materia ya está registrada")

    materia = Materia(organizacion_id=user.organizacion_id, **data.model_dump())
    db.add(materia)
    db.commit()
    db.refresh(materia)
    return materia


@router.get("/materias", response_model=list[MateriaOut])
def listar_materias(
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    return (
        db.query(Materia)
        .filter(Materia.organizacion_id == user.organizacion_id)
        .order_by(Materia.nombre.asc())
        .all()
    )


@router.post("/calificaciones", response_model=CalificacionOut)
def guardar_calificacion(
    data: CalificacionCreate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    _propio_o_404(db, Alumno, data.alumno_id, user)
    _propio_o_404(db, Materia, data.materia_id, user)

    calificacion = (
        db.query(Calificacion)
        .filter(
            Calificacion.organizacion_id == user.organizacion_id,
            Calificacion.alumno_id == data.alumno_id,
            Calificacion.materia_id == data.materia_id,
            Calificacion.periodo == data.periodo,
        )
        .first()
    )
    if calificacion:
        calificacion.valor = data.valor
        calificacion.observaciones = data.observaciones
    else:
        calificacion = Calificacion(
            organizacion_id=user.organizacion_id,
            **data.model_dump(),
        )
        db.add(calificacion)

    db.commit()
    db.refresh(calificacion)
    return calificacion


@router.get("/boletas/{alumno_id}", response_model=BoletaOut)
def obtener_boleta(
    alumno_id: int,
    periodo: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    alumno = _propio_o_404(db, Alumno, alumno_id, user)
    grupo = _propio_o_404(db, GrupoEscolar, alumno.grupo_id, user)
    materias = (
        db.query(Materia)
        .filter(Materia.organizacion_id == user.organizacion_id)
        .order_by(Materia.nombre.asc())
        .all()
    )
    registros = (
        db.query(Calificacion)
        .filter(
            Calificacion.organizacion_id == user.organizacion_id,
            Calificacion.alumno_id == alumno.id,
            Calificacion.periodo == periodo,
        )
        .all()
    )
    valores = {registro.materia_id: registro.valor for registro in registros}
    calificaciones = [
        MateriaCalificacionOut(
            materia_id=materia.id,
            materia=materia.nombre,
            valor=valores.get(materia.id),
        )
        for materia in materias
    ]
    capturadas = [item.valor for item in calificaciones if item.valor is not None]
    promedio = round(sum(capturadas) / len(capturadas), 2) if capturadas else None

    return BoletaOut(
        alumno_id=alumno.id,
        matricula=alumno.matricula,
        alumno=alumno.nombre_completo,
        grupo=grupo.nombre,
        ciclo_escolar=grupo.ciclo_escolar,
        periodo=periodo,
        calificaciones=calificaciones,
        promedio=promedio,
    )


def _constancia_o_404(
    db: Session,
    constancia_id: int,
    user: Usuario,
) -> SolicitudConstancia:
    return _propio_o_404(db, SolicitudConstancia, constancia_id, user)


def _exigir_rol_autorizador(user: Usuario) -> None:
    roles = {"admin", "director", "direccion", "control_escolar"}
    if user.rol.lower() not in roles:
        raise HTTPException(
            status_code=403,
            detail="Se requiere autorización de Dirección o Control Escolar",
        )


@router.post(
    "/constancias",
    response_model=ConstanciaOut,
    status_code=status.HTTP_201_CREATED,
)
def solicitar_constancia(
    data: ConstanciaCreate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    _propio_o_404(db, Alumno, data.alumno_id, user)
    consecutivo = (
        db.query(SolicitudConstancia)
        .filter(SolicitudConstancia.organizacion_id == user.organizacion_id)
        .count()
        + 1
    )
    requiere_original = data.medio_entrega in {"recoger_original", "ambos"}
    estado_pago = "EXENTO" if data.monto == 0 else "PENDIENTE"
    estado = "SOLICITADA" if estado_pago == "EXENTO" else "PAGO_PENDIENTE"
    solicitud = SolicitudConstancia(
        organizacion_id=user.organizacion_id,
        folio=construir_folio(user.organizacion_id, consecutivo),
        token_verificacion=nuevo_token_verificacion(),
        requiere_original=requiere_original,
        estado_pago=estado_pago,
        estado=estado,
        **data.model_dump(),
    )
    db.add(solicitud)
    db.commit()
    db.refresh(solicitud)
    return solicitud


@router.get("/constancias", response_model=list[ConstanciaOut])
def listar_constancias(
    estado: str | None = Query(default=None),
    alumno_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    query = db.query(SolicitudConstancia).filter(
        SolicitudConstancia.organizacion_id == user.organizacion_id
    )
    if estado:
        query = query.filter(SolicitudConstancia.estado == estado.upper())
    if alumno_id is not None:
        query = query.filter(SolicitudConstancia.alumno_id == alumno_id)
    return query.order_by(SolicitudConstancia.created_at.desc()).all()


@router.get("/constancias/{constancia_id}", response_model=ConstanciaOut)
def obtener_constancia(
    constancia_id: int,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    return _constancia_o_404(db, constancia_id, user)


@router.patch("/constancias/{constancia_id}/pago", response_model=ConstanciaOut)
def actualizar_pago_constancia(
    constancia_id: int,
    data: PagoConstanciaUpdate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    solicitud = _constancia_o_404(db, constancia_id, user)
    if solicitud.estado in {"AUTORIZADA", "LISTA_PARA_RECOGER", "ENTREGADA"}:
        raise HTTPException(status_code=409, detail="El documento ya fue autorizado")
    solicitud.estado_pago = data.estado_pago
    solicitud.referencia_pago = data.referencia_pago
    if data.estado_pago in {"PAGADO", "EXENTO"} and solicitud.estado == "PAGO_PENDIENTE":
        validar_transicion(solicitud.estado, "SOLICITADA")
        solicitud.estado = "SOLICITADA"
    db.commit()
    db.refresh(solicitud)
    return solicitud


@router.post("/constancias/{constancia_id}/revisar", response_model=ConstanciaOut)
def revisar_constancia(
    constancia_id: int,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    solicitud = _constancia_o_404(db, constancia_id, user)
    if solicitud.estado_pago not in {"PAGADO", "EXENTO"}:
        raise HTTPException(status_code=409, detail="El pago todavía no está validado")
    validar_transicion(solicitud.estado, "EN_REVISION")
    solicitud.estado = "EN_REVISION"
    solicitud.revisado_por_id = user.id
    solicitud.revisado_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(solicitud)
    return solicitud


@router.post("/constancias/{constancia_id}/autorizar", response_model=ConstanciaOut)
def autorizar_constancia(
    constancia_id: int,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    _exigir_rol_autorizador(user)
    solicitud = _constancia_o_404(db, constancia_id, user)
    validar_transicion(solicitud.estado, "AUTORIZADA")
    solicitud.estado = "AUTORIZADA"
    solicitud.autorizado_por_id = user.id
    solicitud.autorizado_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(solicitud)
    return solicitud


@router.post("/constancias/{constancia_id}/lista-recoger", response_model=ConstanciaOut)
def marcar_lista_para_recoger(
    constancia_id: int,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    solicitud = _constancia_o_404(db, constancia_id, user)
    if not solicitud.requiere_original:
        raise HTTPException(status_code=409, detail="La solicitud no requiere original")
    validar_transicion(solicitud.estado, "LISTA_PARA_RECOGER")
    solicitud.estado = "LISTA_PARA_RECOGER"
    db.commit()
    db.refresh(solicitud)
    return solicitud


@router.post("/constancias/{constancia_id}/entregar", response_model=ConstanciaOut)
def entregar_constancia(
    constancia_id: int,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    solicitud = _constancia_o_404(db, constancia_id, user)
    validar_transicion(solicitud.estado, "ENTREGADA")
    solicitud.estado = "ENTREGADA"
    solicitud.entregado_por_id = user.id
    solicitud.entregado_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(solicitud)
    return solicitud


@router.post("/constancias/{constancia_id}/cancelar", response_model=ConstanciaOut)
def cancelar_constancia(
    constancia_id: int,
    motivo: str = Query(..., min_length=3),
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    solicitud = _constancia_o_404(db, constancia_id, user)
    validar_transicion(solicitud.estado, "CANCELADA")
    solicitud.estado = "CANCELADA"
    solicitud.observaciones = motivo
    db.commit()
    db.refresh(solicitud)
    return solicitud


@router.get(
    "/verificar/{token}",
    response_class=HTMLResponse,
    tags=["Verificación pública"],
)
def verificar_constancia(token: str, db: Session = Depends(get_db)):
    datos = _datos_verificacion(token, db)
    fecha = datos.fecha_emision.strftime("%d/%m/%Y")
    estado = datos.estado.replace("_", " ").title()
    cct = f" · CCT {escape(datos.cct)}" if datos.cct else ""
    return HTMLResponse(
        f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
        <meta name="viewport" content="width=device-width,initial-scale=1">
        <title>Documento válido · {escape(datos.folio)}</title><style>
        *{{box-sizing:border-box}}body{{margin:0;min-height:100vh;display:grid;place-items:center;padding:22px;
        font-family:Arial,sans-serif;background:linear-gradient(145deg,#061221,#102b46);color:#eaf4ff}}
        .card{{width:min(620px,100%);background:#0b1b2d;border:1px solid #284767;border-radius:22px;
        padding:30px;box-shadow:0 22px 60px #0007}}.check{{width:72px;height:72px;margin:0 auto 18px;
        display:grid;place-items:center;border-radius:50%;background:#16834b;font-size:40px;font-weight:bold}}
        h1{{text-align:center;margin:0 0 8px;font-size:28px}}.school{{text-align:center;color:#9dc5e8;margin-bottom:26px}}
        .data{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}.item{{padding:14px;border-radius:12px;
        background:#071522;border:1px solid #1d3852}}.item.full{{grid-column:1/-1}}.label{{display:block;color:#83a9cb;
        font-size:12px;text-transform:uppercase;letter-spacing:.7px;margin-bottom:5px}}.value{{font-weight:700}}
        .privacy{{margin:22px 0 0;padding-top:18px;border-top:1px solid #26425e;color:#91a9bf;font-size:12px;line-height:1.5}}
        .brand{{text-align:center;margin-top:18px;color:#6e91b0;font-size:12px}}@media(max-width:520px){{.card{{padding:22px}}.data{{grid-template-columns:1fr}}.item.full{{grid-column:auto}}}}
        </style></head><body><main class="card"><div class="check">✓</div><h1>Documento válido</h1>
        <div class="school">{escape(datos.escuela)}{cct}</div><section class="data">
        <div class="item full"><span class="label">Folio</span><span class="value">{escape(datos.folio)}</span></div>
        <div class="item"><span class="label">Documento</span><span class="value">Constancia de estudios</span></div>
        <div class="item"><span class="label">Estado</span><span class="value">{escape(estado)}</span></div>
        <div class="item full"><span class="label">Alumno</span><span class="value">{escape(datos.alumno)}</span></div>
        <div class="item"><span class="label">Matrícula</span><span class="value">{escape(datos.matricula)}</span></div>
        <div class="item"><span class="label">Grupo</span><span class="value">{escape(datos.grupo)}</span></div>
        <div class="item"><span class="label">Ciclo escolar</span><span class="value">{escape(datos.ciclo_escolar)}</span></div>
        <div class="item"><span class="label">Fecha de emisión</span><span class="value">{fecha}</span></div>
        </section><p class="privacy">Por seguridad, el nombre y la matrícula se muestran parcialmente ocultos.
        La validez corresponde al folio registrado por la institución emisora.</p><div class="brand">Verificado con MEXA Escolar</div>
        </main></body></html>"""
    )


def _datos_verificacion(
    token: str,
    db: Session,
) -> VerificacionConstanciaOut:
    solicitud = (
        db.query(SolicitudConstancia)
        .filter(SolicitudConstancia.token_verificacion == token)
        .first()
    )
    if not solicitud or solicitud.estado == "CANCELADA":
        raise HTTPException(status_code=404, detail="Constancia no válida")
    if solicitud.estado not in {"AUTORIZADA", "LISTA_PARA_RECOGER", "ENTREGADA"}:
        raise HTTPException(status_code=409, detail="Constancia todavía no emitida")
    alumno = solicitud.alumno
    return VerificacionConstanciaOut(
        valida=True,
        folio=solicitud.folio,
        escuela=solicitud.organizacion.nombre,
        cct=solicitud.organizacion.cct,
        tipo=solicitud.tipo,
        alumno=nombre_protegido(alumno.nombre_completo),
        matricula=f"***{alumno.matricula[-4:]}",
        grupo=alumno.grupo.nombre,
        ciclo_escolar=alumno.grupo.ciclo_escolar,
        fecha_emision=solicitud.autorizado_at,
        estado=solicitud.estado,
    )


@router.get(
    "/verificar/{token}/datos",
    response_model=VerificacionConstanciaOut,
    tags=["Verificación pública"],
)
def datos_verificacion_constancia(token: str, db: Session = Depends(get_db)):
    return _datos_verificacion(token, db)


@router.get("/verificar/{token}/qr.png", include_in_schema=False)
def qr_constancia(token: str, request: Request, db: Session = Depends(get_db)):
    solicitud = (
        db.query(SolicitudConstancia)
        .filter(SolicitudConstancia.token_verificacion == token)
        .first()
    )
    if not solicitud:
        raise HTTPException(status_code=404, detail="Constancia no encontrada")
    url = str(request.url_for("verificar_constancia", token=token))
    imagen = qrcode.make(url)
    salida = BytesIO()
    imagen.save(salida, format="PNG")
    salida.seek(0)
    return StreamingResponse(salida, media_type="image/png")


@router.get(
    "/constancias/{constancia_id}/documento",
    response_class=HTMLResponse,
    include_in_schema=False,
)
def documento_constancia(
    constancia_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    solicitud = _constancia_o_404(db, constancia_id, user)
    if solicitud.estado not in {"AUTORIZADA", "LISTA_PARA_RECOGER", "ENTREGADA"}:
        raise HTTPException(status_code=409, detail="La constancia aún no está autorizada")
    alumno = solicitud.alumno
    grupo = alumno.grupo
    organizacion = solicitud.organizacion
    color_primario = (
        organizacion.color_primario
        if organizacion.color_primario
        and re.fullmatch(r"#[0-9A-Fa-f]{6}", organizacion.color_primario)
        else "#1e3a5f"
    )
    autorizador = solicitud.autorizado_por.nombre if solicitud.autorizado_por else "Dirección"
    firmante = organizacion.firmante_nombre or autorizador
    firmante_cargo = organizacion.firmante_cargo or "Persona autorizada"
    cct = f"CCT: {escape(organizacion.cct)}" if organizacion.cct else ""
    domicilio = escape(organizacion.domicilio) if organizacion.domicilio else ""
    contacto = " · ".join(
        escape(valor)
        for valor in [organizacion.telefono, organizacion.correo_institucional]
        if valor
    )
    logo = (
        f'<img class="logo" src="{escape(organizacion.logo_url)}" alt="Logotipo institucional">'
        if organizacion.logo_url
        else ""
    )
    qr_url = request.url_for("qr_constancia", token=solicitud.token_verificacion)
    verificar_url = request.url_for(
        "verificar_constancia", token=solicitud.token_verificacion
    )
    fecha = solicitud.autorizado_at.strftime("%d/%m/%Y")
    motivo = f" para {escape(solicitud.motivo)}" if solicitud.motivo else ""
    whatsapp = ""
    if alumno.telefono_tutor:
        mensaje = quote(
            f"La constancia {solicitud.folio} de {alumno.nombre_completo} "
            f"fue emitida por {organizacion.nombre}. Verificación: {verificar_url}"
        )
        whatsapp = (
            f'<a class="no-print" href="https://wa.me/{escape(alumno.telefono_tutor)}'
            f'?text={mensaje}" target="_blank">Preparar mensaje por WhatsApp</a>'
        )
    return HTMLResponse(
        f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
        <meta name="viewport" content="width=device-width,initial-scale=1">
        <title>{escape(solicitud.folio)}</title><style>
        body{{font-family:Georgia,serif;color:#172033;margin:0;background:#eef2f7}}
        .hoja{{max-width:760px;margin:28px auto;background:white;padding:64px;box-shadow:0 8px 30px #0002}}
        .membrete{{text-align:center;border-bottom:2px solid {color_primario};padding-bottom:18px;margin-bottom:28px}}
        .logo{{display:block;max-width:110px;max-height:90px;object-fit:contain;margin:0 auto 10px}}
        .datos-institucion{{font:12px Arial,sans-serif;color:#526277;line-height:1.5}}
        h1{{text-align:center;font-size:24px;letter-spacing:2px}} .escuela{{text-align:center;font-size:20px;font-weight:bold}}
        p{{font-size:17px;line-height:1.8;text-align:justify}} .firma{{margin-top:72px;text-align:center}}
        .firma-linea{{border-top:1px solid #222;max-width:360px;margin:auto;padding-top:8px}}
        .pie{{display:flex;gap:20px;align-items:end;margin-top:50px;font:12px Arial,sans-serif}}
        .pie img{{width:115px;height:115px}} .folio{{font:13px Arial,sans-serif;color:#475569}}
        .no-print{{display:block;max-width:760px;margin:18px auto;padding:13px;text-align:center;background:#16a34a;color:white;text-decoration:none;border-radius:9px;font:600 14px Arial}}
        @media print{{body{{background:white}}.hoja{{margin:0;box-shadow:none;max-width:none}}.no-print{{display:none}}}}
        @media(max-width:700px){{.hoja{{margin:0;padding:32px 22px}}}}
        </style></head><body>
        <button class="no-print" onclick="window.print()">Imprimir o guardar como PDF</button>
        {whatsapp}
        <main class="hoja"><header class="membrete">{logo}<div class="escuela">{escape(organizacion.nombre)}</div>
        <div class="datos-institucion">{cct}<br>{domicilio}<br>{contacto}</div></header>
        <h1>CONSTANCIA DE ESTUDIOS</h1>
        <p>A QUIEN CORRESPONDA:</p>
        <p>Por medio de la presente se hace constar que <strong>{escape(alumno.nombre_completo)}</strong>,
        con matrícula <strong>{escape(alumno.matricula)}</strong>, se encuentra inscrito(a) en el grupo
        <strong>{escape(grupo.nombre)}</strong>, grado <strong>{escape(grupo.grado or grupo.nombre)}</strong>,
        durante el ciclo escolar <strong>{escape(grupo.ciclo_escolar)}</strong>.</p>
        <p>Se extiende la presente{motivo} a petición de la persona interesada, el {fecha}.</p>
        <div class="firma"><div class="firma-linea"><strong>{escape(firmante)}</strong><br>{escape(firmante_cargo)}</div></div>
        <div class="pie"><img src="{qr_url}" alt="QR de verificación"><div>
        <div class="folio"><strong>Folio:</strong> {escape(solicitud.folio)}</div>
        <div class="folio">Documento verificable en:<br>{escape(str(verificar_url))}</div>
        <div class="folio">Este documento fue autorizado dentro de MEXA; no representa por sí mismo una firma electrónica avanzada.</div>
        </div></div></main></body></html>"""
    )
