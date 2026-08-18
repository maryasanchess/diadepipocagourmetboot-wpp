"""
Interpretação e validação da data/horário desejado pelo cliente.

Feito à mão (em vez de uma lib de NLP de datas) de propósito: testamos a
biblioteca `dateparser` e ela deu resultado errado em casos simples (ex:
"hoje às 18h" caindo num dia diferente). Como isso alimenta uma regra de
negócio real (antecedência mínima) e futuramente o evento no Google
Agenda, preferimos um parser pequeno e 100% previsível a um "mágico" que
pode falhar silenciosamente.

Formatos entendidos:
    - "hoje" / "amanhã" (ou "amanha", sem acento) + horário
    - uma data explícita DD/MM ou DD/MM/AAAA + horário
    - horário como "15h", "15h30", "15:30" ou "15:00"

Se o texto não bater com nenhum desses formatos, retorna None e o bot
pede pro cliente reformular.
"""

import re
from datetime import date, datetime, timedelta

from .config import settings

_PADRAO_DATA = re.compile(r"\b(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?\b")
_PADRAO_HORA = re.compile(r"\b(\d{1,2})[h:](\d{2})?\b")


def _extrair_data(texto_lower: str, hoje: date) -> date | None:
    if "amanhã" in texto_lower or "amanha" in texto_lower:
        return hoje + timedelta(days=1)
    if "hoje" in texto_lower:
        return hoje

    match = _PADRAO_DATA.search(texto_lower)
    if not match:
        return None

    dia, mes, ano = match.groups()
    ano_resolvido = int(ano) if ano else hoje.year
    if ano_resolvido < 100:
        ano_resolvido += 2000

    try:
        data = date(ano_resolvido, int(mes), int(dia))
    except ValueError:
        return None

    # Se a data já passou este ano e ninguém disse o ano explicitamente,
    # assume que é para o ano que vem (ex: pedir "25/12" em dezembro tardio).
    if ano is None and data < hoje:
        try:
            data = date(ano_resolvido + 1, int(mes), int(dia))
        except ValueError:
            return None

    return data


def _extrair_hora(texto_lower: str) -> tuple[int, int] | None:
    match = _PADRAO_HORA.search(texto_lower)
    if not match:
        return None
    hora_str, minuto_str = match.groups()
    hora = int(hora_str)
    minuto = int(minuto_str) if minuto_str else 0
    if 0 <= hora <= 23 and 0 <= minuto <= 59:
        return hora, minuto
    return None


def interpretar_data_hora(texto: str, agora: datetime | None = None) -> datetime | None:
    agora = agora or datetime.now()
    texto_lower = texto.strip().lower()

    data = _extrair_data(texto_lower, agora.date())
    hora_minuto = _extrair_hora(texto_lower)
    if data is None or hora_minuto is None:
        return None

    hora, minuto = hora_minuto
    return datetime(data.year, data.month, data.day, hora, minuto)


def antecedencia_suficiente(data_hora: datetime, agora: datetime | None = None) -> bool:
    agora = agora or datetime.now()
    minimo = agora + timedelta(hours=settings.antecedencia_minima_horas)
    return data_hora >= minimo
