"""
Ponto único de entrada para decidir se uma mensagem recebida é um comando
admin ou deve seguir pro fluxo normal de conversa. Usado pelo webhook e
pelo chat_local.py, para não duplicar essa lógica.
"""

from sqlalchemy.orm import Session

from . import admin, conversation


def processar_mensagem_recebida(db: Session, telefone: str, texto: str) -> str:
    if admin.eh_admin(telefone):
        resposta_admin = admin.tratar_comando_admin(db, texto)
        if resposta_admin is not None:
            return resposta_admin
    return conversation.processar_mensagem(db, telefone, texto)
