from contextlib import asynccontextmanager

from fastapi import FastAPI

from . import models  # noqa: F401  garante que os modelos sejam registrados no metadata
from .database import Base, engine
from .webhook import router as webhook_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Cria as tabelas só quando o servidor sobe de verdade — não como
    # efeito colateral de importar o módulo (ex: nos testes, que usam um
    # banco em memória próprio e não devem tocar em data/pipoca.db).
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="PipocaBot", lifespan=lifespan)
app.include_router(webhook_router)


@app.get("/")
async def raiz() -> dict:
    return {"status": "PipocaBot rodando"}
