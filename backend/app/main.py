from contextlib import asynccontextmanager
import logging
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect, text

from app.core.config import settings
from app.core.security import hash_password
from app.db.database import engine, SessionLocal
from app.db.base import Base
from app.models.organizacion import Organizacion
from app.models.usuario import Usuario

# Registrar todos los modelos antes de ejecutar create_all.
import app.models  # noqa: F401

# Routers que ya incluyen su propio prefijo.
from app.api.auth import router as auth_router
from app.api.organizaciones.router import router as organizaciones_router
from app.api.productos import router as productos_router
from app.api.movimientos.router.router import router as movimientos_router
from app.api.ubicaciones import router as ubicaciones_router
from app.api.vales_resguardo import router as vales_resguardo_router
from app.api.formularios import router as formularios_router
from app.api.escolar import router as escolar_router
from app.api.parking import router as parking_router

# Routers sin prefijo interno.
from app.api.inventario_ubicaciones import router as inventario_ubicaciones_router
from app.api.traspasos import router as traspasos_router


logger = logging.getLogger("mexa.main")


# ==========================================================
# IMPORTACIÓN OPCIONAL DE VENTAS
# ==========================================================
try:
    from app.api.ventas import router as ventas_router
except Exception as exc:  # pragma: no cover
    ventas_router = None
    logger.warning("El router de ventas no pudo cargarse: %s", exc)


# ==========================================================
# MIGRACIONES LIGERAS Y SEGURAS
# ==========================================================
def _table_exists(table_name: str) -> bool:
    return inspect(engine).has_table(table_name)


def _column_exists(table_name: str, column_name: str) -> bool:
    inspector = inspect(engine)
    if not inspector.has_table(table_name):
        return False
    return column_name in {column["name"] for column in inspector.get_columns(table_name)}


def _add_column_if_missing(table_name: str, column_name: str, column_sql: str) -> None:
    if not _table_exists(table_name):
        return
    if _column_exists(table_name, column_name):
        return
    statement = f'ALTER TABLE "{table_name}" ADD COLUMN "{column_name}" {column_sql}'
    try:
        with engine.begin() as connection:
            connection.execute(text(statement))
        logger.info("Migración aplicada: %s.%s", table_name, column_name)
    except Exception as exc:
        logger.exception("No se pudo agregar la columna %s.%s: %s", table_name, column_name, exc)


def run_startup_migrations() -> None:
    dialect = engine.dialect.name
    timestamp_default = (
        "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        if dialect == "sqlite"
        else "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"
    )
    timestamp_nullable = "TIMESTAMP" if dialect == "sqlite" else "TIMESTAMP WITH TIME ZONE"

    # MOVIMIENTOS
    _add_column_if_missing("movimientos", "recibe", "VARCHAR")
    _add_column_if_missing("movimientos", "empleado", "VARCHAR")
    _add_column_if_missing("movimientos", "nota", "VARCHAR")
    _add_column_if_missing("movimientos", "ubicacion_id", "INTEGER")

    # UBICACIONES
    _add_column_if_missing("ubicaciones", "created_at", timestamp_default)
    _add_column_if_missing("ubicaciones", "responsable", "VARCHAR")
    _add_column_if_missing("ubicaciones", "numero_empleado", "VARCHAR")
    _add_column_if_missing("ubicaciones", "ubicacion_padre_id", "INTEGER")

    # VENTAS
    _add_column_if_missing("ventas", "created_at", timestamp_default)

    # IDENTIDAD DE LA INSTITUCIÓN PARA MEXA ESCOLAR
    _add_column_if_missing("organizaciones", "cct", "VARCHAR")
    _add_column_if_missing("organizaciones", "domicilio", "VARCHAR")
    _add_column_if_missing("organizaciones", "telefono", "VARCHAR")
    _add_column_if_missing("organizaciones", "correo_institucional", "VARCHAR")
    _add_column_if_missing("organizaciones", "logo_url", "VARCHAR")
    _add_column_if_missing("organizaciones", "firmante_nombre", "VARCHAR")
    _add_column_if_missing("organizaciones", "firmante_cargo", "VARCHAR")
    _add_column_if_missing("organizaciones", "ciclo_escolar_actual", "VARCHAR")
    _add_column_if_missing("organizaciones", "color_primario", "VARCHAR")

    # PADRÓN ESCOLAR
    _add_column_if_missing("alumnos", "nombre_tutor", "VARCHAR")

    # VALES DE RESGUARDO
    _add_column_if_missing("vales_resguardo", "numero_empleado", "VARCHAR")
    _add_column_if_missing("vales_resguardo", "estado_vale", "VARCHAR DEFAULT 'abierto'")
    _add_column_if_missing("vales_resguardo", "fecha_cierre", timestamp_nullable)
    _add_column_if_missing("vales_resguardo", "usuario_creador", "VARCHAR")
    _add_column_if_missing("vales_resguardo", "ubicacion_fisica_vale", "VARCHAR")
    _add_column_if_missing("vales_resguardo", "estado_archivo_fisico", "VARCHAR DEFAULT 'archivado'")
    _add_column_if_missing("vales_resguardo", "foto_url", "VARCHAR")

    # DETALLES DE VALES
    _add_column_if_missing("vales_resguardo_detalles", "cantidad_devuelta", "INTEGER DEFAULT 0")
    _add_column_if_missing("vales_resguardo_detalles", "estado", "VARCHAR DEFAULT 'pendiente'")
    _add_column_if_missing("vales_resguardo_detalles", "observacion", "VARCHAR")

    # Compatibilidad con un nombre anterior posible de la tabla.
    _add_column_if_missing("vales_resguardo_items", "cantidad_devuelta", "INTEGER DEFAULT 0")
    _add_column_if_missing("vales_resguardo_items", "estado", "VARCHAR DEFAULT 'pendiente'")
    _add_column_if_missing("vales_resguardo_items", "observaciones", "VARCHAR")


