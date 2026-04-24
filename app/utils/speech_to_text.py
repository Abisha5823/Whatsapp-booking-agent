import httpx
import logging
from app.config import settings

logger = logging.getLogger(__name__)

async def transcribe_audio(media_id: str) -> str:
    """
    Convert voice note to text using WhatsApp's media endpoint
    For MVP, just return None - text only
    """
    # For MVP, voice notes are not fully implemented
    # You can add OpenAI Whisper or Google Speech-to-Text later
    logger.info(f"Voice note received but transcription not implemented yet: {media_id}")
    return None

async def download_media(media_id: str) -> bytes:
    """Download media from WhatsApp servers"""
    url = f"https://graph.facebook.com/v18.0/{media_id}"
    headers = {"Authorization": f"Bearer {settings.WHATSAPP_TOKEN}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            media_url = response.json().get("url")
            if media_url:
                media_response = await client.get(media_url, headers=headers)
                return media_response.content
    return None