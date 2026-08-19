from pathlib import Path

import httpx

from .config import settings

GRAPH_API_BASE = "https://graph.facebook.com/v20.0"

MIME_TYPE_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


async def enviar_mensagem_texto(telefone: str, texto: str) -> None:
    url = f"{GRAPH_API_BASE}/{settings.whatsapp_phone_number_id}/messages"
    headers = {"Authorization": f"Bearer {settings.whatsapp_token}"}
    payload = {
        "messaging_product": "whatsapp",
        "to": telefone,
        "type": "text",
        "text": {"body": texto},
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()


async def _subir_midia(caminho: Path, mime_type: str) -> str:
    """Envia um arquivo pro WhatsApp e retorna o media_id, usado depois pra anexar numa mensagem."""
    url = f"{GRAPH_API_BASE}/{settings.whatsapp_phone_number_id}/media"
    headers = {"Authorization": f"Bearer {settings.whatsapp_token}"}
    async with httpx.AsyncClient() as client:
        with open(caminho, "rb") as arquivo:
            files = {"file": (caminho.name, arquivo, mime_type)}
            data = {"messaging_product": "whatsapp"}
            response = await client.post(url, headers=headers, files=files, data=data)
        response.raise_for_status()
        return response.json()["id"]


async def enviar_documento(telefone: str, caminho: Path, legenda: str = "") -> None:
    """Sobe o arquivo e manda como documento anexado numa mensagem do WhatsApp."""
    media_id = await _subir_midia(caminho, MIME_TYPE_XLSX)

    url = f"{GRAPH_API_BASE}/{settings.whatsapp_phone_number_id}/messages"
    headers = {"Authorization": f"Bearer {settings.whatsapp_token}"}
    payload = {
        "messaging_product": "whatsapp",
        "to": telefone,
        "type": "document",
        "document": {
            "id": media_id,
            "filename": caminho.name,
            "caption": legenda,
        },
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
