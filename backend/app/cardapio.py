"""
Cardápio da loja.

Preços definidos pela loja para começar o desenvolvimento (não é mais
fictício, mas ainda é um valor fixo no código). Quando a integração com a
Google Sheet administrável for implementada (ver docs/02-arquitetura.md), só
este arquivo muda — o resto do código depende apenas do formato de
dicionário retornado por `obter_cardapio()`, não de como ele é obtido.

O tamanho 50g NÃO está no cardápio vendável: segundo a loja, é um brinde
dado sob encomenda, não um item que o cliente escolhe e paga. Se isso virar
uma funcionalidade do bot (ex: "quer levar um brinde de 50g?"), entra depois
como um fluxo separado.
"""

SABORES = [
    "Nutella",
    "Ninho",
    "Doritos",
    "Kinder Bueno",
    "Frutas Vermelhas",
    "Torta de Limão",
]

TAMANHOS_G = [80, 100, 150]

PRECO_BASE_POR_TAMANHO = {
    80: 12.00,
    100: 18.00,
    150: 25.00,
}

# Exceções de preço por (sabor, tamanho_g) — sobrescreve o preço base.
EXCECOES_PRECO = {
    ("Kinder Bueno", 100): 22.00,
}


def obter_cardapio() -> list[dict]:
    """Lista de itens: sabor, tamanho_g, preco, disponivel."""
    itens = []
    for sabor in SABORES:
        for tamanho in TAMANHOS_G:
            preco = EXCECOES_PRECO.get((sabor, tamanho), PRECO_BASE_POR_TAMANHO[tamanho])
            itens.append({"sabor": sabor, "tamanho_g": tamanho, "preco": preco, "disponivel": True})
    return itens


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
