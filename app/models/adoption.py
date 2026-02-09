from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from datetime import datetime
from app.database import Base

class AdoptionPost(Base):
    __tablename__ = "adoption_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    pet_photo = Column(JSON)
    breed = Column(String, index=True)
    age = Column(Integer, index=True)
    personality = Column(Text)
    health_status = Column(Text)
    requirements = Column(Text)
    contact = Column(String)
    posted_at = Column(DateTime, default=datetime.utcnow, index=True)