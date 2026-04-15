from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.db.database import engine
from app.db.base import Base

import app.models  # noqa: F401

from app.api.auth import router as auth_router
from app.api.organizaciones.router import router as organizaciones_router
from app.api.productos import router as productos_router
from app.api.movimientos.router.router import router as movimientos_router
from app.api.ubicaciones import router as ubicaciones_router
from app.api.inventario_ubicaciones import router as inventario_ubicaciones_router
from app.api.traspasos import router as traspasos_router
from app.api.ventas import router as ventas_router
from app.api.usuarios import router as usuarios_router


def run_startup_migrations():
    with engine.connect() as conn:
        conn.execute(text("""
            ALTER TABLE organizaciones
            ADD COLUMN IF NOT EXISTS tipo VARCHAR DEFAULT 'control';
        """))

        conn.execute(text("""
            ALTER TABLE usuarios
            ADD COLUMN IF NOT EXISTS rol VARCHAR DEFAULT 'usuario';
        """))
        conn.execute(text("""
            ALTER TABLE usuarios
            ADD COLUMN IF NOT EXISTS activo VARCHAR DEFAULT 'si';
        """))
        conn.execute(text("""
            ALTER TABLE usuarios
            ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT NOW();
        """))

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
            ALTER TABLE ventas
            ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT NOW();
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Mexa.Digital API activa"}


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(organizaciones_router)
app.include_router(productos_router)
app.include_router(movimientos_router)
app.include_router(ubicaciones_router)
app.include_router(inventario_ubicaciones_router)
app.include_router(traspasos_router)
app.include_router(ventas_router)
app.include_router(usuarios_router)
