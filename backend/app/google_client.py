"""
Cliente compartilhado para as APIs do Google (Calendar e Sheets), usando a
conta de serviço configurada em GOOGLE_CREDENTIALS_PATH.
"""

from functools import lru_cache

from google.oauth2 import service_account
from googleapiclient.discovery import build

from .config import settings

ESCOPOS = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/spreadsheets.readonly",
]


@lru_cache
def _credenciais():
    return service_account.Credentials.from_service_account_file(
        settings.google_credentials_path, scopes=ESCOPOS
    )


@lru_cache
def obter_servico_calendar():
    return build("calendar", "v3", credentials=_credenciais(), cache_discovery=False)


@lru_cache
def obter_servico_sheets():
    return build("sheets", "v4", credentials=_credenciais(), cache_discovery=False)
