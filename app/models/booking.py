from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class Booking(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    booking_id: str
    customer_name: str
    whatsapp_number: str
    service_type: str
    reason_purpose: Optional[str] = ""
    preferred_date: Optional[datetime] = None
    preferred_time: Optional[str] = None
    mode: str = "offline"  # online/offline
    language_preference: str = "english"
    booking_status: str = "pending"  # pending, confirmed, cancelled, completed
    conversation_history: List[dict] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    reminder_sent: bool = False
    calendar_event_id: Optional[str] = None
    notified_owner: bool = False
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        populate_by_name = True

class Session(BaseModel):
    whatsapp_number: str
    conversation_history: List[dict] = []
    current_state: dict = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)