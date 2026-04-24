from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class WhatsAppText(BaseModel):
    body: str

class WhatsAppVoice(BaseModel):
    id: str
    mime_type: str

class WhatsAppMessage(BaseModel):
    from_: str
    id: str
    timestamp: str
    type: str
    text: Optional[WhatsAppText] = None
    voice: Optional[WhatsAppVoice] = None

class WhatsAppChange(BaseModel):
    value: Dict[str, Any]
    field: str

class WhatsAppEntry(BaseModel):
    id: str
    changes: List[WhatsAppChange]

class WhatsAppWebhook(BaseModel):
    object: str
    entry: List[WhatsAppEntry]