from sqlalchemy import Column, Integer, String, Boolean, Float, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class Pet(Base):
    __tablename__ = "pets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    breed = Column(String)
    size = Column(String)
    gender = Column(String)
    age = Column(Integer)
    vaccine = Column(Boolean, default=False)
    personality = Column(Text)
    neutered = Column(Boolean, default=False)
    looking_for_match = Column(Boolean, default=True)
    photos = Column(JSON)
    video_url = Column(String)
    ai_tags = Column(JSON)
    
    owner = relationship("User", back_populates="pets")
    dynamic_info = relationship("PetDynamicInfo", back_populates="pet", uselist=False)


class PetDynamicInfo(Base):
    __tablename__ = "pet_dynamic_info"
    
    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(Integer, ForeignKey("pets.id"), unique=True, nullable=False)
    activity_level = Column(Float)
    approach_speed = Column(Float)
    emotional_stability = Column(Float)
    play_preference = Column(String)
    body_language_score = Column(Float)
    
    pet = relationship("Pet", back_populates="dynamic_info")