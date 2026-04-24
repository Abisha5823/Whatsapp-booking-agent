from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import logging
from app.database.mongodb import get_db
from app.services.whatsapp_handler import send_whatsapp_message
from app.config import settings
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import logging
from app.database.mongodb import get_db
from app.services.whatsapp_client import send_whatsapp_message
from app.config import settings
logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

async def send_reminders():
    """Send reminders for upcoming appointments"""
    db = get_db()
    now = datetime.utcnow()
    
    # Find appointments in next 24 hours that haven't had reminder sent
    tomorrow = now + timedelta(hours=24)
    
    query = {
        "preferred_date": {"$gte": now, "$lte": tomorrow},
        "reminder_sent": False,
        "booking_status": "confirmed"
    }
    
    cursor = db.bookings.find(query)
    reminders_sent = 0
    
    async for booking in cursor:
        # Calculate appointment time
        appt_time = booking["preferred_date"]
        if booking.get("preferred_time"):
            time_parts = booking["preferred_time"].replace(" ", "").split(":")
            hour = int(time_parts[0])
            if "PM" in booking["preferred_time"] and hour != 12:
                hour += 12
            appt_time = appt_time.replace(hour=hour, minute=0)
        
        # Calculate hours until appointment
        hours_until = (appt_time - now).total_seconds() / 3600
        
        # Send reminder if between 2-24 hours before
        if 2 <= hours_until <= 24:
            reminder_msg = f"""🔔 *Appointment Reminder*

Hello {booking['customer_name']}!

Your appointment is *tomorrow* at {booking['preferred_time']}

*Service:* {booking['service_type']}
*Mode:* {booking['mode']}

📍 Location: {settings.OWNER_WHATSAPP} (text for address)

Need to reschedule? Just reply here!

Thank you 🙏"""
            
            await send_whatsapp_message(booking["whatsapp_number"], reminder_msg)
            
            # Mark reminder as sent
            await db.bookings.update_one(
                {"_id": booking["_id"]},
                {"$set": {"reminder_sent": True}}
            )
            reminders_sent += 1
            logger.info(f"Reminder sent for booking {booking['booking_id']}")
    
    if reminders_sent > 0:
        logger.info(f"Sent {reminders_sent} reminders")

async def send_followups():
    """Send follow-up messages after appointments"""
    db = get_db()
    now = datetime.utcnow()
    
    # Find appointments from yesterday
    yesterday = now - timedelta(days=1)
    day_before = now - timedelta(days=2)
    
    query = {
        "preferred_date": {"$gte": day_before, "$lte": yesterday},
        "booking_status": "completed",
        "followup_sent": {"$ne": True}
    }
    
    cursor = db.bookings.find(query)
    
    async for booking in cursor:
        followup_msg = f"""⭐ *How was your experience?*

Hello {booking['customer_name']}, hope your appointment went well!

Would you like to:
1️⃣ Book a follow-up
2️⃣ Leave feedback
3️⃣ No further action

Reply with 1, 2, or 3 😊"""
        
        await send_whatsapp_message(booking["whatsapp_number"], followup_msg)
        
        await db.bookings.update_one(
            {"_id": booking["_id"]},
            {"$set": {"followup_sent": True}}
        )
        logger.info(f"Follow-up sent for booking {booking['booking_id']}")

def start_reminder_scheduler():
    """Start the reminder scheduler"""
    try:
        # Run every hour
        scheduler.add_job(send_reminders, CronTrigger(minute=0))
        scheduler.add_job(send_followups, CronTrigger(hour=10, minute=0))
        scheduler.start()
        logger.info("Reminder scheduler started")
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")

def stop_reminder_scheduler():
    """Stop the reminder scheduler"""
    scheduler.shutdown()
    logger.info("Reminder scheduler stopped")