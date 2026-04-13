from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.db.base import Base
from app.db.database import engine

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
from app.api.requisiciones import router as requisiciones_router


def run_startup_migrations() -> None:
    with engine.connect() as conn:

        # =========================
        # MOVIMIENTOS
        # =========================
        try:
            conn.execute(text("""
                ALTER TABLE movimientos
                ADD COLUMN IF NOT EXISTS recibe VARCHAR;
            """))
        except Exception:
            pass

        try:
            conn.execute(text("""
                ALTER TABLE movimientos
                ADD COLUMN IF NOT EXISTS empleado VARCHAR;
            """))
        except Exception:
            pass

        try:
            conn.execute(text("""
                ALTER TABLE movimientos
                ADD COLUMN IF NOT EXISTS nota TEXT;
            """))
        except Exception:
            pass

        # =========================
        # UBICACIONES
        # =========================
        try:
            conn.execute(text("""
                ALTER TABLE ubicaciones
                ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT TRUE;
            """))
        except Exception:
            pass

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
    lifespan=lifespan,
)

# =========================
# CORS (AQUÍ ESTÁ LA CLAVE 🔥)
# =========================
origins = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://mexa-core-1.onrender.com",
    "https://mexa-frontend.onrender.com",  # 👈 ESTE ES EL IMPORTANTE
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
        "message": "Mexa Core API funcionando",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.get("/health")
def health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": str(e)}


# =========================
# ROUTERS
# =========================
app.include_router(auth_router)
app.include_router(organizaciones_router)
app.include_router(productos_router)
app.include_router(movimientos_router)
app.include_router(ubicaciones_router)
app.include_router(inventario_ubicaciones_router)
app.include_router(traspasos_router)
app.include_router(ventas_router)
app.include_router(requisiciones_router)
