from sqlalchemy.orm import Session

from . import models
from .config import settings
from .horario import dentro_do_horario_de_atendimento

MENSAGEM_BOAS_VINDAS = (
    "Oi! Bem-vindo(a) à loja de pipocas gourmet \U0001f37f\n"
    "Em breve aqui você vai poder ver o cardápio e montar seu pedido."
)

MENSAGEM_FORA_DO_HORARIO = (
    "No momento estamos fora do horário de atendimento "
    f"({settings.horario_abertura} às {settings.horario_fechamento}). "
    "Você pode ver o cardápio, mas os pedidos só são processados dentro desse horário."
)


def _obter_ou_criar_estado(db: Session, telefone: str) -> models.EstadoConversa:
    estado = db.get(models.EstadoConversa, telefone)
    if estado is None:
        estado = models.EstadoConversa(telefone=telefone, etapa_atual="inicio")
        db.add(estado)
        db.commit()
        db.refresh(estado)
    return estado


def processar_mensagem(db: Session, telefone: str, texto: str) -> str:
    """
    Ponto de entrada da state machine de pedidos.

    Ainda não implementa o fluxo completo (cardápio, tamanho, quantidade,
    entrega, pagamento) — isso vem nas próximas etapas, quando tivermos o
    cardápio real na Google Sheet. Por enquanto só cumprimenta e avisa sobre
    o horário de atendimento.
    """
    _obter_ou_criar_estado(db, telefone)

    if not dentro_do_horario_de_atendimento():
        return f"{MENSAGEM_BOAS_VINDAS}\n\n{MENSAGEM_FORA_DO_HORARIO}"

    return MENSAGEM_BOAS_VINDAS
