from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import engine, get_db
from app.db.base import Base

# Registrar modelos
import app.models  # noqa: F401

from app.models.producto import Producto
from app.models.usuario import Usuario
from app.schemas.producto import ProductoCreate, ProductoOut
from app.api.auth import get_current_user

# Routers
from app.api.auth import router as auth_router
from app.api.organizaciones.router import router as organizaciones_router
from app.api.productos import router as productos_router
from app.api.movimientos.router.router import router as movimientos_router
from app.api.ubicaciones import router as ubicaciones_router
from app.api.inventario_ubicaciones import router as inventario_ubicaciones_router
from app.api.traspasos import router as traspasos_router
from app.api.ventas import router as ventas_router


def run_startup_migrations():
    with engine.connect() as conn:
        conn.execute(text("""
            ALTER TABLE movimientos
            ADD COLUMN IF NOT EXISTS recibe VARCHAR;
        """))

        conn.execute(text("""
            ALTER TABLE movimientos
            ADD COLUMN IF NOT EXISTS empleado VARCHAR;
        """))

        conn.execute(text("""
            ALTER TABLE movimientos
            ADD COLUMN IF NOT EXISTS nota VARCHAR;
        """))

        conn.execute(text("""
            ALTER TABLE ubicaciones
            ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW();
        """))

        conn.execute(text("""
            ALTER TABLE ventas
            ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW();
        """))

        conn.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    run_startup_migrations()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan
)

origins = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://mexa-frontend.onrender.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# ROUTERS
# =========================
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(organizaciones_router, prefix="/organizaciones", tags=["Organizaciones"])
app.include_router(productos_router)
app.include_router(movimientos_router, prefix="/movimientos", tags=["Movimientos"])
app.include_router(ubicaciones_router, prefix="/ubicaciones", tags=["Ubicaciones"])
app.include_router(inventario_ubicaciones_router, prefix="/inventario-ubicaciones", tags=["Inventario Ubicaciones"])
app.include_router(traspasos_router, prefix="/traspasos", tags=["Traspasos"])
app.include_router(ventas_router, prefix="/ventas", tags=["Ventas"])


# =========================
# RUTA DE EMERGENCIA PRODUCTOS
# =========================
@app.post("/productos/productos/", response_model=ProductoOut, status_code=status.HTTP_201_CREATED)
def crear_producto_emergencia(
    data: ProductoCreate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
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


@app.get("/")
def root():
    return {"message": "Mexa Core funcionando 🚀"}


@app.get("/health")
def health():
    return {"status": "ok"}
