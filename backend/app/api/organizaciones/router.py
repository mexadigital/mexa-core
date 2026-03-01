from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.organizacion import Organizacion
from app.schemas.organizacion import OrganizacionCreate, OrganizacionOut

router = APIRouter(prefix="/organizaciones", tags=["Organizaciones"])


@router.post("/", response_model=OrganizacionOut)
def crear_organizacion(payload: OrganizacionCreate, db: Session = Depends(get_db)):
    org = Organizacion(nombre=payload.nombre, rfc=payload.rfc, plan=payload.plan)
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


@router.get("/", response_model=list[OrganizacionOut])
def listar_organizaciones(db: Session = Depends(get_db)):
    return db.query(Organizacion).order_by(Organizacion.id.desc()).all()


@router.get("/{org_id}", response_model=OrganizacionOut)
def obtener_organizacion(org_id: int, db: Session = Depends(get_db)):
    org = db.query(Organizacion).filter(Organizacion.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organización no encontrada")
    return org
