from datetime import datetime, timedelta
import json
import logging
from app.config import settings

logger = logging.getLogger(__name__)

# Simplified version - Google Calendar optional
async def create_calendar_event(booking: dict) -> str:
    """Create event in Google Calendar (Optional feature)"""
    if not settings.GOOGLE_CALENDAR_ENABLED:
        logger.info("Google Calendar disabled")
        return None
    
    try:
        # Placeholder for Google Calendar integration
        # You'll need to add google-auth and google-api-python-client
        # For now, just return mock event ID
        event_id = f"mock_{booking['booking_id']}"
        logger.info(f"Mock calendar event created: {event_id}")
        return event_id
    except Exception as e:
        logger.error(f"Calendar creation failed: {e}")
        return None

async def get_available_slots(date: datetime, business_settings: dict) -> list:
    """Get available time slots for a specific date"""
    # Simple slot generation for MVP
    slots = []
    start_hour = 9
    end_hour = 20
    
    current_time = datetime.combine(date, datetime.min.time()) + timedelta(hours=start_hour)
    end_time = datetime.combine(date, datetime.min.time()) + timedelta(hours=end_hour)
    
    while current_time < end_time:
        slot = current_time.strftime("%I:%M %p")
        slots.append(slot)
        current_time += timedelta(minutes=settings.SLOT_DURATION)
    
    # Remove common break times (1-2 PM lunch)
    slots = [s for s in slots if not (s.startswith("01:") or s.startswith("01:") or s == "02:00 PM")]
    
    return slots[:10]  # Return first 10 slots