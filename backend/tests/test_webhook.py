"""Testes dos endpoints HTTP (GET/POST /webhook, GET /)."""

from fastapi.testclient import TestClient

from app.config import settings
from app.main import app

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
