from fastapi import FastAPI
from app.api.inventory.router import router as inventory_router

app = FastAPI(
    title="Mexa.Digital Core",
    version="0.1.0"
)

app.include_router(inventory_router)

@app.get("/health")
def health():
    return {"ok": True}
