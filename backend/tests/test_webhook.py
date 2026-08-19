"""Testes dos endpoints HTTP (GET/POST /webhook, GET /)."""

from fastapi.testclient import TestClient

from app import webhook as webhook_module
from app.config import settings
from app.database import get_db
from app.main import app
from app.respostas import RespostaBot

client = TestClient(app)


def test_raiz_responde_status():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json() == {"status": "PipocaBot rodando"}


def test_webhook_verificacao_com_token_correto():
    settings.whatsapp_verify_token = "teste123"
    r = client.get(
        "/webhook",
        params={"hub.mode": "subscribe", "hub.verify_token": "teste123", "hub.challenge": "abc"},
    )
    assert r.status_code == 200
    assert r.text == "abc"


def test_webhook_verificacao_com_token_errado():
    settings.whatsapp_verify_token = "teste123"
    r = client.get(
        "/webhook",
        params={"hub.mode": "subscribe", "hub.verify_token": "errado", "hub.challenge": "abc"},
    )
    assert r.status_code == 403


def test_post_webhook_erro_em_uma_mensagem_nao_derruba_as_outras(db, monkeypatch):
    """
    Um POST da Meta pode trazer mensagens de vários clientes na mesma
    lista. Se uma delas der erro (ex: falha inesperada no processamento),
    as outras ainda precisam ser respondidas, e o endpoint precisa
    continuar devolvendo 200 — senão a Meta reenvia o lote inteiro,
    duplicando o que já tinha funcionado.
    """
    chamadas = []

    async def enviar_texto_fake(telefone, texto):
        chamadas.append((telefone, texto))

    def processar_fake(db_recebido, telefone, texto):
        if telefone == "5511900000000":
            raise RuntimeError("erro simulado")
        return RespostaBot(texto="resposta ok")

    monkeypatch.setattr(webhook_module.whatsapp, "enviar_mensagem_texto", enviar_texto_fake)
    monkeypatch.setattr(webhook_module, "processar_mensagem_recebida", processar_fake)

    payload = {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {"from": "5511900000000", "text": {"body": "vai dar erro"}},
                                {"from": "5511911111111", "text": {"body": "mensagem normal"}},
                            ]
                        }
                    }
                ]
            }
        ]
    }

    app.dependency_overrides[get_db] = lambda: db
    try:
        r = client.post("/webhook", json=payload)
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert r.status_code == 200
    assert chamadas == [("5511911111111", "resposta ok")]
