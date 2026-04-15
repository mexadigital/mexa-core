from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.organizacion import Organizacion
from app.schemas.organizacion import OrganizacionCreate, OrganizacionOut
from app.core.deps import get_current_user
from app.models.usuario import Usuario

router = APIRouter(prefix="/organizaciones", tags=["Organizaciones"])


@router.post("/", response_model=OrganizacionOut)
def crear_organizacion(
    data: OrganizacionCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if current_user.rol != "admin":
        raise HTTPException(status_code=403, detail="Solo admin puede crear organizaciones")

    if data.tipo not in ["control", "retail"]:
        raise HTTPException(status_code=400, detail="Tipo inválido. Usa: control o retail")

    existente_nombre = db.query(Organizacion).filter(
        Organizacion.nombre == data.nombre
    ).first()
    if existente_nombre:
        raise HTTPException(status_code=400, detail="Ya existe una organización con ese nombre")

    existente_rfc = db.query(Organizacion).filter(
        Organizacion.rfc == data.rfc
    ).first()
    if existente_rfc:
        raise HTTPException(status_code=400, detail="Ya existe una organización con ese RFC")

    nueva = Organizacion(
        nombre=data.nombre,
        rfc=data.rfc,
        plan=data.plan,
        tipo=data.tipo
    )

    db.add(nueva)
    db.commit()
    db.refresh(nueva)

    return nueva


@router.get("/", response_model=List[OrganizacionOut])
def listar_organizaciones(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if current_user.rol != "admin":
        raise HTTPException(status_code=403, detail="Solo admin puede ver organizaciones")

    organizaciones = db.query(Organizacion).order_by(Organizacion.id.desc()).all()
    return organizaciones


@router.get("/{organizacion_id}", response_model=OrganizacionOut)
def obtener_organizacion(
    organizacion_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if current_user.rol != "admin":
        raise HTTPException(status_code=403, detail="Solo admin puede ver organizaciones")

    organizacion = db.query(Organizacion).filter(
        Organizacion.id == organizacion_id
    ).first()

    if not organizacion:
        raise HTTPException(status_code=404, detail="Organización no encontrada")

    return organizacion
