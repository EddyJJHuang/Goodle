from fastapi import APIRouter, Depends, HTTPException  # 确保有 HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.match import Match
from app.models.message import Message
from app.models.pet import Pet
from app.schemas.chat import MessageCreate, MessageResponse, ChatListResponse, ChatPreview

router = APIRouter(prefix="/api", tags=["chat"])

@router.get("/matches/chats", response_model=ChatListResponse)
def get_user_chats(
    user_id: int,
    db: Session = Depends(get_db)
):
    """获取当前用户的所有匹配对话表"""
    # 简化版：直接通过 user_id 查询
    from app.models.user import User
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_pet_ids = [pet.id for pet in user.pets]
    
    matches = db.query(Match).filter(
        (Match.pet1_id.in_(user_pet_ids)) | (Match.pet2_id.in_(user_pet_ids))
    ).all()
    
    chats = []
    for match in matches:
        other_pet_id = match.pet2_id if match.pet1_id in user_pet_ids else match.pet1_id
        other_pet = db.query(Pet).filter(Pet.id == other_pet_id).first()
        my_pet_id = match.pet1_id if match.pet1_id in user_pet_ids else match.pet2_id
        my_pet = db.query(Pet).filter(Pet.id == my_pet_id).first()
        
        last_message = db.query(Message).filter(
            Message.match_id == match.id
        ).order_by(Message.timestamp.desc()).first()
        
        chats.append(ChatPreview(
            match_id=match.id,
            pet1_name=my_pet.name,
            pet2_name=other_pet.name,
            pet1_photo=my_pet.photos[0] if my_pet.photos else None,
            pet2_photo=other_pet.photos[0] if other_pet.photos else None,
            last_message=last_message.content if last_message else None,
            last_message_time=last_message.timestamp if last_message else None,
            unread_count=0
        ))
    
    return ChatListResponse(chats=chats)

@router.get("/chat/{match_id}/messages", response_model=List[MessageResponse])
def get_chat_messages(
    match_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """获取特定对话的历史消息"""
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    messages = db.query(Message).filter(
        Message.match_id == match_id
    ).order_by(Message.timestamp.asc()).offset(skip).limit(limit).all()
    
    return messages

@router.post("/chat/{match_id}/message", response_model=MessageResponse)
def send_message(
    match_id: int,
    message: MessageCreate,
    sender_id: int,
    db: Session = Depends(get_db)
):
    """发送消息"""
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    new_message = Message(
        match_id=match_id,
        sender_id=sender_id,
        content=message.content
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    
    return new_message