from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.ubicacion import Ubicacion
from app.models.usuario import Usuario
from app.schemas.ubicacion import UbicacionCreate, UbicacionOut
from app.core.deps import get_current_user, require_admin

router = APIRouter(prefix="/ubicaciones", tags=["Ubicaciones"])


@router.post("/", response_model=UbicacionOut)
def crear_ubicacion(
    data: UbicacionCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    if current_user.rol != "superadmin":
        if data.organizacion_id != current_user.organizacion_id:
            raise HTTPException(
                status_code=403,
                detail="Solo puedes crear ubicaciones en tu organización"
            )

    nueva = Ubicacion(
        organizacion_id=data.organizacion_id,
        nombre=data.nombre,
        tipo=data.tipo,
        activo=True
    )

    db.add(nueva)
    db.commit()
    db.refresh(nueva)

    return nueva


@router.get("/", response_model=List[UbicacionOut])
def listar_ubicaciones(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if current_user.rol == "superadmin":
        ubicaciones = db.query(Ubicacion).order_by(Ubicacion.id.desc()).all()
    else:
        ubicaciones = (
            db.query(Ubicacion)
            .filter(Ubicacion.organizacion_id == current_user.organizacion_id)
            .order_by(Ubicacion.id.desc())
            .all()
        )

    return ubicaciones


@router.get("/{ubicacion_id}", response_model=UbicacionOut)
def obtener_ubicacion(
    ubicacion_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    ubicacion = db.query(Ubicacion).filter(Ubicacion.id == ubicacion_id).first()

    if not ubicacion:
        raise HTTPException(status_code=404, detail="Ubicación no encontrada")

    if current_user.rol != "superadmin":
        if ubicacion.organizacion_id != current_user.organizacion_id:
            raise HTTPException(status_code=403, detail="No puedes ver esta ubicación")

    return ubicacion
