from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.inventario import Inventario
from app.core.deps import get_current_user
from app.schemas.inventario import InventarioOut

router = APIRouter(prefix="/inventario", tags=["Inventario"])


@router.get("/", response_model=list[InventarioOut])
def obtener_inventario(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    organizacion_id = current_user["organizacion_id"]

    inventario = (
        db.query(Inventario)
        .filter(Inventario.organizacion_id == organizacion_id)
        .all()
    )

    return inventario
