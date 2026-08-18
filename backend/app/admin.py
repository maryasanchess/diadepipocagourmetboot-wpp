from .config import settings


def eh_admin(telefone: str) -> bool:
    return bool(settings.admin_phone_number) and telefone == settings.admin_phone_number


def tratar_comando_admin(texto: str) -> str | None:
    """Retorna a resposta do comando admin, ou None se o texto não for um comando reconhecido."""
    comando = texto.strip().lower()
    if comando == "relatorio":
        return "Geração de relatório mensal ainda não implementada — chega em breve."
    return None
