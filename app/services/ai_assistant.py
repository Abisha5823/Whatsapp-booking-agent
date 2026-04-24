import google.generativeai as genai
from typing import Dict, List
import json
import re
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Configure Gemini
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
else:
    logger.warning("GEMINI_API_KEY not set. AI features will use fallback responses.")
    model = None

SYSTEM_PROMPT = """You are a friendly booking assistant for local businesses (clinics, salons, tutors, fitness trainers, etc.).

**YOUR PERSONALITY:**
- Friendly, warm, and helpful like a local shop assistant
- Use simple English with occasional Tanglish (Tamil+English) like "unga name solunga", "confirm pannalama?", "super!"
- Never say "I am an AI" - always say "I'll help you book your appointment"
- Use emojis appropriately 😊 👍 ✅ 🎉
- Be patient and kind

**YOUR TASK:**
Collect booking details in this order:
1. customer_name (Ask: "May I know your name please?")
2. service_type (Ask: "What service do you need?")
3. mode (Ask: "Online or in-person? Ungaluku ethu comfortable?")
4. preferred_date (Ask: "Which date would you prefer?")
5. preferred_time (After getting date, show available slots)
6. reason_purpose (Ask: "Briefly, what's the reason for your visit?")
7. language_preference (Ask: "Language preference? English / Tamil / Tanglish?")

**AVAILABLE SLOTS (9 AM - 8 PM, 30-min slots):**
Generate realistic slots for the date: 9:00 AM, 9:30 AM, 10:00 AM, 10:30 AM, 11:00 AM, 11:30 AM, 2:00 PM, 2:30 PM, 3:00 PM, 3:30 PM, 4:00 PM, 4:30 PM, 5:00 PM, 5:30 PM, 6:00 PM, 6:30 PM, 7:00 PM, 7:30 PM

**RULES:**
- Only ask for missing information, don't repeat what you already have
- After collecting all 7 details, show a summary and ask "Confirm pannalama? 😊"
- If customer says "no", "change", "modify", help them update specific fields
- If customer asks for human, say "Sure! Connecting you to our team"

**RESPONSE FORMAT (JSON):**
{
    "reply": "Your response text here",
    "action": "ask|confirm|book|handoff",
    "collected": {"field": "value"},
    "missing": ["field1", "field2"],
    "intent": "booking|cancel|reschedule|handoff",
    "booking_data": {} // Only for action="book"
}

**EXAMPLE FLOW:**

Customer: I need consultation for stress tomorrow evening
Response: {
    "reply": "Sure 😊 I'll help you book. May I know your name?",
    "action": "ask",
    "collected": {"service_type": "stress consultation", "preferred_date": "tomorrow"},
    "missing": ["customer_name", "mode", "preferred_time"]
}

Customer: Abisha
Response: {
    "reply": "Nice to meet you Abisha! 😊 Do you prefer online or in-person consultation?",
    "action": "ask",
    "collected": {"customer_name": "Abisha"},
    "missing": ["mode", "preferred_time"]
}

Customer: Online
Response: {
    "reply": "Available slots for tomorrow: 5:00 PM, 6:30 PM, 7:30 PM. Which one do you prefer?",
    "action": "ask",
    "collected": {"mode": "online"},
    "missing": ["preferred_time"]
}

Customer: 6:30
Response: {
    "reply": "Perfect! Now, briefly, what's the reason for your consultation?",
    "action": "ask",
    "collected": {"preferred_time": "6:30 PM"},
    "missing": ["reason_purpose", "language_preference"]
}

Customer: Stress and anxiety
Response: {
    "reply": "Got it. Last question - language preference? English / Tamil / Tanglish?",
    "action": "ask",
    "collected": {"reason_purpose": "Stress and anxiety"},
    "missing": ["language_preference"]
}

Customer: Tamil
Response: {
    "reply": "Booking summary:\nName: Abisha\nService: Stress consultation\nMode: Online\nDate: Tomorrow\nTime: 6:30 PM\nReason: Stress and anxiety\nLanguage: Tamil\n\nConfirm pannalama? 😊",
    "action": "confirm",
    "collected": {"language_preference": "Tamil"},
    "missing": []
}

Customer: Yes
Response: {
    "reply": "Your booking is confirmed! Our team will contact you if needed.",
    "action": "book",
    "booking_data": {
        "customer_name": "Abisha",
        "service_type": "stress consultation",
        "mode": "online",
        "preferred_date": "2024-01-20",
        "preferred_time": "18:30",
        "reason": "Stress and anxiety",
        "language": "Tamil"
    }
}"""

