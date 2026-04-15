from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.usuario import Usuario
from app.models.organizacion import Organizacion
from app.schemas.usuario import UsuarioCreate, UsuarioOut
from app.core.security import hash_password
from app.core.deps import get_current_user, require_admin

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.post("/", response_model=UsuarioOut)
def crear_usuario(
    data: UsuarioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    if data.rol not in ["admin", "usuario"]:
        raise HTTPException(status_code=400, detail="Rol inválido")

    organizacion = db.query(Organizacion).filter(
        Organizacion.id == data.organizacion_id
    ).first()

    if not organizacion:
        raise HTTPException(status_code=404, detail="Organización no encontrada")

    usuario_existente = db.query(Usuario).filter(Usuario.email == data.email).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    nuevo_usuario = Usuario(
        organizacion_id=data.organizacion_id,
        nombre=data.nombre,
        email=data.email,
        hashed_password=hash_password(data.password),
        rol=data.rol,
        activo="si"
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return nuevo_usuario


@router.get("/", response_model=List[UsuarioOut])
def listar_usuarios(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    usuarios = db.query(Usuario).filter(
        Usuario.organizacion_id == current_user.organizacion_id
    ).order_by(Usuario.id.desc()).all()

    return usuarios


@router.get("/{usuario_id}", response_model=UsuarioOut)
def obtener_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    usuario = db.query(Usuario).filter(
        Usuario.id == usuario_id,
        Usuario.organizacion_id == current_user.organizacion_id
    ).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return usuario
