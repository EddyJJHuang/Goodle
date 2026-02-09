from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class PetBase(BaseModel):
    name: str
    breed: str
    size: str
    gender: str
    age: int
    vaccinated: bool = False
    neutered: bool = False
    personality_tags: Optional[List[str]] = None
    activity_level: float = 50
    sociability: float = 50
    emotional_stability: float = 50
    playfulness: float = 50
    health_score: float = 50
    photos: Optional[List[str]] = None
    videos: Optional[List[str]] = None
    looking_for: Optional[str] = None
    bio: Optional[str] = None


class PetCreate(PetBase):
    pass


class PetUpdate(BaseModel):
    name: Optional[str] = None
    breed: Optional[str] = None
    size: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    vaccinated: Optional[bool] = None
    neutered: Optional[bool] = None
    personality_tags: Optional[List[str]] = None
    activity_level: Optional[float] = None
    sociability: Optional[float] = None
    emotional_stability: Optional[float] = None
    playfulness: Optional[float] = None
    health_score: Optional[float] = None
    photos: Optional[List[str]] = None
    videos: Optional[List[str]] = None
    looking_for: Optional[str] = None
    bio: Optional[str] = None


class PetResponse(PetBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PetListResponse(BaseModel):
    items: List[PetResponse]
    total: int
    page: int
    pageSize: int


class SwipeRequest(BaseModel):
    pet_id: int
    target_pet_id: int
    action: str  # "like" or "pass"


class SwipeResponse(BaseModel):
    match: bool
    match_id: Optional[int] = None


class MatchResponse(BaseModel):
    id: int
    pet1: PetResponse
    pet2: PetResponse
    score: float
    created_at: datetime

    class Config:
        from_attributes = True
