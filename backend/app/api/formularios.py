from datetime import date, datetime, timezone
from html import escape

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session, selectinload

from app.core.deps import get_current_user
from app.db.database import get_db
from app.models.formulario import (
    CampoFormulario,
    Formulario,
    RegistroFormulario,
    ValorRegistro,
)
from app.models.usuario import Usuario
from app.schemas.formulario import (
    CampoCreate,
    CampoOut,
    FormularioCreate,
    FormularioOut,
    RegistroCreate,
    RegistroOut,
    ValorOut,
)


router = APIRouter(prefix="/formularios", tags=["MEXA Formularios"])


def _formulario_propio(db: Session, formulario_id: int, user: Usuario) -> Formulario:
    formulario = (
        db.query(Formulario)
        .options(selectinload(Formulario.campos))
        .filter(
            Formulario.id == formulario_id,
            Formulario.organizacion_id == user.organizacion_id,
        )
        .first()
    )
    if not formulario:
        raise HTTPException(status_code=404, detail="Formulario no encontrado")
    return formulario


def _registro_salida(registro: RegistroFormulario) -> RegistroOut:
    valores_por_campo = {item.campo_id: item.valor for item in registro.valores}
    return RegistroOut(
        id=registro.id,
        formulario_id=registro.formulario_id,
        formulario=registro.formulario.nombre,
        folio=registro.folio,
        estado=registro.estado,
        created_at=registro.created_at,
        valores=[
            ValorOut(
                campo_id=campo.id,
                clave=campo.clave,
                etiqueta=campo.etiqueta,
                valor=valores_por_campo.get(campo.id),
            )
            for campo in registro.formulario.campos
        ],
    )


def _registro_propio(db: Session, registro_id: int, user: Usuario) -> RegistroFormulario:
    registro = (
        db.query(RegistroFormulario)
        .options(
            selectinload(RegistroFormulario.valores),
            selectinload(RegistroFormulario.formulario).selectinload(Formulario.campos),
        )
        .filter(
            RegistroFormulario.id == registro_id,
            RegistroFormulario.organizacion_id == user.organizacion_id,
        )
        .first()
    )
    if not registro:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    return registro


def _validar_valor(campo: CampoFormulario, valor: str | None) -> str | None:
    """Valida el texto según el tipo configurado y conserva el original limpio."""

    if valor is None:
        return None
    valor = valor.strip()
    if not valor:
        return None

    if campo.tipo == "numero":
        try:
            float(valor)
        except ValueError as exc:
            raise HTTPException(
                status_code=400,
                detail=f"{campo.etiqueta} debe ser un número",
            ) from exc
    elif campo.tipo == "fecha":
        try:
            date.fromisoformat(valor)
        except ValueError as exc:
            raise HTTPException(
                status_code=400,
                detail=f"{campo.etiqueta} debe ser una fecha válida",
            ) from exc
    elif campo.tipo == "seleccion":
        opciones = [item.strip() for item in (campo.opciones or "").split(",") if item.strip()]
        if valor not in opciones:
            raise HTTPException(
                status_code=400,
                detail=f"{campo.etiqueta} contiene una opción inválida",
            )

    return valor