def ensure_parking_access() -> None:
    """Crea una organización y usuario inicial de Parking sin tocar datos existentes."""
    email = os.getenv("PARKING_BOOTSTRAP_EMAIL", "").strip().lower()
    password = os.getenv("PARKING_BOOTSTRAP_PASSWORD", "")
    if not email or not password:
        return

    db = SessionLocal()
    try:
        org = db.query(Organizacion).filter(Organizacion.nombre == "Capital Parking").first()
        if not org:
            org = Organizacion(
                nombre="Capital Parking",
                rfc="CAPITAL-PARKING-LOCAL",
                plan="starter",
                tipo="control",
            )
            db.add(org)
            db.flush()

        user = db.query(Usuario).filter(Usuario.email == email).first()
        if not user:
            user = Usuario(
                organizacion_id=org.id,
                nombre="Capital Parking",
                email=email,
                hashed_password=hash_password(password),
                rol="admin",
                activo="si",
            )
            db.add(user)
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.exception("No se pudo preparar el usuario inicial de Parking: %s", exc)
    finally:
        db.close()


# ==========================================================
# CICLO DE VIDA
# ==========================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    run_startup_migrations()
    ensure_parking_access()

    try:
        from scripts.crear_demo_formularios import crear_demo
        crear_demo()
    except Exception as exc:  # pragma: no cover
        logger.exception("No se pudo preparar el acceso inicial: %s", exc)

    logger.info("%s %s iniciado correctamente", settings.APP_NAME, settings.APP_VERSION)
    yield


# ==========================================================
# APLICACIÓN
# ==========================================================
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)


# ==========================================================
# CORS
# ==========================================================
origins = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://mexa-frontend.onrender.com",
    "https://capital-parking-backup.onrender.com",
    "https://mexa.digital",
    "https://www.mexa.digital",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================================
# ARCHIVOS SUBIDOS
# ==========================================================
UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")


# ==========================================================
# ROUTERS
# ==========================================================
app.include_router(auth_router)
app.include_router(organizaciones_router)
app.include_router(productos_router)
app.include_router(movimientos_router)
app.include_router(ubicaciones_router)
app.include_router(vales_resguardo_router)
app.include_router(formularios_router)
app.include_router(escolar_router)
app.include_router(parking_router)

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

if ventas_router is not None:
    app.include_router(ventas_router, prefix="/ventas", tags=["Ventas"])


# ==========================================================
# RUTAS BASE
# ==========================================================
@app.get("/", tags=["Sistema"])
def root():
    return {
        "message": "Mexa Core funcionando",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.get("/health", tags=["Sistema"])
def health():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": engine.dialect.name,
        "ventas_habilitadas": ventas_router is not None,
        "parking_habilitado": True,
    }


@app.get("/formularios-app", include_in_schema=False)
def formularios_app():
    return FileResponse(Path(__file__).resolve().parents[1] / "formularios.html")


@app.get("/escolar-app", include_in_schema=False)
def escolar_app():
    return FileResponse(Path(__file__).resolve().parents[1] / "escolar.html")
