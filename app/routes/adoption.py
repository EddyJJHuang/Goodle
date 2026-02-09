from fastapi import APIRouter, Depends, Query, HTTPException  # 添加 HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.adoption import AdoptionPost
from app.schemas.adoption import AdoptionCreate, AdoptionResponse

router = APIRouter(prefix="/api/adoption", tags=["adoption"])

@router.post("", response_model=AdoptionResponse, status_code=201)
def create_adoption_post(
    post: AdoptionCreate,
    db: Session = Depends(get_db)
):
    """发布待领养宠物信息"""
    new_post = AdoptionPost(**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.get("/list", response_model=List[AdoptionResponse])
def get_adoption_list(
    breed: Optional[str] = Query(None, description="品种筛选"),
    min_age: Optional[int] = Query(None, description="最小年龄"),
    max_age: Optional[int] = Query(None, description="最大年龄"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取所有待领养宠物列表（支持筛选）"""
    query = db.query(AdoptionPost)
    
    if breed:
        query = query.filter(AdoptionPost.breed.ilike(f"%{breed}%"))
    if min_age is not None:
        query = query.filter(AdoptionPost.age >= min_age)
    if max_age is not None:
        query = query.filter(AdoptionPost.age <= max_age)
    
    posts = query.order_by(AdoptionPost.posted_at.desc()).offset(skip).limit(limit).all()
    return posts

@router.get("/{post_id}", response_model=AdoptionResponse)
def get_adoption_detail(
    post_id: int,
    db: Session = Depends(get_db)
):
    """获取单个领养信息详情"""
    post = db.query(AdoptionPost).filter(AdoptionPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Adoption post not found")
    return post