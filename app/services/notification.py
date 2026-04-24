import logging
from app.config import settings
from app.services.whatsapp_client import send_whatsapp_message
from app.database.mongodb import get_db

logger = logging.getLogger(__name__)

async def notify_owner(booking: dict):
    """Notify business owner about new booking"""
    if not settings.OWNER_WHATSAPP:
        logger.warning("Owner WhatsApp number not configured")
        return
    
    # Format date nicely
    date_str = "N/A"
    if booking.get("preferred_date"):
        date_str = booking["preferred_date"].strftime("%B %d, %Y")
    
    message = f"""📅 *NEW BOOKING ALERT!*

*Booking ID:* {booking['booking_id']}
*Customer:* {booking['customer_name']}
*WhatsApp:* {booking['whatsapp_number']}
*Service:* {booking['service_type']}
*Date:* {date_str}
*Time:* {booking.get('preferred_time', 'TBD')}
*Mode:* {booking['mode']}
*Language:* {booking.get('language_preference', 'English')}

*Reason:* {booking.get('reason_purpose', 'Not provided')[:100]}

✅ Booking confirmed automatically

To cancel or modify, contact the customer directly via WhatsApp."""
    
    success = await send_whatsapp_message(settings.OWNER_WHATSAPP, message)
    
    if success:
        # Update booking as notified
        db = get_db()
        await db.bookings.update_one(
            {"booking_id": booking['booking_id']},
            {"$set": {"notified_owner": True}}
        )
        logger.info(f"Owner notified for booking {booking['booking_id']}")
    else:
        logger.warning(f"Failed to notify owner for {booking['booking_id']}")