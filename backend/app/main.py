from fastapi import FastAPI

from . import models  # noqa: F401  garante que os modelos sejam registrados no metadata
from .database import Base, engine
from .webhook import router as webhook_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="PipocaBot")
app.include_router(webhook_router)


@app.get("/")
async def raiz() -> dict:
    return {"status": "PipocaBot rodando"}
