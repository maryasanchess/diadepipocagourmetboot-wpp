"""
Cardápio da loja.

Os preços abaixo são FICTÍCIOS (placeholder) porque a loja ainda não
definiu os valores reais (ver docs/01-visao-geral.md). Quando a
integração com a Google Sheet administrável for implementada (ver
docs/02-arquitetura.md), só esta função muda — o resto do código depende
apenas do formato de dicionário retornado aqui, não de como ele é obtido.
"""

SABORES = [
    "Nutella",
    "Ninho",
    "Doritos",
    "Kinder Bueno",
    "Frutas Vermelhas",
    "Torta de Limão",
]

PRECO_FICTICIO_POR_TAMANHO = {
    50: 10.00,
    80: 15.00,
    100: 18.00,
    150: 25.00,
}


def obter_cardapio() -> list[dict]:
    """Lista de itens: sabor, tamanho_g, preco, disponivel."""
    return [
        {"sabor": sabor, "tamanho_g": tamanho, "preco": preco, "disponivel": True}
        for sabor in SABORES
        for tamanho, preco in PRECO_FICTICIO_POR_TAMANHO.items()
    ]


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
