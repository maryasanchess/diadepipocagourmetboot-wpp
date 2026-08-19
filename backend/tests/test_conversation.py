"""
Testes do fluxo de conversa (app/conversation.py).

Datas usadas nos testes são calculadas a partir de "agora + alguns dias",
nunca fixas — evita testes instáveis perto da borda das 24h de
antecedência mínima (already found this the hard way, ver
docs/08-registro-de-testes.md).
"""

from datetime import datetime, timedelta

from app import conversation, models
from app.config import settings

TELEFONE = "5511999990000"


def _data_segura(dias: int = 3) -> str:
    """Uma data/horário garantidamente além da antecedência mínima."""
    return (datetime.now() + timedelta(days=dias)).strftime("%d/%m às %Hh")


def test_pedido_completo_dois_itens_entrega(db):
    conversation.processar_mensagem(db, TELEFONE, "oi")
    conversation.processar_mensagem(db, TELEFONE, "Nutella")
    conversation.processar_mensagem(db, TELEFONE, "2")  # tamanho por índice
    conversation.processar_mensagem(db, TELEFONE, "3")  # quantidade
    conversation.processar_mensagem(db, TELEFONE, "sim")
    conversation.processar_mensagem(db, TELEFONE, "Ninho")
    conversation.processar_mensagem(db, TELEFONE, "1")
    conversation.processar_mensagem(db, TELEFONE, "1")
    conversation.processar_mensagem(db, TELEFONE, "nao")
    conversation.processar_mensagem(db, TELEFONE, "entrega")
    conversation.processar_mensagem(db, TELEFONE, "Rua das Flores, 123")
    conversation.processar_mensagem(db, TELEFONE, _data_segura())
    resposta = conversation.processar_mensagem(db, TELEFONE, "sim")

    assert "confirmado" in resposta.lower()

    pedido = db.query(models.Pedido).order_by(models.Pedido.id.desc()).first()
    assert pedido is not None
    assert len(pedido.itens) == 2
    assert pedido.status == models.StatusPedido.recebido
    assert pedido.tipo_entrega == "entrega"
    assert pedido.endereco == "Rua das Flores, 123"
    assert pedido.data_hora_prevista is not None


def test_multiplos_sabores_em_uma_mensagem(db):
    conversation.processar_mensagem(db, TELEFONE, "oi")
    resposta = conversation.processar_mensagem(db, TELEFONE, "Nutella e Torta de Limao")
    assert "torta de limão" in resposta.lower() or "nutella" in resposta.lower()

    conversation.processar_mensagem(db, TELEFONE, "2")  # tamanho do 1º
    conversation.processar_mensagem(db, TELEFONE, "3")  # qtd do 1º -> deve avançar pro 2º sabor sem perguntar "mais um?"
    resposta = conversation.processar_mensagem(db, TELEFONE, "2")  # tamanho do 2º
    assert "quantas unidades" in resposta.lower()


def test_sabor_sem_acento_e_reconhecido(db):
    conversation.processar_mensagem(db, TELEFONE, "oi")
    resposta = conversation.processar_mensagem(db, TELEFONE, "limao")
    assert "torta de limão" in resposta.lower()


def test_kinder_bueno_preco_diferenciado(db):
    conversation.processar_mensagem(db, TELEFONE, "oi")
    conversation.processar_mensagem(db, TELEFONE, "Kinder Bueno")
    conversation.processar_mensagem(db, TELEFONE, "2")  # 100g
    conversation.processar_mensagem(db, TELEFONE, "2")  # quantidade
    conversation.processar_mensagem(db, TELEFONE, "nao")
    conversation.processar_mensagem(db, TELEFONE, "retirada")
    resposta = conversation.processar_mensagem(db, TELEFONE, _data_segura())

    assert "44.00" in resposta  # 2x R$22


def test_cancelar_pedido_em_andamento(db):
    conversation.processar_mensagem(db, TELEFONE, "oi")
    conversation.processar_mensagem(db, TELEFONE, "Doritos")
    resposta = conversation.processar_mensagem(db, TELEFONE, "cancelar")

    assert "cancelado" in resposta.lower()
    estado = db.get(models.EstadoConversa, TELEFONE)
    assert estado.etapa_atual == "inicio"


def test_cancelar_pedido_ja_confirmado(db):
    conversation.processar_mensagem(db, TELEFONE, "oi")
    conversation.processar_mensagem(db, TELEFONE, "Doritos")
    conversation.processar_mensagem(db, TELEFONE, "1")
    conversation.processar_mensagem(db, TELEFONE, "1")
    conversation.processar_mensagem(db, TELEFONE, "nao")
    conversation.processar_mensagem(db, TELEFONE, "retirada")
    conversation.processar_mensagem(db, TELEFONE, _data_segura())
    conversation.processar_mensagem(db, TELEFONE, "sim")

    resposta = conversation.processar_mensagem(db, TELEFONE, "cancelar")
    assert "cancelado" in resposta.lower()

    pedido = db.query(models.Pedido).order_by(models.Pedido.id.desc()).first()
    assert pedido.status == models.StatusPedido.cancelado


