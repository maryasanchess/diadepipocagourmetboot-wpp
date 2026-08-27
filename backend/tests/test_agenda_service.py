"""Testes do agenda_service.py — especialmente o modo de teste local."""

from datetime import datetime, timedelta, timezone

from app import agenda_service, models
from app.config import settings


def _pedido_de_teste(db):
    cliente = models.Cliente(telefone="5511999990000")
    db.add(cliente)
    db.commit()
    db.refresh(cliente)

    pedido = models.Pedido(
        cliente_id=cliente.id,
        tipo_entrega="entrega",
        endereco="Rua Teste, 1",
        data_hora_prevista=datetime.now(timezone.utc) + timedelta(days=1),
        status=models.StatusPedido.confirmado,
    )
    pedido.itens.append(
        models.ItemPedido(sabor="Nutella", tamanho_g=100, quantidade=1, preco_unitario=18.0)
    )
    db.add(pedido)
    db.commit()
    db.refresh(pedido)
    return pedido


def test_modo_teste_local_nao_chama_a_api_real(db, monkeypatch):
    """
    O bug real: rodar a suíte de testes (ou o chat_local.py) sem essa
    proteção criava eventos de verdade na Google Agenda real a cada
    execução — encontramos dezenas deles acumulados na agenda da loja.
    """
    monkeypatch.setattr(settings, "modo_teste_local", True)
    monkeypatch.setattr(settings, "google_calendar_id", "algum-id-qualquer")

    def _api_real_nao_deveria_ser_chamada():
        raise AssertionError("chamou a API real do Google Agenda em modo de teste local")

    monkeypatch.setattr(agenda_service, "obter_servico_calendar", _api_real_nao_deveria_ser_chamada)

    pedido = _pedido_de_teste(db)
    resultado = agenda_service.criar_evento_pedido(pedido)

    assert resultado == "teste-local"


def test_fora_do_modo_teste_local_chama_a_api(db, monkeypatch):
    """Confirma que o modo de teste é opt-in — fora dele, o fluxo real continua intacto."""
    monkeypatch.setattr(settings, "modo_teste_local", False)
    monkeypatch.setattr(settings, "google_calendar_id", "algum-id-qualquer")

    chamadas = []

    class _EventosFake:
        def insert(self, calendarId, body):
            chamadas.append((calendarId, body))
            return self

        def execute(self):
            return {"id": "evento-fake-123"}

    class _ServicoFake:
        def events(self):
            return _EventosFake()

    monkeypatch.setattr(agenda_service, "obter_servico_calendar", lambda: _ServicoFake())

    pedido = _pedido_de_teste(db)
    resultado = agenda_service.criar_evento_pedido(pedido)

    assert resultado == "evento-fake-123"
    assert len(chamadas) == 1
