from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.database import engine
from app.db.base import Base

import app.models  # noqa: F401

from app.api.productos import router as productos_router
from app.api.movimientos.router.router import router as movimientos_router
from app.api.organizaciones.router import router as organizaciones_router
from app.api.inventario import router as inventario_router
from app.api.auth import router as auth_router

app = FastAPI(title=settings.APP_NAME)

origins = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(productos_router)
app.include_router(movimientos_router)
app.include_router(organizaciones_router)
app.include_router(inventario_router)
app.include_router(auth_router)


@app.get("/")
def root():
    return {"message": "Mexa Core funcionando 🚀"}


@app.get("/health")
def health():
    return {"status": "ok"}
