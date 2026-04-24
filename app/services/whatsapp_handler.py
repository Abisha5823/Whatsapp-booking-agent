import logging
from app.config import settings
from app.services.ai_assistant import process_message
from app.services.booking_manager import save_booking, get_or_create_session, update_session
from app.services.notification import notify_owner
from app.services.whatsapp_client import send_whatsapp_message
from app.utils.speech_to_text import transcribe_audio
from app.utils.validators import validate_phone_number

logger = logging.getLogger(__name__)

async def handle_whatsapp_message(message_data: dict):
    """Main handler for incoming WhatsApp messages"""
    
    try:
        # Extract customer number
        from_number = message_data.get("from")
        if not from_number:
            logger.warning("No 'from' field in message")
            return {"status": "ignored"}
        
        # Validate phone number
        if not validate_phone_number(from_number):
            logger.warning(f"Invalid phone number: {from_number}")
            return {"status": "invalid_number"}
        
        # Get message content
        msg_type = message_data.get("type")
        user_message = ""
        
        if msg_type == "text":
            user_message = message_data["text"]["body"]
            logger.info(f"Text from {from_number}: {user_message}")
            
        elif msg_type == "voice":
            logger.info(f"Voice note from {from_number}")
            media_id = message_data["voice"]["id"]
            transcription = await transcribe_audio(media_id)
            if transcription:
                user_message = transcription
                await send_whatsapp_message(from_number, f"🎤 I heard: \"{transcription}\"\n\nLet me help you with that!")
            else:
                await send_whatsapp_message(from_number, "Sorry, I couldn't understand the voice note. Could you please type your message? 📝")
                return {"status": "voice_failed"}
        else:
            await send_whatsapp_message(from_number, "Please send text messages for booking. I can help you with appointments! 😊")
            return {"status": "unsupported_type"}
        
        # Get or create session
        session = await get_or_create_session(from_number)
        
        # Process with AI
        ai_response = await process_message(
            user_message,
            session.get("conversation_history", []),
            session.get("current_state", {})
        )
        
        # Update session
        session["conversation_history"].append({"role": "user", "content": user_message, "timestamp": "now"})
        session["conversation_history"].append({"role": "assistant", "content": ai_response.get("reply", ""), "timestamp": "now"})
        
        # Keep only last 20 messages to avoid token limits
        if len(session["conversation_history"]) > 20:
            session["conversation_history"] = session["conversation_history"][-20:]
        
        session["current_state"] = {
            "step": ai_response.get("action", "ask"),
            "collected_fields": ai_response.get("collected", {}),
            "missing_fields": ai_response.get("missing", []),
            "last_intent": ai_response.get("intent", "")
        }
        
        await update_session(from_number, session)
        
        # Handle different actions
        action = ai_response.get("action", "ask")
        
        if action == "book":
            # Save booking to database
            booking_data = ai_response.get("booking_data", {})
            booking = await save_booking(booking_data, from_number)
            
            # Send confirmation message
            from datetime import datetime
            date_str = booking['preferred_date'].strftime('%B %d, %Y') if booking['preferred_date'] else 'To be confirmed'
            
            success_msg = f"""✅ *Booking Confirmed!*

*Booking ID:* {booking['booking_id']}
*Name:* {booking['customer_name']}
*Service:* {booking['service_type']}
*Mode:* {booking['mode']}
*Date:* {date_str}
*Time:* {booking['preferred_time'] or 'To be confirmed'}

📌 *Next Steps:*
• We'll send a reminder before your appointment
• Our team will contact you if needed
• Use this chat to reschedule or cancel

Thank you for choosing us! 🙏"""
            
            await send_whatsapp_message(from_number, success_msg)
            
            # Notify business owner
            await notify_owner(booking)
            
        elif action == "handoff":
            await send_whatsapp_message(from_number, "📞 *Connecting to Human Support*\n\nOur team will respond shortly. Please share any urgent details here.")
            # Notify owner about handoff request
            await send_whatsapp_message(settings.OWNER_WHATSAPP, f"⚠️ *Handoff Request*\nCustomer: {from_number}\nPlease check and respond.")
            
        elif action == "confirm":
            # Show summary and ask for confirmation
            response_text = ai_response.get("reply", "")
            await send_whatsapp_message(from_number, response_text)
            
        else:
            # Regular response (asking for information)
            response_text = ai_response.get("reply", "Could you please provide your name and service needed? 😊")
            await send_whatsapp_message(from_number, response_text)
        
        return {"status": "processed", "action": action}
        
    except Exception as e:
        logger.error(f"Error handling message: {str(e)}", exc_info=True)
        await send_whatsapp_message(from_number, "Sorry, I'm having trouble processing your request. Please try again or contact us directly. 😅")
        return {"status": "error", "error": str(e)}