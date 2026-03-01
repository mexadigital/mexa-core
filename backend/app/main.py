import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.database import engine
from app.db.base import Base

# 👇 IMPORTAR MODELOS (IMPORTANTE para que SQLAlchemy registre las tablas)
import app.models  # noqa: F401

# 👇 IMPORTAR ROUTERS
from app.api.productos import router as productos_router
from app.api.organizaciones.router import router as organizaciones_router  # ✅ NUEVO

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Crear todas las tablas
Base.metadata.create_all(bind=engine)
logger.info("Base de datos inicializada")

# Crear instancia de FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

# 👇 REGISTRAR ROUTERS
app.include_router(productos_router)
app.include_router(organizaciones_router)  # ✅ NUEVO

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
def root():
    return {
        "nombre": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online"
    }

@app.get("/health")
def health():
    """Health check"""
    return {"ok": True}
