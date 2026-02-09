from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class AdoptionCreate(BaseModel):
    pet_photo: List[str]
    breed: str
    age: int
    personality: str
    health_status: str
    requirements: str
    contact: str

class AdoptionResponse(BaseModel):
    id: int
    pet_photo: List[str]
    breed: str
    age: int
    personality: str
    health_status: str
    requirements: str
    contact: str
    posted_at: datetime
    
    class Config:
        from_attributes = True