from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from ..core import get_db, get_current_user
from ..models import User, Pet
from ..schemas import (
    PetCreate, PetUpdate, PetResponse, PetListResponse, ApiResponse
)

router = APIRouter(prefix="/pets", tags=["pets"])


@router.get("", response_model=ApiResponse[PetListResponse])
def get_pets(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Pet)

    # Apply filters if provided
    if type:
        query = query.filter(Pet.breed.ilike(f"%{type}%"))
    if status:
        # Add status filter logic if needed
        pass

    # Get total count
    total = query.count()

    # Apply pagination
    skip = (page - 1) * limit
    pets = query.offset(skip).limit(limit).all()

    # Convert to response schema
    pet_responses = [
        PetResponse(
            id=pet.id,
            name=pet.name,
            owner_id=pet.owner_id,
            breed=pet.breed,
            size=pet.size,
            gender=pet.gender,
            age=pet.age,
            vaccinated=pet.vaccinated,
            neutered=pet.neutered,
            personality_tags=pet.personality_tags,
            activity_level=pet.activity_level,
            sociability=pet.sociability,
            emotional_stability=pet.emotional_stability,
            playfulness=pet.playfulness,
            health_score=pet.health_score,
            photos=pet.photos,
            videos=pet.videos,
            looking_for=pet.looking_for,
            bio=pet.bio,
            created_at=pet.created_at,
            updated_at=pet.updated_at
        )
        for pet in pets
    ]

    list_response = PetListResponse(
        items=pet_responses,
        total=total,
        page=page,
        pageSize=limit
    )

    return ApiResponse.success(data=list_response)


@router.get("/{pet_id}", response_model=ApiResponse[PetResponse])
def get_pet(
    pet_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pet not found"
        )

    pet_response = PetResponse(
        id=pet.id,
        name=pet.name,
        owner_id=pet.owner_id,
        breed=pet.breed,
        size=pet.size,
        gender=pet.gender,
        age=pet.age,
        vaccinated=pet.vaccinated,
        neutered=pet.neutered,
        personality_tags=pet.personality_tags,
        activity_level=pet.activity_level,
        sociability=pet.sociability,
        emotional_stability=pet.emotional_stability,
        playfulness=pet.playfulness,
        health_score=pet.health_score,
        photos=pet.photos,
        videos=pet.videos,
        looking_for=pet.looking_for,
        bio=pet.bio,
        created_at=pet.created_at,
        updated_at=pet.updated_at
    )

    return ApiResponse.success(data=pet_response)


@router.post("", response_model=ApiResponse[PetResponse], status_code=status.HTTP_201_CREATED)
def create_pet(
    pet_data: PetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_pet = Pet(
        owner_id=current_user.id,
        name=pet_data.name,
        breed=pet_data.breed,
        size=pet_data.size,
        gender=pet_data.gender,
        age=pet_data.age,
        vaccinated=pet_data.vaccinated,
        neutered=pet_data.neutered,
        personality_tags=pet_data.personality_tags,
        activity_level=pet_data.activity_level,
        sociability=pet_data.sociability,
        emotional_stability=pet_data.emotional_stability,
        playfulness=pet_data.playfulness,
        health_score=pet_data.health_score,
        photos=pet_data.photos,
        videos=pet_data.videos,
        looking_for=pet_data.looking_for,
        bio=pet_data.bio
    )

    db.add(new_pet)
    db.commit()
    db.refresh(new_pet)

    pet_response = PetResponse(
        id=new_pet.id,
        name=new_pet.name,
        owner_id=new_pet.owner_id,
        breed=new_pet.breed,
        size=new_pet.size,
        gender=new_pet.gender,
        age=new_pet.age,
        vaccinated=new_pet.vaccinated,
        neutered=new_pet.neutered,
        personality_tags=new_pet.personality_tags,
        activity_level=new_pet.activity_level,
        sociability=new_pet.sociability,
        emotional_stability=new_pet.emotional_stability,
        playfulness=new_pet.playfulness,
        health_score=new_pet.health_score,
        photos=new_pet.photos,
        videos=new_pet.videos,
        looking_for=new_pet.looking_for,
        bio=new_pet.bio,
        created_at=new_pet.created_at,
        updated_at=new_pet.updated_at
    )

    return ApiResponse.success(data=pet_response, message="Pet created successfully")


@router.put("/{pet_id}", response_model=ApiResponse[PetResponse])
def update_pet(
    pet_id: int,
    pet_data: PetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pet not found"
        )

    # Check if user owns the pet
    if pet.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this pet"
        )

    # Update fields
    update_data = pet_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(pet, field, value)

    db.commit()
    db.refresh(pet)

    pet_response = PetResponse(
        id=pet.id,
        name=pet.name,
        owner_id=pet.owner_id,
        breed=pet.breed,
        size=pet.size,
        gender=pet.gender,
        age=pet.age,
        vaccinated=pet.vaccinated,
        neutered=pet.neutered,
        personality_tags=pet.personality_tags,
        activity_level=pet.activity_level,
        sociability=pet.sociability,
        emotional_stability=pet.emotional_stability,
        playfulness=pet.playfulness,
        health_score=pet.health_score,
        photos=pet.photos,
        videos=pet.videos,
        looking_for=pet.looking_for,
        bio=pet.bio,
        created_at=pet.created_at,
        updated_at=pet.updated_at
    )

    return ApiResponse.success(data=pet_response, message="Pet updated successfully")


@router.delete("/{pet_id}", response_model=ApiResponse[dict])
def delete_pet(
    pet_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pet not found"
        )

    # Check if user owns the pet
    if pet.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this pet"
        )

    db.delete(pet)
    db.commit()

    return ApiResponse.success(data={"message": "Pet deleted successfully"})
