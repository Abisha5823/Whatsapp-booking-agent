from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # WhatsApp Business API
    WHATSAPP_TOKEN: str = os.getenv("WHATSAPP_TOKEN", "")
    WHATSAPP_VERIFY_TOKEN: str = os.getenv("WHATSAPP_VERIFY_TOKEN", "mySecretVerifyToken123")
    WHATSAPP_PHONE_ID: str = os.getenv("WHATSAPP_PHONE_ID", "")
    
    # MongoDB Atlas
    MONGODB_URL: str = os.getenv("MONGODB_URL") or os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "booking_assistant")
    
    # AI - Google Gemini
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Owner Notification
    OWNER_WHATSAPP: str = os.getenv("OWNER_WHATSAPP", "")
    OWNER_EMAIL: Optional[str] = os.getenv("OWNER_EMAIL", None)
    
    # Redis (Optional)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    USE_REDIS: bool = False  # Set to False for MVP
    
    # Google Calendar (Optional)
    GOOGLE_CALENDAR_ENABLED: bool = os.getenv("GOOGLE_CALENDAR_ENABLED", "False").lower() == "true"
    GOOGLE_CALENDAR_CREDENTIALS: str = os.getenv("GOOGLE_CALENDAR_CREDENTIALS", "{}")
    GOOGLE_CALENDAR_ID: str = os.getenv("GOOGLE_CALENDAR_ID", "primary")
    
    # Business Settings
    SLOT_DURATION: int = int(os.getenv("SLOT_DURATION", "30"))
    WORKING_HOURS_START: str = os.getenv("WORKING_HOURS_START", "09:00")
    WORKING_HOURS_END: str = os.getenv("WORKING_HOURS_END", "20:00")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()