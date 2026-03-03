from fastapi import FastAPI

from app.core.config import settings
from app.db.database import engine
from app.db.base import Base

import app.models  # noqa: F401

# ✅ IMPORTS CORRECTOS SEGÚN TU REPO
from app.api.productos import router as productos_router
from app.api.organizaciones.router import router as organizaciones_router
from app.api.movimientos.router.router import router as movimientos_router


app = FastAPI(
    title="Mexa.Digital Core",
    version="1.0.0"
)

Base.metadata.create_all(bind=engine)

app.include_router(productos_router)
app.include_router(organizaciones_router)
app.include_router(movimientos_router)


@app.get("/")
def root():
    return {"message": "Mexa.Digital Core activo"}


@app.get("/health")
def health():
    return {"ok": True}
