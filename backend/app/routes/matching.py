from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from ..core import get_db, get_current_user
from ..models import User, Pet, Match
from ..schemas import (
    SwipeRequest, SwipeResponse, MatchResponse, PetResponse, ApiResponse
)
from ..services.matching import MatchingService
from typing import List

router = APIRouter(prefix="/api", tags=["matching"])


@router.get("/matches", response_model=ApiResponse[List[PetResponse]])
def get_matches(
    pet_id: int = Query(..., description="Your pet ID"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get recommended pets for matching."""
    # Get pet and verify ownership
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pet not found"
        )

    if pet.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to get matches for this pet"
        )

    # Get already swiped pets to exclude
    exclude_ids = MatchingService.get_already_swiped_pet_ids(db, pet_id)

    # Get recommended matches
    recommended = MatchingService.get_recommended_pets(
        db, pet, limit=limit, exclude_pet_ids=exclude_ids
    )

    # Convert to response
    pet_responses = []
    for matched_pet, score in recommended:
        pet_response = PetResponse(
            id=matched_pet.id,
            name=matched_pet.name,
            owner_id=matched_pet.owner_id,
            breed=matched_pet.breed,
            size=matched_pet.size,
            gender=matched_pet.gender,
            age=matched_pet.age,
            vaccinated=matched_pet.vaccinated,
            neutered=matched_pet.neutered,
            personality_tags=matched_pet.personality_tags,
            activity_level=matched_pet.activity_level,
            sociability=matched_pet.sociability,
            emotional_stability=matched_pet.emotional_stability,
            playfulness=matched_pet.playfulness,
            health_score=matched_pet.health_score,
            photos=matched_pet.photos,
            videos=matched_pet.videos,
            looking_for=matched_pet.looking_for,
            bio=matched_pet.bio,
            created_at=matched_pet.created_at,
            updated_at=matched_pet.updated_at
        )
        pet_responses.append(pet_response)

    return ApiResponse.success(data=pet_responses)


@router.post("/swipe", response_model=ApiResponse[SwipeResponse])
def swipe(
    swipe_data: SwipeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Process a swipe (like/pass) action."""
    # Verify pet ownership
    pet = db.query(Pet).filter(Pet.id == swipe_data.pet_id).first()
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pet not found"
        )

    if pet.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to swipe for this pet"
        )

    # Verify target pet exists
    target_pet = db.query(Pet).filter(Pet.id == swipe_data.target_pet_id).first()
    if not target_pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target pet not found"
        )

    # Validate action
    if swipe_data.action not in ["like", "pass"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid action. Must be 'like' or 'pass'"
        )

    # Process swipe
    is_match, match_id = MatchingService.process_swipe(
        db,
        current_user.id,
        swipe_data.pet_id,
        swipe_data.target_pet_id,
        swipe_data.action
    )

    response = SwipeResponse(
        match=is_match,
        match_id=match_id
    )

    return ApiResponse.success(
        data=response,
        message="It's a match!" if is_match else "Swipe recorded"
    )


@router.get("/matches/list", response_model=ApiResponse[List[MatchResponse]])
def get_match_list(
    pet_id: int = Query(..., description="Your pet ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of matches for a pet."""
    # Verify pet ownership
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pet not found"
        )

    if pet.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view matches for this pet"
        )

    # Get matches
    matches = db.query(Match).filter(
        (Match.pet1_id == pet_id) | (Match.pet2_id == pet_id)
    ).all()

    match_responses = []
    for match in matches:
        # Determine which pet is the other one
        other_pet_id = match.pet2_id if match.pet1_id == pet_id else match.pet1_id
        other_pet = db.query(Pet).filter(Pet.id == other_pet_id).first()

        if other_pet:
            # Calculate match score
            score = MatchingService.calculate_match_score(pet, other_pet)

            match_response = MatchResponse(
                id=match.id,
                pet1=PetResponse.model_validate(pet),
                pet2=PetResponse.model_validate(other_pet),
                score=score,
                created_at=match.created_at
            )
            match_responses.append(match_response)

    return ApiResponse.success(data=match_responses)
