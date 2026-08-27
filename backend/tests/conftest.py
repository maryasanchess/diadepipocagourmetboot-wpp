"""
Configuração compartilhada dos testes: cada teste ganha um banco SQLite em
memória isolado, pra não misturar dados entre testes nem tocar no banco
real de desenvolvimento (data/pipoca.db).
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings
from app.database import Base


@pytest.fixture(autouse=True)
def _sem_chamadas_reais_de_agenda(monkeypatch):
    """
    Roda pra todo teste automaticamente: garante que nenhum teste cria
    evento na Google Agenda real, mesmo rodando com o .env de verdade
    (o mesmo modo usado pelo chat_local.py — ver app/agenda_service.py).
    """
    monkeypatch.setattr(settings, "modo_teste_local", True)


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