def test_agradecimento_apos_pedido_nao_reabre_cardapio(db):
    conversation.processar_mensagem(db, TELEFONE, "oi")
    conversation.processar_mensagem(db, TELEFONE, "Doritos")
    conversation.processar_mensagem(db, TELEFONE, "1")
    conversation.processar_mensagem(db, TELEFONE, "1")
    conversation.processar_mensagem(db, TELEFONE, "nao")
    conversation.processar_mensagem(db, TELEFONE, "retirada")
    conversation.processar_mensagem(db, TELEFONE, _data_segura())
    conversation.processar_mensagem(db, TELEFONE, "sim")

    resposta = conversation.processar_mensagem(db, TELEFONE, "ok")
    assert "cardápio" not in resposta.lower()
    assert "bem-vindo" not in resposta.lower()

    resposta_oi = conversation.processar_mensagem(db, TELEFONE, "oi")
    assert "bem-vindo" in resposta_oi.lower()


def test_sabor_invalido_mostra_lista(db):
    conversation.processar_mensagem(db, TELEFONE, "oi")
    resposta = conversation.processar_mensagem(db, TELEFONE, "sabor que não existe")
    assert "não encontrei" in resposta.lower()


def test_antecedencia_minima_rejeita_horario_muito_proximo(db):
    conversation.processar_mensagem(db, TELEFONE, "oi")
    conversation.processar_mensagem(db, TELEFONE, "Doritos")
    conversation.processar_mensagem(db, TELEFONE, "1")
    conversation.processar_mensagem(db, TELEFONE, "1")
    conversation.processar_mensagem(db, TELEFONE, "nao")
    conversation.processar_mensagem(db, TELEFONE, "retirada")

    agora = datetime.now().strftime("%d/%m às %Hh")  # "agora" nunca tem 24h de antecedência
    resposta = conversation.processar_mensagem(db, TELEFONE, agora)
    assert "antecedência" in resposta.lower()


def test_taxa_de_entrega_nao_configurada_fica_a_confirmar(db, monkeypatch):
    monkeypatch.setattr(settings, "taxa_entrega_fixa", "")

    conversation.processar_mensagem(db, TELEFONE, "oi")
    conversation.processar_mensagem(db, TELEFONE, "Doritos")
    conversation.processar_mensagem(db, TELEFONE, "1")
    conversation.processar_mensagem(db, TELEFONE, "1")
    conversation.processar_mensagem(db, TELEFONE, "nao")
    conversation.processar_mensagem(db, TELEFONE, "entrega")
    conversation.processar_mensagem(db, TELEFONE, "Rua Teste, 1")
    resumo = conversation.processar_mensagem(db, TELEFONE, _data_segura())

    assert "a confirmar" in resumo.lower()
    conversation.processar_mensagem(db, TELEFONE, "sim")

    pedido = db.query(models.Pedido).order_by(models.Pedido.id.desc()).first()
    assert pedido.taxa_entrega is None


def test_taxa_de_entrega_configurada_entra_no_total(db, monkeypatch):
    monkeypatch.setattr(settings, "taxa_entrega_fixa", "5.00")

    conversation.processar_mensagem(db, TELEFONE, "oi")
    conversation.processar_mensagem(db, TELEFONE, "Doritos")
    conversation.processar_mensagem(db, TELEFONE, "1")  # 80g, R$12
    conversation.processar_mensagem(db, TELEFONE, "1")
    conversation.processar_mensagem(db, TELEFONE, "nao")
    conversation.processar_mensagem(db, TELEFONE, "entrega")
    conversation.processar_mensagem(db, TELEFONE, "Rua Teste, 1")
    resumo = conversation.processar_mensagem(db, TELEFONE, _data_segura())

    assert "R$ 5.00" in resumo
    assert "17.00" in resumo  # 12 (item) + 5 (taxa)
    conversation.processar_mensagem(db, TELEFONE, "sim")

    pedido = db.query(models.Pedido).order_by(models.Pedido.id.desc()).first()
    assert pedido.taxa_entrega == 5.00


def test_taxa_de_entrega_nao_se_aplica_na_retirada(db, monkeypatch):
    monkeypatch.setattr(settings, "taxa_entrega_fixa", "5.00")

    conversation.processar_mensagem(db, TELEFONE, "oi")
    conversation.processar_mensagem(db, TELEFONE, "Doritos")
    conversation.processar_mensagem(db, TELEFONE, "1")
    conversation.processar_mensagem(db, TELEFONE, "1")
    conversation.processar_mensagem(db, TELEFONE, "nao")
    conversation.processar_mensagem(db, TELEFONE, "retirada")
    resumo = conversation.processar_mensagem(db, TELEFONE, _data_segura())

    assert "taxa de entrega" not in resumo.lower()
    conversation.processar_mensagem(db, TELEFONE, "sim")

    pedido = db.query(models.Pedido).order_by(models.Pedido.id.desc()).first()
    assert pedido.taxa_entrega is None
