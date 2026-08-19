from datetime import datetime

from sqlalchemy.orm import Session

from .config import settings
from .relatorio import gerar_relatorio_mensal


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


def tratar_comando_admin(db: Session, texto: str) -> str | None:
    """Retorna a resposta do comando admin, ou None se o texto não for um comando reconhecido."""
    comando = texto.strip().lower()

    if comando in ("relatorio", "relatório"):
        agora = datetime.now()
        caminho = gerar_relatorio_mensal(db, agora.year, agora.month)
        return (
            f"Relatório de {agora.month:02d}/{agora.year} gerado: {caminho.name}\n"
            f"Salvo em: {caminho}\n"
            "(Envio automático pelo WhatsApp ainda não está pronto — pegue o arquivo direto no servidor por enquanto.)"
        )

    if comando in ("relatorio mes passado", "relatório mês passado", "relatorio anterior"):
        agora = datetime.now()
        ano, mes = _mes_anterior(agora.year, agora.month)
        caminho = gerar_relatorio_mensal(db, ano, mes)
        return (
            f"Relatório de {mes:02d}/{ano} gerado: {caminho.name}\n"
            f"Salvo em: {caminho}\n"
            "(Envio automático pelo WhatsApp ainda não está pronto — pegue o arquivo direto no servidor por enquanto.)"
        )

    return None
