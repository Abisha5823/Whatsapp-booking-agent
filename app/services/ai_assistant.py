import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

async def process_message(user_message: str, conversation_history: List[Dict], current_state: Dict) -> Dict:
    """Improved rule-based assistant with better state tracking"""
    
    # Get current collected fields and step
    collected = current_state.get("collected_fields", {})
    last_question = current_state.get("last_question", "name")
    user_lower = user_message.lower().strip()
    
    logger.info(f"State: collected={collected}, last_question={last_question}")
    logger.info(f"User message: {user_message}")
    
    # Check for confirmation
    if last_question == "confirm" or current_state.get("step") == "awaiting_confirmation":
        if any(word in user_lower for word in ["yes", "confirm", "ok", "yeah", "sure", "correct", "ya", "y"]):
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
                "missing": ["name", "service", "mode", "date", "time"],
                "last_question": "name",
                "step": "collecting"
            }
    
    # Collect information in order
    # Step 1: Get name
    if not collected.get("name"):
        name = user_message if not any(word in user_lower for word in ["hi", "hello", "need", "appointment", "consultation"]) else None
        
        if name and len(name) > 1 and not any(word in name.lower() for word in ["i need", "consultation", "therapy"]):
            return {
                "reply": f"Nice to meet you {name}! What service do you need?\n(Consultation / Therapy / Stress relief / Follow-up)",
                "action": "ask",
                "collected": {"name": name},
                "missing": ["service", "mode", "date", "time"],
                "last_question": "service",
                "step": "collecting"
            }
        else:
            return {
                "reply": "I'll help you book an appointment. May I know your name? 😊",
                "action": "ask",
                "collected": collected,
                "missing": ["name", "service", "mode", "date", "time"],
                "last_question": "name",
                "step": "collecting"
            }
    
    # Step 2: Get service
    if not collected.get("service"):
        if not any(word in user_lower for word in ["online", "offline", "in-person", "tomorrow", "today", "monday", "am", "pm"]):
            return {
                "reply": f"What service do you need? (Consultation / Therapy / Stress relief / Follow-up)",
                "action": "ask",
                "collected": {**collected, "service": user_message},
                "missing": ["mode", "date", "time"],
                "last_question": "mode",
                "step": "collecting"
            }
        else:
            return {
                "reply": "What service do you need? (Consultation / Therapy / Stress relief)",
                "action": "ask",
                "collected": collected,
                "missing": ["service", "mode", "date", "time"],
                "last_question": "service",
                "step": "collecting"
            }
    
    # Step 3: Get mode (online/offline)
    if not collected.get("mode"):
        if "online" in user_lower:
            mode = "online"
            reply = "Great! When would you like to come? (e.g., tomorrow, Monday, or a specific date)"
            return {
                "reply": reply,
                "action": "ask",
                "collected": {**collected, "mode": mode},
                "missing": ["date", "time"],
                "last_question": "date",
                "step": "collecting"
            }
        elif "offline" in user_lower or "in-person" in user_lower or "person" in user_lower:
            mode = "offline"
            reply = "Great! When would you like to visit us? (e.g., tomorrow, Monday, or a specific date)"
            return {
                "reply": reply,
                "action": "ask",
                "collected": {**collected, "mode": mode},
                "missing": ["date", "time"],
                "last_question": "date",
                "step": "collecting"
            }
        else:
            return {
                "reply": "Do you prefer online or in-person consultation?",
                "action": "ask",
                "collected": collected,
                "missing": ["mode", "date", "time"],
                "last_question": "mode",
                "step": "collecting"
            }
    
    # Step 4: Get date
    if not collected.get("date"):
        return {
            "reply": "Available slots: 9:00 AM, 11:00 AM, 2:00 PM, 4:00 PM, 6:00 PM. Which time works for you?",
            "action": "ask",
            "collected": {**collected, "date": user_message},
            "missing": ["time"],
            "last_question": "time",
            "step": "collecting"
        }
    
    # Step 5: Get time and confirm
    if not collected.get("time"):
        collected["time"] = user_message
        
        summary = f"""📋 *Booking Summary*

Name: {collected.get('name', 'Unknown')}
Service: {collected.get('service', 'Unknown')}
Mode: {collected.get('mode', 'Unknown')}
Date: {collected.get('date', 'Unknown')}
Time: {user_message}

Confirm pannalama? 😊 (Reply 'Yes' to confirm)"""
        
        return {
            "reply": summary,
            "action": "confirm",
            "collected": collected,
            "missing": [],
            "last_question": "confirm",
            "step": "awaiting_confirmation"
        }
    
    # Fallback - shouldn't reach here
    return {
        "reply": "I'll help you book an appointment. What's your name? 😊",
        "action": "ask",
        "collected": {},
        "missing": ["name", "service", "mode", "date", "time"],
        "last_question": "name",
        "step": "collecting"
    }