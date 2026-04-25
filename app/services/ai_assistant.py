import logging
from typing import Dict, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

async def process_message(user_message: str, conversation_history: List[Dict], current_state: Dict) -> Dict:
    """Simple rule-based assistant (no API key needed)"""
    
    collected = current_state.get("collected_fields", {})
    user_lower = user_message.lower()
    
    # Check if confirming
    if current_state.get("step") == "awaiting_confirmation":
        if "yes" in user_lower or "confirm" in user_lower or "ok" in user_lower:
            return {
                "reply": "✅ Booking confirmed! We'll send a reminder before your appointment.\n\nThank you for choosing us! 🙏",
                "action": "book",
                "booking_data": collected
            }
        else:
            return {
                "reply": "No problem! Let's start over. What's your name? 😊",
                "action": "ask",
                "collected": {},
                "missing": ["name", "service", "mode", "date", "time"]
            }
    
    # Collect information in order
    if "name" not in collected:
        return {
            "reply": "I'll help you book an appointment. May I know your name? 😊",
            "action": "ask",
            "collected": {"name": user_message},
            "missing": ["service", "mode", "date", "time"]
        }
    
    elif "service" not in collected:
        return {
            "reply": f"Nice to meet you {collected['name']}! What service do you need? (Consultation/Therapy/Follow-up)",
            "action": "ask",
            "collected": {"name": collected['name'], "service": user_message},
            "missing": ["mode", "date", "time"]
        }
    
    elif "mode" not in collected:
        mode = "online" if "online" in user_lower else "offline" if "offline" in user_lower or "person" in user_lower else None
        if mode:
            return {
                "reply": "Great! When would you like to come? (e.g., tomorrow, Monday, or specific date)",
                "action": "ask",
                "collected": {"name": collected['name'], "service": collected['service'], "mode": mode},
                "missing": ["date", "time"]
            }
        else:
            return {
                "reply": "Do you prefer online or in-person consultation?",
                "action": "ask",
                "collected": collected,
                "missing": ["mode", "date", "time"]
            }
    
    elif "date" not in collected:
        return {
            "reply": "Available slots: 9:00 AM, 11:00 AM, 2:00 PM, 4:00 PM, 6:00 PM. Which time works for you?",
            "action": "ask",
            "collected": {"name": collected['name'], "service": collected['service'], "mode": collected['mode'], "date": user_message},
            "missing": ["time"]
        }
    
    elif "time" not in collected:
        # Show summary and ask for confirmation
        summary = f"""📋 *Booking Summary*

Name: {collected['name']}
Service: {collected['service']}
Mode: {collected['mode']}
Date: {collected.get('date', 'TBD')}
Time: {user_message}

Confirm pannalama? 😊 (Reply 'Yes' to confirm)"""
        
        collected['time'] = user_message
        
        return {
            "reply": summary,
            "action": "confirm",
            "collected": collected,
            "missing": []
        }
    
    # Fallback
    return {
        "reply": "I'll help you book an appointment. What's your name? 😊",
        "action": "ask",
        "collected": {},
        "missing": ["name", "service", "mode", "date", "time"]
    }