from fastapi import FastAPI
from app.database import engine
from app.models import Base
from app.routes import epp, consumables

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(epp.router)
app.include_router(consumables.router)