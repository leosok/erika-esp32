from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class TextdataSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    hashid: str
    line_number: int
    text: str
    timestamp: datetime

class TypewriterSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: str
    user_firstname: str | None = None
    user_lastname: str | None = None
    user_email: str
    chat_active: bool
    erika_name: str
    email: str
    status: int

class MessageSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    typewriter: TypewriterSchema
    sender: str
    subject: str
    body: str
    timestamp: datetime
    is_printed: bool

class TypewriterCreateSchema(BaseModel):
    uuid: str
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    email: str
    chat_active: bool = True
    erika_name: str

class PageLineSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    line_number: int
    text: str
    timestamp: datetime

class PageSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    hashid: str
    lines: List[PageLineSchema]
    created_at: datetime
    is_printed: bool = False

class EmailWebhookSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    headers: Dict[str, Any] = Field(..., description="Email headers containing 'to', 'from', 'subject'")
    plain: str = Field(..., description="The plain text body of the email")

class WebhookResponseSchema(BaseModel):
    detail: str
