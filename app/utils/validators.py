import re

def validate_phone_number(phone: str) -> bool:
    """Validate international phone number format"""
    # Remove any non-digit characters
    cleaned = re.sub(r'\D', '', phone)
    
    # Check length (should be 10-15 digits)
    if 10 <= len(cleaned) <= 15:
        return True
    return False

def validate_email(email: str) -> bool:
    """Basic email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_time_slot(time_str: str) -> bool:
    """Validate time format (e.g., '14:30' or '2:30 PM')"""
    patterns = [
        r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$',  # 24-hour
        r'^([1-9]|1[0-2]):[0-5][0-9]\s?(AM|PM)$'  # 12-hour with AM/PM
    ]
    
    for pattern in patterns:
        if re.match(pattern, time_str, re.IGNORECASE):
            return True
    return False