@router.post("/", response_model=FormularioOut, status_code=status.HTTP_201_CREATED)
def crear_formulario(
    data: FormularioCreate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    existente = (
        db.query(Formulario)
        .filter(
            Formulario.organizacion_id == user.organizacion_id,
            Formulario.nombre == data.nombre,
        )
        .first()
    )
    if existente:
        raise HTTPException(status_code=400, detail="Ya existe un formulario con ese nombre")

    formulario = Formulario(organizacion_id=user.organizacion_id, **data.model_dump())
    db.add(formulario)
    db.commit()
    db.refresh(formulario)
    return formulario


@router.get("/", response_model=list[FormularioOut])
def listar_formularios(
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    return (
        db.query(Formulario)
        .options(selectinload(Formulario.campos))
        .filter(Formulario.organizacion_id == user.organizacion_id)
        .order_by(Formulario.nombre.asc())
        .all()
    )


@router.get("/{formulario_id}", response_model=FormularioOut)
def obtener_formulario(
    formulario_id: int,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    return _formulario_propio(db, formulario_id, user)


@router.post(
    "/{formulario_id}/campos",
    response_model=CampoOut,
    status_code=status.HTTP_201_CREATED,
)
def agregar_campo(
    formulario_id: int,
    data: CampoCreate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    formulario = _formulario_propio(db, formulario_id, user)
    if any(campo.clave == data.clave for campo in formulario.campos):
        raise HTTPException(status_code=400, detail="La clave ya existe en el formulario")

    campo = CampoFormulario(formulario_id=formulario.id, **data.model_dump())
    db.add(campo)
    db.commit()
    db.refresh(campo)
    return campo


@router.post(
    "/{formulario_id}/registros",
    response_model=RegistroOut,
    status_code=status.HTTP_201_CREATED,
)
def crear_registro(
    formulario_id: int,
    data: RegistroCreate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    formulario = _formulario_propio(db, formulario_id, user)
    campos = {campo.id: campo for campo in formulario.campos}
    entradas = {entrada.campo_id: entrada.valor for entrada in data.valores}

    desconocidos = set(entradas) - set(campos)
    if desconocidos:
        raise HTTPException(status_code=400, detail="Hay campos que no pertenecen al formulario")

    faltantes = [
        campo.etiqueta
        for campo in campos.values()
        if campo.obligatorio and not (entradas.get(campo.id) or "").strip()
    ]
    if faltantes:
        raise HTTPException(
            status_code=400,
            detail="Faltan campos obligatorios: " + ", ".join(faltantes),
        )

    entradas = {
        campo_id: _validar_valor(campos[campo_id], valor)
        for campo_id, valor in entradas.items()
    }

    registro = RegistroFormulario(
        organizacion_id=user.organizacion_id,
        formulario_id=formulario.id,
        creado_por_id=user.id,
        folio="PENDIENTE",
    )
    db.add(registro)
    db.flush()
    registro.folio = f"{datetime.now(timezone.utc):%Y%m%d}-{registro.id:06d}"

    for campo in formulario.campos:
        db.add(
            ValorRegistro(
                registro_id=registro.id,
                campo_id=campo.id,
                valor=entradas.get(campo.id),
            )
        )

    db.commit()
    registro_guardado = _registro_propio(db, registro.id, user)
    return _registro_salida(registro_guardado)


@router.get("/{formulario_id}/registros", response_model=list[RegistroOut])
def listar_registros(
    formulario_id: int,
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    _formulario_propio(db, formulario_id, user)
    registros = (
        db.query(RegistroFormulario)
        .options(
            selectinload(RegistroFormulario.valores),
            selectinload(RegistroFormulario.formulario).selectinload(Formulario.campos),
        )
        .filter(
            RegistroFormulario.formulario_id == formulario_id,
            RegistroFormulario.organizacion_id == user.organizacion_id,
        )
        .order_by(RegistroFormulario.id.desc())
        .limit(limit)
        .all()
    )
    return [_registro_salida(registro) for registro in registros]


@router.get("/registros/{registro_id}/imprimir", response_class=HTMLResponse)
def imprimir_registro(
    registro_id: int,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    registro = _registro_propio(db, registro_id, user)
    filas = "".join(
        f"<tr><th>{escape(item.etiqueta)}</th><td>{escape(item.valor or '')}</td></tr>"
        for item in _registro_salida(registro).valores
    )
    return HTMLResponse(
        f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><title>{escape(registro.folio)}</title>
<style>
body{{font-family:Arial,sans-serif;max-width:800px;margin:36px auto;color:#111827}}
h1{{margin-bottom:4px}} .meta{{color:#64748b;margin-bottom:24px}}
table{{width:100%;border-collapse:collapse}} th,td{{border:1px solid #cbd5e1;padding:12px;text-align:left}}
th{{width:34%;background:#f1f5f9}} .actions{{margin:20px 0}} button{{padding:10px 16px}}
@media print{{.actions{{display:none}} body{{margin:0}}}}
</style></head><body>
<div class="actions"><button onclick="window.print()">Imprimir / Guardar PDF</button></div>
<h1>{escape(registro.formulario.nombre)}</h1>
<div class="meta">Folio {escape(registro.folio)} · {registro.created_at:%d/%m/%Y %H:%M}</div>
<table>{filas}</table>
</body></html>"""
    )
