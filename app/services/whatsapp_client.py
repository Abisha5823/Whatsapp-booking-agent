import httpx
import logging
from app.config import settings

logger = logging.getLogger(__name__)

async def send_whatsapp_message(to: str, message: str):
    """Send message via WhatsApp Cloud API"""
    if not settings.WHATSAPP_TOKEN or not settings.WHATSAPP_PHONE_ID:
        logger.error("WhatsApp credentials not configured")
        return False
    
    url = f"https://graph.facebook.com/v18.0/{settings.WHATSAPP_PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Split long messages (WhatsApp limit ~1600 chars)
    if len(message) > 1500:
        parts = [message[i:i+1500] for i in range(0, len(message), 1500)]
        for part in parts:
            payload = {
                "messaging_product": "whatsapp",
                "to": to,
                "type": "text",
                "text": {"body": part}
            }
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.post(url, json=payload, headers=headers, timeout=10)
                    if response.status_code != 200:
                        logger.error(f"WhatsApp send failed: {response.text}")
                except Exception as e:
                    logger.error(f"HTTP error: {e}")
        return True
    
    # Send single message
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                logger.info(f"Message sent to {to}")
                return True
            else:
                logger.error(f"WhatsApp API error: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False