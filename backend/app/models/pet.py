from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base


class Pet(Base):
    __tablename__ = "pets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Static info
    breed = Column(String, nullable=False)
    size = Column(String, nullable=False)  # small, medium, large
    gender = Column(String, nullable=False)  # male, female
    age = Column(Integer, nullable=False)  # in months
    vaccinated = Column(Boolean, default=False)
    neutered = Column(Boolean, default=False)
    personality_tags = Column(JSON, nullable=True)  # ["friendly", "energetic", etc.]

    # Dynamic info (scores 0-100)
    activity_level = Column(Float, default=50)  # 活动量评分
    sociability = Column(Float, default=50)  # 外向程度
    emotional_stability = Column(Float, default=50)  # 情绪稳定度
    playfulness = Column(Float, default=50)  # 玩耍偏好
    health_score = Column(Float, default=50)  # 身体活合评分

    # Media
    photos = Column(JSON, nullable=True)  # ["url1", "url2", ...]
    videos = Column(JSON, nullable=True)  # ["url1", "url2", ...]

    # Matching preferences
    looking_for = Column(String, nullable=True)  # playmate, walking_buddy, etc.

    # Metadata
    bio = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="pets")


class Swipe(Base):
    __tablename__ = "swipes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False)
    target_pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False)
    action = Column(String, nullable=False)  # "like" or "pass"
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="swipes")


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    pet1_id = Column(Integer, ForeignKey("pets.id"), nullable=False)
    pet2_id = Column(Integer, ForeignKey("pets.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
