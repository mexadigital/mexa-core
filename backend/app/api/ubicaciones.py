from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.ubicacion import Ubicacion
from app.schemas.ubicacion import UbicacionCreate, UbicacionUpdate, UbicacionOut
from app.core.deps import get_current_user

router = APIRouter(prefix="/ubicaciones", tags=["Ubicaciones"])


@router.post("/", response_model=UbicacionOut, status_code=status.HTTP_201_CREATED)
def crear_ubicacion(
    data: UbicacionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    organizacion_id = current_user["organizacion_id"]

    if data.tipo not in ["tienda", "almacen"]:
        raise HTTPException(status_code=400, detail="Tipo inválido. Usa 'tienda' o 'almacen'")

    existente = (
        db.query(Ubicacion)
        .filter(
            Ubicacion.organizacion_id == organizacion_id,
            Ubicacion.nombre == data.nombre
        )
        .first()
    )

    if existente:
        raise HTTPException(status_code=400, detail="Ya existe una ubicación con ese nombre")

    ubicacion = Ubicacion(
        organizacion_id=organizacion_id,
        nombre=data.nombre,
        tipo=data.tipo,
        activo=data.activo if data.activo is not None else True
    )

    db.add(ubicacion)
    db.commit()
    db.refresh(ubicacion)

    return ubicacion


@router.get("/", response_model=list[UbicacionOut])
def listar_ubicaciones(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    organizacion_id = current_user["organizacion_id"]

    ubicaciones = (
        db.query(Ubicacion)
        .filter(Ubicacion.organizacion_id == organizacion_id)
        .order_by(Ubicacion.tipo.asc(), Ubicacion.nombre.asc())
        .all()
    )

    return ubicaciones


@router.get("/{ubicacion_id}", response_model=UbicacionOut)
def obtener_ubicacion(
    ubicacion_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    organizacion_id = current_user["organizacion_id"]

    ubicacion = (
        db.query(Ubicacion)
        .filter(
            Ubicacion.id == ubicacion_id,
            Ubicacion.organizacion_id == organizacion_id
        )
        .first()
    )

    if not ubicacion:
        raise HTTPException(status_code=404, detail="Ubicación no encontrada")

    return ubicacion


@router.put("/{ubicacion_id}", response_model=UbicacionOut)
def actualizar_ubicacion(
    ubicacion_id: int,
    data: UbicacionUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    organizacion_id = current_user["organizacion_id"]

    ubicacion = (
        db.query(Ubicacion)
        .filter(
            Ubicacion.id == ubicacion_id,
            Ubicacion.organizacion_id == organizacion_id
        )
        .first()
    )

    if not ubicacion:
        raise HTTPException(status_code=404, detail="Ubicación no encontrada")

    if data.tipo is not None and data.tipo not in ["tienda", "almacen"]:
        raise HTTPException(status_code=400, detail="Tipo inválido. Usa 'tienda' o 'almacen'")

    nuevo_nombre = data.nombre if data.nombre is not None else ubicacion.nombre

    existe_otra = (
        db.query(Ubicacion)
        .filter(
            Ubicacion.organizacion_id == organizacion_id,
            Ubicacion.nombre == nuevo_nombre,
            Ubicacion.id != ubicacion_id
        )
        .first()
    )

    if existe_otra:
        raise HTTPException(status_code=400, detail="Ya existe otra ubicación con ese nombre")

    if data.nombre is not None:
        ubicacion.nombre = data.nombre

    if data.tipo is not None:
        ubicacion.tipo = data.tipo

    if data.activo is not None:
        ubicacion.activo = data.activo

    db.commit()
    db.refresh(ubicacion)

    return ubicacion


@router.delete("/{ubicacion_id}")
def desactivar_ubicacion(
    ubicacion_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    organizacion_id = current_user["organizacion_id"]

    ubicacion = (
        db.query(Ubicacion)
        .filter(
            Ubicacion.id == ubicacion_id,
            Ubicacion.organizacion_id == organizacion_id
        )
        .first()
    )

    if not ubicacion:
        raise HTTPException(status_code=404, detail="Ubicación no encontrada")

    ubicacion.activo = False
    db.commit()

    return {"message": "Ubicación desactivada correctamente"}
