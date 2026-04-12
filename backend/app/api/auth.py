from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password, verify_password, create_access_token
from app.db.database import get_db
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioLogin, UsuarioOut, Token

router = APIRouter(prefix="/auth", tags=["Auth"])
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    token = credentials.credentials

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autenticado",
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        email: Optional[str] = payload.get("sub")
        user_id: Optional[int] = payload.get("user_id")
        organizacion_id: Optional[int] = payload.get("organizacion_id")

        if email is None or user_id is None or organizacion_id is None:
            raise credentials_exception

        return {
            "email": email,
            "user_id": user_id,
            "organizacion_id": organizacion_id,
        }

    except JWTError:
        raise credentials_exception


@router.post("/register", response_model=UsuarioOut)
def register(data: UsuarioCreate, db: Session = Depends(get_db)):
    usuario_existente = db.query(Usuario).filter(Usuario.email == data.email).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    nuevo_usuario = Usuario(
        organizacion_id=data.organizacion_id,
        nombre=data.nombre,
        email=data.email,
        hashed_password=hash_password(data.password),
        activo="si"
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return nuevo_usuario


@router.post("/login", response_model=Token)
def login(data: UsuarioLogin, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == data.email).first()

    if not usuario:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    if not verify_password(data.password, usuario.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    token = create_access_token(
        {
            "sub": usuario.email,
            "user_id": usuario.id,
            "organizacion_id": usuario.organizacion_id
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }
