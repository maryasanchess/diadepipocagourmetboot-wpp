"""
Cardápio da loja.

Fonte de verdade: uma Google Sheet editável pela própria loja (ver
docs/02-arquitetura.md), configurada em GOOGLE_SHEETS_CARDAPIO_ID. O bot lê
essa planilha com um cache curto (CARDAPIO_CACHE_MINUTOS) para não bater na
API do Google a cada mensagem.

Se a planilha não estiver configurada, ou se a leitura falhar (API fora do
ar, planilha mal preenchida), o bot cai para o último cardápio válido em
cache — e, se nunca conseguiu ler nada, usa os valores fixos abaixo como
último recurso, para nunca deixar a conversa quebrada.
"""

import time

from .config import settings
from .google_client import obter_servico_sheets

# Último recurso: usado só se a planilha nunca puder ser lida (não
# configurada, ou primeira falha antes de qualquer leitura bem-sucedida).
SABORES = [
    "Nutella",
    "Ninho",
    "Doritos",
    "Kinder Bueno",
    "Frutas Vermelhas",
    "Torta de Limão",
]
TAMANHOS_G = [80, 100, 150]
PRECO_BASE_POR_TAMANHO = {80: 12.00, 100: 18.00, 150: 25.00}
EXCECOES_PRECO = {("Kinder Bueno", 100): 22.00}


def _cardapio_padrao() -> list[dict]:
    itens = []
    for sabor in SABORES:
        for tamanho in TAMANHOS_G:
            preco = EXCECOES_PRECO.get((sabor, tamanho), PRECO_BASE_POR_TAMANHO[tamanho])
            itens.append({"sabor": sabor, "tamanho_g": tamanho, "preco": preco, "disponivel": True})
    return itens


_cache: dict = {"itens": None, "buscado_em": 0.0}


def _linha_para_item(linha: list) -> dict | None:
    try:
        sabor = str(linha[0]).strip()
        tamanho_g = int(float(str(linha[1]).replace(",", ".")))
        preco = float(str(linha[2]).replace(",", "."))
        disponivel = str(linha[3]).strip().lower() in ("sim", "true", "1")
    except (IndexError, ValueError):
        return None
    if not sabor:
        return None
    return {"sabor": sabor, "tamanho_g": tamanho_g, "preco": preco, "disponivel": disponivel}


def _buscar_da_planilha() -> list[dict]:
    servico = obter_servico_sheets()
    resultado = (
        servico.spreadsheets()
        .values()
        .get(spreadsheetId=settings.google_sheets_cardapio_id, range="A2:D1000")
        .execute()
    )
    linhas = resultado.get("values", [])
    itens = [_linha_para_item(linha) for linha in linhas]
    return [item for item in itens if item is not None]


def obter_cardapio() -> list[dict]:
    """Lista de itens: sabor, tamanho_g, preco, disponivel."""
    if not settings.google_sheets_cardapio_id:
        return _cardapio_padrao()

    agora = time.monotonic()
    cache_valido = (agora - _cache["buscado_em"]) < settings.cardapio_cache_minutos * 60
    if cache_valido and _cache["itens"] is not None:
        return _cache["itens"]

    try:
        itens = _buscar_da_planilha()
        if itens:
            _cache["itens"] = itens
            _cache["buscado_em"] = agora
            return itens
    except Exception:
        pass

    # Falha na leitura: usa o último cardápio válido em cache, se existir.
    if _cache["itens"] is not None:
        return _cache["itens"]
    return _cardapio_padrao()


def sabores_disponiveis() -> list[str]:
    vistos: list[str] = []
    for item in obter_cardapio():
        if item["disponivel"] and item["sabor"] not in vistos:
            vistos.append(item["sabor"])
    return vistos


def tamanhos_disponiveis(sabor: str) -> list[dict]:
    return [
        item
        for item in obter_cardapio()
        if item["sabor"].lower() == (sabor or "").lower() and item["disponivel"]
    ]
