from datetime import datetime

from sqlalchemy.orm import Session

from .config import settings
from .relatorio import gerar_relatorio_mensal
from .respostas import RespostaBot


def _normalizar_telefone(numero: str) -> str:
    """Garante o código do país (55) em números brasileiros sem ele."""
    digitos = "".join(c for c in numero if c.isdigit())
    if len(digitos) in (10, 11) and not digitos.startswith("55"):
        digitos = "55" + digitos
    return digitos


def _numeros_admin() -> set[str]:
    """ADMIN_PHONE_NUMBER aceita um ou mais números separados por vírgula."""
    return {
        _normalizar_telefone(numero)
        for numero in settings.admin_phone_number.split(",")
        if numero.strip()
    }


def eh_admin(telefone: str) -> bool:
    numeros = _numeros_admin()
    return bool(numeros) and _normalizar_telefone(telefone) in numeros


def _mes_anterior(ano: int, mes: int) -> tuple[int, int]:
    return (ano - 1, 12) if mes == 1 else (ano, mes - 1)


def tratar_comando_admin(db: Session, texto: str) -> RespostaBot | None:
    """Retorna a resposta do comando admin, ou None se o texto não for um comando reconhecido.

    Não faz nenhuma chamada à API do WhatsApp — só gera o arquivo e devolve
    o caminho como anexo. Quem manda de verdade é sempre o webhook.py (ou,
    em teste local, o chat_local.py só avisa que mandaria).
    """
    comando = texto.strip().lower()

    if comando in ("relatorio", "relatório"):
        agora = datetime.now()
        caminho = gerar_relatorio_mensal(db, agora.year, agora.month)
        return RespostaBot(
            texto=f"Relatório de {agora.month:02d}/{agora.year} gerado! Mandando o arquivo... 📎",
            anexo=caminho,
        )

    if comando in ("relatorio mes passado", "relatório mês passado", "relatorio anterior"):
        agora = datetime.now()
        ano, mes = _mes_anterior(agora.year, agora.month)
        caminho = gerar_relatorio_mensal(db, ano, mes)
        return RespostaBot(
            texto=f"Relatório de {mes:02d}/{ano} gerado! Mandando o arquivo... 📎",
            anexo=caminho,
        )

    return None
