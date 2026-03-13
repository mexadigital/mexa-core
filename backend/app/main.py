from fastapi import FastAPI

from app.core.config import settings
from app.db.database import engine
from app.db.base import Base

import app.models  # noqa: F401

from app.api.productos import router as productos_router
from app.api.movimientos.router.router import router as movimientos_router

app = FastAPI(title=settings.PROJECT_NAME)

Base.metadata.create_all(bind=engine)

app.include_router(productos_router)
app.include_router(movimientos_router)


@app.get("/")
def root():
    return {"message": "Mexa Core funcionando"}
