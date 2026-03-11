from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.producto import Producto
from app.models.organizacion import Organizacion
from app.schemas.producto import ProductoCreate, ProductoOut

router = APIRouter(prefix="/productos", tags=["Productos"])


@router.post("/", response_model=ProductoOut)
def crear_producto(payload: ProductoCreate, db: Session = Depends(get_db)):
    # 1) Validar que exista la organización
    org = db.query(Organizacion).filter(
        Organizacion.id == payload.organizacion_id
    ).first()

    if not org:
        raise HTTPException(status_code=404, detail="Organización no existe")

    # 2) Crear producto
    producto = Producto(
        organizacion_id=payload.organizacion_id,
        nombre=payload.nombre,
        codigo=payload.codigo,
        tipo=payload.tipo,
        cantidad=payload.cantidad,
        ubicacion=payload.ubicacion,
        precio=payload.precio,
    )

    db.add(producto)
    db.commit()
    db.refresh(producto)

    return producto

@router.get("/", response_model=list[ProductoOut])
def listar_productos(db: Session = Depends(get_db)):
    productos = db.query(Producto).order_by(Producto.id.desc()).all()
    return productos
