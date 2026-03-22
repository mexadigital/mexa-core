from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.producto import Producto
from app.models.organizacion import Organizacion
from app.schemas.producto import ProductoCreate, ProductoOut
from app.core.deps import get_current_user

router = APIRouter(prefix="/productos", tags=["Productos"])


# =========================
# Crear producto
# =========================
@router.post("/", response_model=ProductoOut)
def crear_producto(
    payload: ProductoCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    org = db.query(Organizacion).filter(
        Organizacion.id == user["organizacion_id"]
    ).first()

    if not org:
        raise HTTPException(status_code=404, detail="Organización no existe")

    producto = Producto(
        organizacion_id=user["organizacion_id"],
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


# =========================
# Listar productos
# =========================
@router.get("/", response_model=list[ProductoOut])
def listar_productos(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    productos = db.query(Producto).filter(
        Producto.organizacion_id == user["organizacion_id"]
    ).order_by(Producto.id.desc()).all()

    return productos


# =========================
# Obtener producto por ID
# =========================
@router.get("/{producto_id}", response_model=ProductoOut)
def obtener_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    producto = db.query(Producto).filter(
        Producto.id == producto_id,
        Producto.organizacion_id == user["organizacion_id"]
    ).first()

    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    return producto
