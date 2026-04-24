from fastapi import APIRouter, Request, HTTPException, Query
from app.services.whatsapp_handler import handle_whatsapp_message
from app.config import settings
import logging
import json

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/verify")
async def verify_webhook(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_verify_token: str = Query(..., alias="hub.verify_token"),
    hub_challenge: int = Query(..., alias="hub.challenge")
):
    """WhatsApp webhook verification endpoint"""
    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        logger.info("Webhook verified successfully")
        return hub_challenge
    else:
        logger.warning(f"Webhook verification failed: token mismatch")
        raise HTTPException(status_code=403, detail="Verification failed")

@router.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    """Main webhook endpoint for WhatsApp messages"""
    try:
        body = await request.json()
        logger.info(f"Received webhook: {json.dumps(body, indent=2)}")
        
        # Check if this is a WhatsApp message event
        if body.get("object") == "whatsapp_business_account":
            for entry in body.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    
                    # Process messages
                    if "messages" in value:
                        for message in value["messages"]:
                            await handle_whatsapp_message(message)
                    
                    # Process status updates (delivered, read)
                    elif "statuses" in value:
                        logger.info(f"Status update: {value['statuses']}")
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))