from datetime import datetime, timedelta
from typing import List, Optional

def generate_time_slots(
    start_time: str = "09:00",
    end_time: str = "20:00",
    slot_duration: int = 30
) -> List[str]:
    """Generate time slots between start and end time"""
    slots = []
    start = datetime.strptime(start_time, "%H:%M")
    end = datetime.strptime(end_time, "%H:%M")
    
    current = start
    while current < end:
        slot = current.strftime("%I:%M %p")
        slots.append(slot)
        current += timedelta(minutes=slot_duration)
    
    return slots

def parse_date(date_string: str) -> Optional[datetime]:
    """Parse various date formats"""
    date_string = date_string.lower().strip()
    
    if date_string == "today":
        return datetime.utcnow()
    elif date_string == "tomorrow":
        return datetime.utcnow() + timedelta(days=1)
    elif date_string == "day after tomorrow":
        return datetime.utcnow() + timedelta(days=2)
    
    # Try different formats
    formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%B %d, %Y",
        "%d %B %Y"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except:
            continue
    
    return None

def format_datetime_for_display(dt: datetime) -> str:
    """Format datetime for display to customer"""
    if dt.date() == datetime.utcnow().date():
        return f"Today at {dt.strftime('%I:%M %p')}"
    elif dt.date() == (datetime.utcnow() + timedelta(days=1)).date():
        return f"Tomorrow at {dt.strftime('%I:%M %p')}"
    else:
        return dt.strftime("%B %d at %I:%M %p")