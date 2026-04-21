from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.producto import Producto
from app.models.usuario import Usuario
from app.schemas.producto import ProductoCreate, ProductoUpdate, ProductoOut
from app.api.auth import get_current_user

router = APIRouter(prefix="/productos", tags=["Productos"])


@router.post("/", response_model=ProductoOut, status_code=status.HTTP_201_CREATED)
def crear_producto(
    data: ProductoCreate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    # Validar código único dentro de la organización
    existente = (
        db.query(Producto)
        .filter(
            Producto.organizacion_id == user.organizacion_id,
            Producto.codigo == data.codigo,
        )
        .first()
    )

    if existente:
        raise HTTPException(
            status_code=400,
            detail="Ya existe un producto con ese código en tu organización",
        )

    nuevo_producto = Producto(
        organizacion_id=user.organizacion_id,
        nombre=data.nombre,
        codigo=data.codigo,
        tipo=data.tipo,
        cantidad=data.cantidad,
        ubicacion=data.ubicacion,
        precio=data.precio,
    )

    db.add(nuevo_producto)
    db.commit()
    db.refresh(nuevo_producto)
    return nuevo_producto


@router.get("/", response_model=list[ProductoOut])
def listar_productos(
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    productos = (
        db.query(Producto)
        .filter(Producto.organizacion_id == user.organizacion_id)
        .order_by(Producto.id.desc())
        .all()
    )
    return productos


@router.get("/{producto_id}", response_model=ProductoOut)
def obtener_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    producto = (
        db.query(Producto)
        .filter(
            Producto.id == producto_id,
            Producto.organizacion_id == user.organizacion_id,
        )
        .first()
    )

    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    return producto


@router.put("/{producto_id}", response_model=ProductoOut)
def actualizar_producto(
    producto_id: int,
    data: ProductoUpdate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    producto = (
        db.query(Producto)
        .filter(
            Producto.id == producto_id,
            Producto.organizacion_id == user.organizacion_id,
        )
        .first()
    )

    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # Si quieren cambiar el código, validar que no se repita en la organización
    if data.codigo and data.codigo != producto.codigo:
        existente = (
            db.query(Producto)
            .filter(
                Producto.organizacion_id == user.organizacion_id,
                Producto.codigo == data.codigo,
                Producto.id != producto_id,
            )
            .first()
        )
        if existente:
            raise HTTPException(
                status_code=400,
                detail="Ya existe otro producto con ese código en tu organización",
            )

    # Actualización parcial
    if data.nombre is not None:
        producto.nombre = data.nombre
    if data.codigo is not None:
        producto.codigo = data.codigo
    if data.tipo is not None:
        producto.tipo = data.tipo
    if data.cantidad is not None:
        producto.cantidad = data.cantidad
    if data.ubicacion is not None:
        producto.ubicacion = data.ubicacion
    if data.precio is not None:
        producto.precio = data.precio

    db.commit()
    db.refresh(producto)
    return producto


@router.delete("/{producto_id}")
def eliminar_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    producto = (
        db.query(Producto)
        .filter(
            Producto.id == producto_id,
            Producto.organizacion_id == user.organizacion_id,
        )
        .first()
    )

    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    db.delete(producto)
    db.commit()

    return {"message": "Producto eliminado correctamente"}
