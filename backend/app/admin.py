from .config import settings


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


def tratar_comando_admin(texto: str) -> str | None:
    """Retorna a resposta do comando admin, ou None se o texto não for um comando reconhecido."""
    comando = texto.strip().lower()
    if comando == "relatorio":
        return "Geração de relatório mensal ainda não implementada — chega em breve."
    return None
