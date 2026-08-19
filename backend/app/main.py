from contextlib import asynccontextmanager
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect, text

from app.core.config import settings
from app.db.database import engine
from app.db.base import Base

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

# Routers sin prefijo interno.
from app.api.inventario_ubicaciones import router as inventario_ubicaciones_router
from app.api.traspasos import router as traspasos_router


logger = logging.getLogger("mexa.main")


# ==========================================================
# IMPORTACIÓN OPCIONAL DE VENTAS
# ==========================================================
# Actualmente app/api/ventas.py importa get_current_user desde
# app.api.deps, pero en este proyecto la dependencia real está en
# app.core.deps. Mientras se corrige ese import, el backend podrá
# arrancar sin perder el resto de los módulos.
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

    return column_name in {
        column["name"] for column in inspector.get_columns(table_name)
    }


def _add_column_if_missing(
    table_name: str,
    column_name: str,
    column_sql: str,
) -> None:
    """
    Agrega una columna únicamente cuando la tabla existe y la columna
    todavía no existe.

    Funciona tanto con PostgreSQL como con SQLite porque primero revisa
    el esquema y después ejecuta un ALTER TABLE sencillo.
    """

    if not _table_exists(table_name):
        return

    if _column_exists(table_name, column_name):
        return

    statement = (
        f'ALTER TABLE "{table_name}" '
        f'ADD COLUMN "{column_name}" {column_sql}'
    )

    try:
        with engine.begin() as connection:
            connection.execute(text(statement))

        logger.info(
            "Migración aplicada: %s.%s",
            table_name,
            column_name,
        )
    except Exception as exc:
        logger.exception(
            "No se pudo agregar la columna %s.%s: %s",
            table_name,
            column_name,
            exc,
        )


def run_startup_migrations() -> None:
    """
    Migraciones pequeñas para conservar datos existentes.

    Base.metadata.create_all() crea tablas nuevas, pero no agrega columnas
    a tablas que ya existen. Estas verificaciones completan ese trabajo
    sin borrar registros.
    """

    dialect = engine.dialect.name

    timestamp_default = (
        "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        if dialect == "sqlite"
        else "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"
    )

    timestamp_nullable = (
        "TIMESTAMP"
        if dialect == "sqlite"
        else "TIMESTAMP WITH TIME ZONE"
    )

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
    _add_column_if_missing(
        "vales_resguardo",
        "estado_vale",
        "VARCHAR DEFAULT 'abierto'",
    )
    _add_column_if_missing("vales_resguardo", "fecha_cierre", timestamp_nullable)
    _add_column_if_missing("vales_resguardo", "usuario_creador", "VARCHAR")
    _add_column_if_missing("vales_resguardo", "ubicacion_fisica_vale", "VARCHAR")
    _add_column_if_missing(
        "vales_resguardo",
        "estado_archivo_fisico",
        "VARCHAR DEFAULT 'archivado'",
    )
    _add_column_if_missing("vales_resguardo", "foto_url", "VARCHAR")

    # DETALLES DE VALES
    _add_column_if_missing(
        "vales_resguardo_detalles",
        "cantidad_devuelta",
        "INTEGER DEFAULT 0",
    )
    _add_column_if_missing(
        "vales_resguardo_detalles",
        "estado",
        "VARCHAR DEFAULT 'pendiente'",
    )
    _add_column_if_missing("vales_resguardo_detalles", "observacion", "VARCHAR")

    # Compatibilidad con un nombre anterior posible de la tabla.
    _add_column_if_missing(
        "vales_resguardo_items",
        "cantidad_devuelta",
        "INTEGER DEFAULT 0",
    )
    _add_column_if_missing(
        "vales_resguardo_items",
        "estado",
        "VARCHAR DEFAULT 'pendiente'",
    )
    _add_column_if_missing("vales_resguardo_items", "observaciones", "VARCHAR")


# ==========================================================
# CICLO DE VIDA
# ==========================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    run_startup_migrations()

    # El bootstrap es idempotente y sólo actúa cuando existen las variables
    # privadas MEXA_BOOTSTRAP_EMAIL y MEXA_BOOTSTRAP_PASSWORD.
    try:
        from scripts.crear_demo_formularios import crear_demo

        crear_demo()
    except Exception as exc:  # pragma: no cover
        logger.exception("No se pudo preparar el acceso inicial: %s", exc)

    logger.info(
        "%s %s iniciado correctamente",
        settings.APP_NAME,
        settings.APP_VERSION,
    )

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
# Estos routers YA tienen prefijo interno.
app.include_router(auth_router)
app.include_router(organizaciones_router)
app.include_router(productos_router)
app.include_router(movimientos_router)
app.include_router(ubicaciones_router)
app.include_router(vales_resguardo_router)
app.include_router(formularios_router)
app.include_router(escolar_router)

# Estos routers NO tienen prefijo interno.
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
    app.include_router(
        ventas_router,
        prefix="/ventas",
        tags=["Ventas"],
    )


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
    }


@app.get("/formularios-app", include_in_schema=False)
def formularios_app():
    return FileResponse(Path(__file__).resolve().parents[1] / "formularios.html")


@app.get("/escolar-app", include_in_schema=False)
def escolar_app():
    return FileResponse(Path(__file__).resolve().parents[1] / "escolar.html")
