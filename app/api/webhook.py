from fastapi import APIRouter, Request, HTTPException, Query
from app.services.whatsapp_handler import handle_whatsapp_message
from app.config import settings
import logging
import json

router = APIRouter()
logger = logging.getLogger(__name__)

# Verification endpoint for Meta (works on both paths)
@router.get("/verify")
@router.get("/whatsapp")  # Also handle GET on /whatsapp for verification
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: int = Query(None, alias="hub.challenge")
):
    """WhatsApp webhook verification endpoint"""
    
    logger.info(f"Verification attempt - Mode: {hub_mode}, Token: {hub_verify_token}, Challenge: {hub_challenge}")
    
    # If no parameters, just return 200 (health check)
    if hub_mode is None:
        return {"status": "ok", "message": "Webhook endpoint is active"}
    
    # Check all required parameters are present
    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        logger.info("✅ Webhook verified successfully")
        return hub_challenge
    else:
        logger.warning(f"❌ Verification failed - Token mismatch")
        raise HTTPException(status_code=403, detail="Verification failed")

@router.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    """Main webhook endpoint for WhatsApp messages (POST only)"""
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
                    
                    # Process status updates
                    elif "statuses" in value:
                        logger.info(f"Status update: {value['statuses']}")
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))