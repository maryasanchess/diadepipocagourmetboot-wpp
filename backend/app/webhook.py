from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from . import whatsapp
from .config import settings
from .database import get_db
from .dispatcher import processar_mensagem_recebida

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

                resposta = processar_mensagem_recebida(db, telefone, texto)
                await whatsapp.enviar_mensagem_texto(telefone, resposta.texto)
                if resposta.anexo is not None:
                    await whatsapp.enviar_documento(telefone, resposta.anexo)

    return {"status": "ok"}
