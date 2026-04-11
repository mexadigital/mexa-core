from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.db.database import engine
from app.db.base import Base

# Registrar modelos
import app.models  # noqa: F401

# Routers
from app.api.auth import router as auth_router
from app.api.organizaciones.router import router as organizaciones_router
from app.api.productos import router as productos_router
from app.api.movimientos.router.router import router as movimientos_router
from app.api.ubicaciones import router as ubicaciones_router
from app.api.inventario_ubicaciones import router as inventario_ubicaciones_router
from app.api.traspasos import router as traspasos_router
from app.api.ventas import router as ventas_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Inicialización de la aplicación.
    Crea tablas que no existan al arrancar.
    """
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# =========================
# CORS
# =========================
origins = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://mexa-core-2.onrender.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# RUTAS BASE
# =========================
@app.get("/")
def root():
    return {
        "message": "Mexa Digital API funcionando",
        "version": settings.APP_VERSION,
        "status": "ok",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


# =========================
# FIX TEMPORAL DE BD (VENTAS)
# =========================
@app.get("/fix-db")
def fix_db():
    """
    Reinicia las tablas de ventas
    """
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS venta_detalles CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS ventas CASCADE;"))
        conn.commit()

    Base.metadata.create_all(bind=engine)

    return {
        "message": "DB reset",
        "detail": "Tablas ventas recreadas correctamente"
    }


# =========================
# 🔥 AGREGAR COLUMNAS MOVIMIENTOS (VALE)
# =========================
@app.get("/add-column-movimientos")
def add_columns():
    """
    Agrega columnas para vale de almacén
    """
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE movimientos ADD COLUMN IF NOT EXISTS recibe VARCHAR;"))
        conn.execute(text("ALTER TABLE movimientos ADD COLUMN IF NOT EXISTS empleado VARCHAR;"))
        conn.execute(text("ALTER TABLE movimientos ADD COLUMN IF NOT EXISTS nota VARCHAR;"))
        conn.commit()

    return {"ok": True}


# =========================
# ROUTERS
# =========================
app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Auth"],
)

app.include_router(
    organizaciones_router,
    prefix="/organizaciones",
    tags=["Organizaciones"],
)

app.include_router(
    productos_router,
    prefix="/productos",
    tags=["Productos"],
)

# movimientos ya trae prefix interno
app.include_router(
    movimientos_router,
)

app.include_router(
    ubicaciones_router,
    prefix="/ubicaciones",
    tags=["Ubicaciones"],
)

app.include_router(
    inventario_ubicaciones_router,
    prefix="/inventario-ubicaciones",
    tags=["Inventario Ubicaciones"],
)

app.include_router(
    traspasos_router,
    prefix="/traspasos",
    tags=["Traspasos"],
)

# ventas ya trae prefix interno
app.include_router(
    ventas_router,
)
