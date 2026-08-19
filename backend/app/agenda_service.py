"""
Criação de eventos no Google Agenda para pedidos confirmados.

Se a Agenda não estiver configurada, ou a chamada à API falhar (rede,
credencial, etc.), retorna None em vez de propagar o erro — o pedido já foi
salvo no banco e a conversa com o cliente não deve travar por causa disso.
"""

from datetime import timedelta

from . import models
from .config import settings
from .google_client import obter_servico_calendar

DURACAO_EVENTO_MINUTOS = 30
FUSO_HORARIO = "America/Sao_Paulo"


def _descricao_pedido(pedido: models.Pedido) -> str:
    linhas = [f"Cliente: {pedido.cliente.telefone}"]
    for item in pedido.itens:
        linhas.append(f"- {item.quantidade}x {item.sabor} {item.tamanho_g}g")
    if pedido.tipo_entrega == "entrega":
        linhas.append(f"Entrega em: {pedido.endereco or '(endereço não informado)'}")
    else:
        linhas.append("Retirada na loja")
    linhas.append("Pagamento: Pix")
    return "\n".join(linhas)


def criar_evento_pedido(pedido: models.Pedido) -> str | None:
    """Cria o evento no Google Agenda. Retorna o ID do evento, ou None se não foi possível criar."""
    if not settings.google_calendar_id or pedido.data_hora_prevista is None:
        return None

    inicio = pedido.data_hora_prevista
    fim = inicio + timedelta(minutes=DURACAO_EVENTO_MINUTOS)
    tipo = "Entrega" if pedido.tipo_entrega == "entrega" else "Retirada"

    evento = {
        "summary": f"Pedido #{pedido.id} - {tipo}",
        "description": _descricao_pedido(pedido),
        "start": {"dateTime": inicio.isoformat(), "timeZone": FUSO_HORARIO},
        "end": {"dateTime": fim.isoformat(), "timeZone": FUSO_HORARIO},
    }
    if pedido.tipo_entrega == "entrega" and pedido.endereco:
        evento["location"] = pedido.endereco

    try:
        servico = obter_servico_calendar()
        resultado = (
            servico.events().insert(calendarId=settings.google_calendar_id, body=evento).execute()
        )
        return resultado.get("id")
    except Exception:
        return None
