from fastapi import FastAPI
from app.db import init_db
from app.api.inventory.router import router as inventory_router
from app.api.core.router import router as core_router

app = FastAPI(title="Mexa.Digital Core", version="0.1.0")

@app.on_event("startup")
def startup():
    init_db()

app.include_router(inventory_router)
app.include_router(core_router)

@app.get("/health")
def health():
    return {"ok": True}
