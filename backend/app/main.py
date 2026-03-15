from fastapi import FastAPI

from app.core.config import settings
from app.db.database import engine
from app.db.base import Base

# Registrar modelos
import app.models  # noqa: F401

# Routers
from app.api.productos import router as productos_router
from app.api.movimientos.router.router import router as movimientos_router
from app.api.organizaciones.router import router as organizaciones_router
from app.api.inventario import router as inventario_router
from app.api.auth import router as auth_router

app = FastAPI(title=settings.APP_NAME)

# Crear tablas
Base.metadata.create_all(bind=engine)

# Routers
app.include_router(productos_router)
app.include_router(movimientos_router)
app.include_router(organizaciones_router)
app.include_router(inventario_router)
app.include_router(auth_router)

# Rutas base
@app.get("/")
def root():
    return {"message": "Mexa Core funcionando 🚀"}


@app.get("/health")
def health():
    return {"status": "ok"}
