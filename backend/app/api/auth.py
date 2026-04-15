from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.usuario import Usuario
from app.models.organizacion import Organizacion
from app.schemas.usuario import UsuarioCreate, UsuarioLogin, UsuarioOut, Token, UsuarioMe
from app.core.security import hash_password, verify_password, create_access_token
from app.core.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UsuarioOut)
def register(data: UsuarioCreate, db: Session = Depends(get_db)):
    usuario_existente = db.query(Usuario).filter(Usuario.email == data.email).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    organizacion = db.query(Organizacion).filter(
        Organizacion.id == data.organizacion_id
    ).first()
    if not organizacion:
        raise HTTPException(status_code=404, detail="Organización no encontrada")

    if data.rol not in ["superadmin", "admin", "usuario"]:
        raise HTTPException(status_code=400, detail="Rol inválido")

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


@router.post("/login", response_model=Token)
def login(data: UsuarioLogin, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == data.email).first()

    if not usuario or not verify_password(data.password, usuario.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    if usuario.activo != "si":
        raise HTTPException(status_code=403, detail="Usuario inactivo")

    organizacion = db.query(Organizacion).filter(
        Organizacion.id == usuario.organizacion_id
    ).first()

    if not organizacion:
        raise HTTPException(status_code=404, detail="Organización no encontrada")

    access_token = create_access_token(
        data={
            "sub": usuario.email,
            "user_id": usuario.id,
            "organizacion_id": usuario.organizacion_id,
            "rol": usuario.rol,
            "organizacion_tipo": organizacion.tipo
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UsuarioMe)
def me(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    organizacion = db.query(Organizacion).filter(
        Organizacion.id == current_user.organizacion_id
    ).first()

    if not organizacion:
        raise HTTPException(status_code=404, detail="Organización no encontrada")

    return UsuarioMe(
        id=current_user.id,
        organizacion_id=current_user.organizacion_id,
        nombre=current_user.nombre,
        email=current_user.email,
        rol=current_user.rol,
        activo=current_user.activo,
        organizacion_nombre=organizacion.nombre,
        organizacion_tipo=organizacion.tipo
    )