async def process_message(user_message: str, conversation_history: List[Dict], current_state: Dict) -> Dict:
    """Process user message using Gemini AI (Free)"""
    
    # Fallback if Gemini not configured
    if not model:
        return fallback_response(user_message, current_state)
    
    try:
        # Build context from conversation history
        recent_history = conversation_history[-10:] if conversation_history else []
        history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_history])
        
        # Build the prompt
        full_prompt = f"""{SYSTEM_PROMPT}

**Current State:**
Already collected: {json.dumps(current_state.get('collected_fields', {}))}
Missing fields: {current_state.get('missing_fields', [])}

**Conversation History:**
{history_text}

**Current User Message:**
Customer: {user_message}

**Respond with JSON only (no other text):**"""
        
        # Call Gemini API
        response = model.generate_content(full_prompt)
        
        # Parse JSON response
        result_text = response.text.strip()
        
        # Extract JSON if wrapped in markdown
        if '```json' in result_text:
            result_text = result_text.split('```json')[1].split('```')[0].strip()
        elif '```' in result_text:
            result_text = result_text.split('```')[1].strip()
        
        result = json.loads(result_text)
        
        # Ensure required fields
        if "reply" not in result:
            result["reply"] = "Could you please provide that again? 😊"
        if "action" not in result:
            result["action"] = "ask"
        if "collected" not in result:
            result["collected"] = {}
        if "missing" not in result:
            result["missing"] = []
        
        return result
        
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return fallback_response(user_message, current_state)

def fallback_response(user_message: str, current_state: Dict) -> Dict:
    """Fallback rule-based responses when AI is unavailable"""
    
    collected = current_state.get('collected_fields', {})
    user_lower = user_message.lower()
    
    # Simple rule-based logic
    if 'name' not in collected:
        return {
            "reply": "May I know your name please? 😊",
            "action": "ask",
            "collected": {},
            "missing": ["name", "service", "date"]
        }
    
    elif 'service_type' not in collected:
        return {
            "reply": "What service do you need? (Consultation, Therapy, Follow-up, etc.)",
            "action": "ask",
            "collected": collected,
            "missing": ["service_type", "date"]
        }
    
    elif 'date' not in collected:
        if 'tomorrow' in user_lower or 'today' in user_lower:
            return {
                "reply": "Great! Available slots: 10:00 AM, 2:00 PM, 4:30 PM, 6:00 PM. Which time works for you?",
                "action": "ask",
                "collected": {**collected, "date": "tomorrow"},
                "missing": ["time"]
            }
        else:
            return {
                "reply": "Which date would you prefer? (e.g., tomorrow, Monday, or specific date)",
                "action": "ask",
                "collected": collected,
                "missing": ["date", "time"]
            }
    
    elif 'time' not in collected:
        return {
            "reply": "Please select a time: 10:00 AM, 2:00 PM, 4:30 PM, or 6:00 PM?",
            "action": "ask",
            "collected": collected,
            "missing": ["time"]
        }
    
    else:
        # All fields collected, confirm booking
        return {
            "reply": f"Booking summary:\nName: {collected.get('name', 'Unknown')}\nService: {collected.get('service_type', 'Unknown')}\nDate: {collected.get('date', 'TBD')}\nTime: {collected.get('time', 'TBD')}\n\nConfirm pannalama? 😊",
            "action": "confirm",
            "collected": collected,
            "missing": [],
            "booking_data": {
                "customer_name": collected.get('name', ''),
                "service_type": collected.get('service_type', ''),
                "mode": "offline",
                "preferred_date": "2024-01-20",
                "preferred_time": collected.get('time', ''),
                "reason": collected.get('reason', '')
            }
        }