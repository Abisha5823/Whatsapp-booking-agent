from app.database.mongodb import get_db
from datetime import datetime
from typing import Dict, Optional, List
from datetime import timedelta
import uuid
import logging

logger = logging.getLogger(__name__)

async def save_booking(booking_data: Dict, whatsapp_number: str) -> Dict:
    """Save booking to MongoDB Atlas"""
    db = get_db()
    
    # Generate unique booking ID
    booking_id = str(uuid.uuid4())[:8].upper()
    
    # Parse date if provided
    preferred_date = None
    date_str = booking_data.get("preferred_date")
    if date_str:
        try:
            # Handle various date formats
            if date_str.lower() == "tomorrow":
                from datetime import timedelta
                preferred_date = datetime.utcnow() + timedelta(days=1)
            elif date_str.lower() == "today":
                preferred_date = datetime.utcnow()
            else:
                preferred_date = datetime.strptime(date_str, "%Y-%m-%d")
        except:
            preferred_date = None
    
    booking = {
        "booking_id": booking_id,
        "customer_name": booking_data.get("customer_name", ""),
        "whatsapp_number": whatsapp_number,
        "service_type": booking_data.get("service_type", ""),
        "reason_purpose": booking_data.get("reason", ""),
        "preferred_date": preferred_date,
        "preferred_time": booking_data.get("preferred_time", ""),
        "mode": booking_data.get("mode", "offline"),
        "language_preference": booking_data.get("language", "english"),
        "booking_status": "confirmed",
        "conversation_history": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "reminder_sent": False,
        "calendar_event_id": None,
        "notified_owner": False
    }
    
    try:
        result = await db.bookings.insert_one(booking)
        booking["_id"] = str(result.inserted_id)
        logger.info(f"Booking saved: {booking_id} for {whatsapp_number}")
        return booking
    except Exception as e:
        logger.error(f"Failed to save booking: {e}")
        raise

async def get_booking(booking_id: str) -> Optional[Dict]:
    """Get booking by ID"""
    db = get_db()
    booking = await db.bookings.find_one({"booking_id": booking_id})
    if booking:
        booking["_id"] = str(booking["_id"])
    return booking

async def get_bookings_by_customer(whatsapp_number: str, limit: int = 10) -> List[Dict]:
    """Get all bookings for a customer"""
    db = get_db()
    cursor = db.bookings.find({"whatsapp_number": whatsapp_number}).sort("created_at", -1).limit(limit)
    bookings = []
    async for booking in cursor:
        booking["_id"] = str(booking["_id"])
        bookings.append(booking)
    return bookings

async def update_booking_status(booking_id: str, status: str) -> bool:
    """Update booking status (confirmed, cancelled, completed)"""
    db = get_db()
    result = await db.bookings.update_one(
        {"booking_id": booking_id},
        {"$set": {"booking_status": status, "updated_at": datetime.utcnow()}}
    )
    return result.modified_count > 0

async def get_or_create_session(whatsapp_number: str) -> Dict:
    """Get or create conversation session"""
    db = get_db()
    
    session = await db.sessions.find_one({"whatsapp_number": whatsapp_number})
    
    if not session:
        session = {
            "whatsapp_number": whatsapp_number,
            "conversation_history": [],
            "current_state": {
                "step": "collecting",
                "collected_fields": {},
                "missing_fields": ["name", "service", "mode", "date", "time"],
                "last_question": "name"
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = await db.sessions.insert_one(session)
        session["_id"] = str(result.inserted_id)
        logger.info(f"New session created for {whatsapp_number}")
    else:
        session["_id"] = str(session["_id"])
        # Initialize current_state if missing
        if "current_state" not in session:
            session["current_state"] = {
                "step": "collecting",
                "collected_fields": {},
                "missing_fields": ["name", "service", "mode", "date", "time"],
                "last_question": "name"
            }
    
    return session

async def update_session(whatsapp_number: str, session: Dict):
    """Update existing session"""
    db = get_db()
    session["updated_at"] = datetime.utcnow()
    
    # Remove _id for update
    session_copy = session.copy()
    session_copy.pop("_id", None)
    
    await db.sessions.update_one(
        {"whatsapp_number": whatsapp_number},
        {"$set": session_copy},
        upsert=True
    )
    logger.info(f"Session updated for {whatsapp_number} - Step: {session.get('current_state', {}).get('step')}")

async def delete_old_sessions(days: int = 7):
    """Delete sessions older than specified days"""
    db = get_db()
    cutoff = datetime.utcnow() - timedelta(days=days)
    result = await db.sessions.delete_many({"updated_at": {"$lt": cutoff}})
    logger.info(f"Deleted {result.deleted_count} old sessions")