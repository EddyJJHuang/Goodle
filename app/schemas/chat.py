from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class MessageCreate(BaseModel):
    content: str

class MessageResponse(BaseModel):
    id: int
    match_id: int
    sender_id: int
    content: str
    timestamp: datetime
    
    class Config:
        from_attributes = True

class ChatPreview(BaseModel):
    match_id: int
    pet1_name: str
    pet2_name: str
    pet1_photo: Optional[str] = None
    pet2_photo: Optional[str] = None
    last_message: Optional[str] = None
    last_message_time: Optional[datetime] = None
    unread_count: int = 0

class ChatListResponse(BaseModel):
    chats: List[ChatPreview]