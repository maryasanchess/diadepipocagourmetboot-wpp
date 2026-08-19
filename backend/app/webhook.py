import logging

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from . import whatsapp
from .config import settings
from .database import get_db
from .dispatcher import processar_mensagem_recebida

logger = logging.getLogger("pipocabot.webhook")
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
    """
    Sempre responde 200 pra Meta, mesmo se alguma mensagem individual der
    erro — a Meta reenvia (com retry automático) qualquer webhook que não
    responda 2xx, e como um POST pode trazer várias mensagens de clientes
    diferentes numa lista só, deixar uma exceção subir derrubaria a
    resposta pra todo mundo do lote e ainda geraria reprocessamento
    duplicado no reenvio.
    """
    try:
        payload = await request.json()
    except Exception:
        logger.exception("Corpo do POST /webhook não é um JSON válido")
        return {"status": "ok"}

    if not isinstance(payload, dict):
        logger.warning("Corpo do POST /webhook não é um objeto JSON: %r", payload)
        return {"status": "ok"}

    for entrada in payload.get("entry", []):
        for mudanca in entrada.get("changes", []):
            valor = mudanca.get("value", {})
            for mensagem in valor.get("messages", []):
                telefone = mensagem.get("from")
                texto = mensagem.get("text", {}).get("body", "")
                if not telefone:
                    continue

                try:
                    resposta = processar_mensagem_recebida(db, telefone, texto)
                    await whatsapp.enviar_mensagem_texto(telefone, resposta.texto)
                    if resposta.anexo is not None:
                        await whatsapp.enviar_documento(telefone, resposta.anexo)
                except Exception:
                    db.rollback()
                    logger.exception("Falha ao processar mensagem de %s", telefone)

    return {"status": "ok"}
