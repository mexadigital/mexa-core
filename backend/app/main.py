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
from app.api.vales_resguardo import router as vales_resguardo_router


# ==========================================================
# ROUTER OPCIONAL PARA DÍA 12
# ==========================================================
# Esto NO rompe si todavía no existe el archivo.
# Más adelante podremos crear:
# app/api/reportes_vales.py
#
# Y ahí meter:
# GET /reportes/empleado-pendientes?query=...
try:
    from app.api.reportes_vales import router as reportes_vales_router
except Exception:
    reportes_vales_router = None


def run_startup_migrations():
    """
    Migraciones ligeras al arrancar.

    La idea es no borrar nada, no romper datos existentes
    y agregar columnas necesarias conforme crece el SaaS.
    """

    with engine.connect() as conn:

        # ==================================================
        # MOVIMIENTOS
        # ==================================================
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
            ALTER TABLE movimientos
            ADD COLUMN IF NOT EXISTS ubicacion_id INTEGER;
        """))

        # ==================================================
        # UBICACIONES
        # ==================================================
        conn.execute(text("""
            ALTER TABLE ubicaciones
            ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW();
        """))

        conn.execute(text("""
            ALTER TABLE ubicaciones
            ADD COLUMN IF NOT EXISTS responsable VARCHAR;
        """))

        conn.execute(text("""
            ALTER TABLE ubicaciones
            ADD COLUMN IF NOT EXISTS numero_empleado VARCHAR;
        """))

        # ==================================================
        # VENTAS
        # ==================================================
        conn.execute(text("""
            ALTER TABLE ventas
            ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW();
        """))

        # ==================================================
        # VALES / RESGUARDOS — SOPORTE DÍA 12
        # ==================================================
        # Estas columnas ayudan al flujo:
        # - Vale abierto
        # - Vale cerrado
        # - Devolución parcial
        # - Reporte de bajas por empleado
        #
        # OJO:
        # Estas migraciones asumen que la tabla vales_resguardo
        # ya existe por el modelo actual.
        # Si tu modelo usa otro nombre de tabla, lo ajustamos.
        try:
            conn.execute(text("""
                ALTER TABLE vales_resguardo
                ADD COLUMN IF NOT EXISTS estado VARCHAR DEFAULT 'ABIERTO';
            """))

            conn.execute(text("""
                ALTER TABLE vales_resguardo
                ADD COLUMN IF NOT EXISTS numero_empleado VARCHAR;
            """))

            conn.execute(text("""
                ALTER TABLE vales_resguardo
                ADD COLUMN IF NOT EXISTS empleado VARCHAR;
            """))

            conn.execute(text("""
                ALTER TABLE vales_resguardo
                ADD COLUMN IF NOT EXISTS responsable VARCHAR;
            """))

            conn.execute(text("""
                ALTER TABLE vales_resguardo
                ADD COLUMN IF NOT EXISTS observaciones VARCHAR;
            """))

            conn.execute(text("""
                ALTER TABLE vales_resguardo
                ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW();
            """))

            conn.execute(text("""
                ALTER TABLE vales_resguardo
                ADD COLUMN IF NOT EXISTS closed_at TIMESTAMP;
            """))
        except Exception:
            # No detenemos el arranque si todavía no existe la tabla.
            # Base.metadata.create_all normalmente la crea si el modelo existe.
            pass

        # ==================================================
        # ITEMS DE VALES / RESGUARDOS — SOPORTE PENDIENTES
        # ==================================================
        # Para calcular:
        # pendiente = cantidad - cantidad_devuelta
        #
        # Si tu tabla tiene otro nombre, luego lo ajustamos.
        try:
            conn.execute(text("""
                ALTER TABLE vales_resguardo_items
                ADD COLUMN IF NOT EXISTS cantidad_devuelta INTEGER DEFAULT 0;
            """))

            conn.execute(text("""
                ALTER TABLE vales_resguardo_items
                ADD COLUMN IF NOT EXISTS estado VARCHAR DEFAULT 'PENDIENTE';
            """))

            conn.execute(text("""
                ALTER TABLE vales_resguardo_items
                ADD COLUMN IF NOT EXISTS observaciones VARCHAR;
            """))
        except Exception:
            # No detenemos el arranque si todavía no existe la tabla.
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
    lifespan=lifespan
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
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================================
# ROUTERS
# ==========================================================
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(
    organizaciones_router,
    prefix="/organizaciones",
    tags=["Organizaciones"],
)
app.include_router(productos_router)
app.include_router(movimientos_router, prefix="/movimientos", tags=["Movimientos"])
app.include_router(ubicaciones_router, prefix="/ubicaciones", tags=["Ubicaciones"])
app.include_router(
    inventario_ubicaciones_router,
    prefix="/inventario-ubicaciones",
    tags=["Inventario Ubicaciones"],
)
app.include_router(traspasos_router, prefix="/traspasos", tags=["Traspasos"])
app.include_router(ventas_router, prefix="/ventas", tags=["Ventas"])
app.include_router(vales_resguardo_router)


# Router opcional para reportes de Día 12
if reportes_vales_router is not None:
    app.include_router(
        reportes_vales_router,
        prefix="/reportes",
        tags=["Reportes"],
    )


# ==========================================================
# RUTA DE EMERGENCIA PRODUCTOS
# ==========================================================
@app.post(
    "/productos/productos/",
    response_model=ProductoOut,
    status_code=status.HTTP_201_CREATED,
)
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


# ==========================================================
# RUTAS BASE
# ==========================================================
@app.get("/")
def root():
    return {"message": "Mexa Core funcionando 🚀"}


@app.get("/health")
def health():
    return {"status": "ok"}
