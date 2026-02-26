from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Consumable, ModoSerie, EPP

router = APIRouter(prefix="/consumables", tags=["consumables"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# SCHEMAS
# =========================

class ConsumableCreate(BaseModel):
    name: str
    epp_id: int
    modo_serie: ModoSerie = ModoSerie.NINGUNA


class ConsumableOut(BaseModel):
    id: int
    name: str
    epp_id: int
    modo_serie: ModoSerie

    class Config:
        from_attributes = True


# =========================
# ROUTES
# =========================

@router.get("", response_model=list[ConsumableOut])
def list_consumables(db: Session = Depends(get_db)):
    return db.query(Consumable).all()


@router.post("", response_model=ConsumableOut)
def create_consumable(payload: ConsumableCreate, db: Session = Depends(get_db)):

    # Validar que el EPP exista
    epp = db.query(EPP).filter(EPP.id == payload.epp_id).first()
    if not epp:
        raise HTTPException(status_code=400, detail="EPP no existe")

    new_consumable = Consumable(
        name=payload.name,
        epp_id=payload.epp_id,
        modo_serie=payload.modo_serie
    )

    db.add(new_consumable)
    db.commit()
    db.refresh(new_consumable)

    return new_consumable


@router.get("/{consumable_id}", response_model=ConsumableOut)
def get_consumable(consumable_id: int, db: Session = Depends(get_db)):
    consumable = db.query(Consumable).filter(Consumable.id == consumable_id).first()
    if not consumable:
        raise HTTPException(status_code=404, detail="Not found")
    return consumable
