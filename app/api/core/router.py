from fastapi import APIRouter
from .empresas import router as empresas_router

router = APIRouter(prefix="/core", tags=["core"])

router.include_router(
    empresas_router,
    prefix="/empresas",
    tags=["core-empresas"]
)
