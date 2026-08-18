from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from . import admin, conversation, whatsapp
from .config import settings
from .database import get_db

router = APIRouter()


@router.get("/webhook")
async def verificar_webhook(request: Request) -> Response:
    """Endpoint de verificação exigido pela Meta ao cadastrar a URL do webhook."""
    params = request.query_params
    if (
        params.get("hub.mode") == "subscribe"
        and params.get("hub.verify_token") == settings.whatsapp_verify_token
    ):
        return Response(content=params.get("hub.challenge", ""), media_type="text/plain")
    return Response(status_code=403)


@router.post("/webhook")
async def receber_mensagem(request: Request, db: Session = Depends(get_db)) -> dict:
    payload = await request.json()

    for entrada in payload.get("entry", []):
        for mudanca in entrada.get("changes", []):
            valor = mudanca.get("value", {})
            for mensagem in valor.get("messages", []):
                telefone = mensagem.get("from")
                texto = mensagem.get("text", {}).get("body", "")
                if not telefone:
                    continue

                if admin.eh_admin(telefone):
                    resposta_admin = admin.tratar_comando_admin(texto)
                    if resposta_admin is not None:
                        await whatsapp.enviar_mensagem_texto(telefone, resposta_admin)
                        continue

                resposta = conversation.processar_mensagem(db, telefone, texto)
                await whatsapp.enviar_mensagem_texto(telefone, resposta)

    return {"status": "ok"}
