from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.database import engine
from app.db.base import Base

# Registrar modelos antes de create_all
import app.models  # noqa: F401

# Routers
from app.api.auth import router as auth_router
from app.api.organizaciones.router import router as organizaciones_router
from app.api.productos import router as productos_router
from app.api.movimientos import router as movimientos_router
from app.api.ubicaciones import router as ubicaciones_router
from app.api.inventario_ubicaciones import router as inventario_ubicaciones_router
from app.api.traspasos import router as traspasos_router


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

origins = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "Mexa Digital API funcionando",
        "version": settings.APP_VERSION,
    }


app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(organizaciones_router, prefix="/organizaciones", tags=["Organizaciones"])
app.include_router(productos_router, prefix="/productos", tags=["Productos"])
app.include_router(movimientos_router, prefix="/movimientos", tags=["Movimientos"])
app.include_router(ubicaciones_router, prefix="/ubicaciones", tags=["Ubicaciones"])
app.include_router(
    inventario_ubicaciones_router,
    prefix="/inventario-ubicaciones",
    tags=["Inventario Ubicaciones"],
)
app.include_router(traspasos_router, prefix="/traspasos", tags=["Traspasos"])
