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
    - horário como "15h", "15h30", "15:30", "15:00" OU só o número
      ("20", "as 20", "às 16") — ver docs/01-visao-geral.md, achado em
      teste real: "hoje as 20" não era reconhecido porque exigíamos "h"
      ou ":" junto do número.

Se o texto não bater com nenhum desses formatos, retorna None e o bot
pede pro cliente reformular.
"""

import re
from datetime import date, datetime, timedelta

from .config import settings

_PADRAO_DATA = re.compile(r"\b(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?\b")
_PADRAO_HORA_COM_SEPARADOR = re.compile(r"\b(\d{1,2})[h:](\d{2})?\b")
_PADRAO_HORA_NUMERO_SOLTO = re.compile(r"\b(\d{1,2})\b")


def _extrair_data(texto_lower: str, hoje: date) -> tuple[date | None, str]:
    """Retorna (data encontrada, texto restante sem a parte da data)."""
    if "amanhã" in texto_lower or "amanha" in texto_lower:
        resto = texto_lower.replace("amanhã", " ").replace("amanha", " ")
        return hoje + timedelta(days=1), resto

    if "hoje" in texto_lower:
        return hoje, texto_lower.replace("hoje", " ")

    match = _PADRAO_DATA.search(texto_lower)
    if not match:
        return None, texto_lower

    dia, mes, ano = match.groups()
    ano_resolvido = int(ano) if ano else hoje.year
    if ano_resolvido < 100:
        ano_resolvido += 2000

    try:
        data = date(ano_resolvido, int(mes), int(dia))
    except ValueError:
        return None, texto_lower

    # Se a data já passou este ano e ninguém disse o ano explicitamente,
    # assume que é para o ano que vem (ex: pedir "25/12" em dezembro tardio).
    if ano is None and data < hoje:
        try:
            data = date(ano_resolvido + 1, int(mes), int(dia))
        except ValueError:
            return None, texto_lower

    # Remove só o trecho da data do texto, pra não confundir dia/mês/ano
    # com o número do horário na busca seguinte.
    resto = texto_lower[: match.start()] + " " + texto_lower[match.end() :]
    return data, resto


def _extrair_hora(resto_sem_data: str) -> tuple[int, int] | None:
    match = _PADRAO_HORA_COM_SEPARADOR.search(resto_sem_data)
    if match:
        hora = int(match.group(1))
        minuto = int(match.group(2)) if match.group(2) else 0
        if 0 <= hora <= 23 and 0 <= minuto <= 59:
            return hora, minuto

    # Fallback: número solto no que sobrou do texto (ex: "hoje as 20"),
    # já sem o trecho da data pra não pegar dia/mês/ano por engano.
    match = _PADRAO_HORA_NUMERO_SOLTO.search(resto_sem_data)
    if match:
        hora = int(match.group(1))
        if 0 <= hora <= 23:
            return hora, 0

    return None


def interpretar_data_hora(texto: str, agora: datetime | None = None) -> datetime | None:
    agora = agora or datetime.now()
    texto_lower = texto.strip().lower()

    data, resto_sem_data = _extrair_data(texto_lower, agora.date())
    if data is None:
        return None

    hora_minuto = _extrair_hora(resto_sem_data)
    if hora_minuto is None:
        return None

    hora, minuto = hora_minuto
    return datetime(data.year, data.month, data.day, hora, minuto)


def antecedencia_suficiente(data_hora: datetime, agora: datetime | None = None) -> bool:
    agora = agora or datetime.now()
    minimo = agora + timedelta(hours=settings.antecedencia_minima_horas)
    return data_hora >= minimo
