import httpx

from .config import settings

GRAPH_API_BASE = "https://graph.facebook.com/v20.0"


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
