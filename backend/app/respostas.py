"""
Tipo de retorno comum pra qualquer resposta do bot (conversa normal ou
comando admin). Separar texto de anexo mantém o envio de verdade pelo
WhatsApp isolado na borda (webhook.py) — o resto do código nunca faz
chamada de rede, o que deixa tudo testável sem depender da API real.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class RespostaBot:
    texto: str
    anexo: Path | None = None
