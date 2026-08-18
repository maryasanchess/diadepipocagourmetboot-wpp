from datetime import datetime, time

from .config import settings


def _parse_hora(valor: str) -> time:
    horas, minutos = valor.split(":")
    return time(hour=int(horas), minute=int(minutos))


def dentro_do_horario_de_atendimento(agora: datetime | None = None) -> bool:
    agora = agora or datetime.now()
    abertura = _parse_hora(settings.horario_abertura)
    fechamento = _parse_hora(settings.horario_fechamento)
    return abertura <= agora.time() <= fechamento
