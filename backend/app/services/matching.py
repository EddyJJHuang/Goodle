from sqlalchemy.orm import Session
from ..models import Pet, Swipe, Match
from typing import List, Tuple
import math


class MatchingService:
    # Weights for matching algorithm
    STATIC_INFO_WEIGHT = 0.5  # 50%
    PERSONALITY_WEIGHT = 0.4  # 40%
    ACTIVITY_WEIGHT = 0.3  # 30%

    @staticmethod
    def calculate_static_score(pet1: Pet, pet2: Pet) -> float:
        """Calculate compatibility score based on static information."""
        score = 100.0

        # Size compatibility (same size preferred)
        if pet1.size == pet2.size:
            score += 20
        else:
            size_order = {"small": 0, "medium": 1, "large": 2}
            diff = abs(size_order.get(pet1.size, 1) - size_order.get(pet2.size, 1))
            score -= diff * 10

        # Age compatibility (similar age preferred)
        age_diff = abs(pet1.age - pet2.age)
        if age_diff <= 6:  # Within 6 months
            score += 20
        elif age_diff <= 12:  # Within 1 year
            score += 10
        else:
            score -= min(age_diff, 30)

        # Vaccination status (both vaccinated preferred)
        if pet1.vaccinated and pet2.vaccinated:
            score += 15

        # Neutered status (both neutered preferred for safety)
        if pet1.neutered and pet2.neutered:
            score += 15

        return max(0, min(100, score))

    @staticmethod
    def calculate_personality_score(pet1: Pet, pet2: Pet) -> float:
        """Calculate compatibility score based on personality traits."""
        # Calculate difference in personality scores
        sociability_diff = abs(pet1.sociability - pet2.sociability)
        playfulness_diff = abs(pet1.playfulness - pet2.playfulness)
        emotional_diff = abs(pet1.emotional_stability - pet2.emotional_stability)

        # Similar personalities are better matches
        avg_diff = (sociability_diff + playfulness_diff + emotional_diff) / 3

        # Convert difference to score (0 diff = 100, 100 diff = 0)
        personality_score = 100 - avg_diff

        return max(0, min(100, personality_score))

    @staticmethod
    def calculate_activity_score(pet1: Pet, pet2: Pet) -> float:
        """Calculate compatibility score based on activity levels."""
        activity_diff = abs(pet1.activity_level - pet2.activity_level)

        # Similar activity levels are better
        activity_score = 100 - activity_diff

        return max(0, min(100, activity_score))

    @classmethod
    def calculate_match_score(cls, pet1: Pet, pet2: Pet) -> float:
        """Calculate overall match score between two pets."""
        static_score = cls.calculate_static_score(pet1, pet2)
        personality_score = cls.calculate_personality_score(pet1, pet2)
        activity_score = cls.calculate_activity_score(pet1, pet2)

        # Weighted average
        total_score = (
            static_score * cls.STATIC_INFO_WEIGHT +
            personality_score * cls.PERSONALITY_WEIGHT +
            activity_score * cls.ACTIVITY_WEIGHT
        )

        # Normalize to 0-100 range
        normalized_score = total_score / (cls.STATIC_INFO_WEIGHT + cls.PERSONALITY_WEIGHT + cls.ACTIVITY_WEIGHT)

        return round(normalized_score, 2)

    @staticmethod
    def get_recommended_pets(
        db: Session,
        pet: Pet,
        limit: int = 10,
        exclude_pet_ids: List[int] = None
    ) -> List[Tuple[Pet, float]]:
        """Get recommended pets for matching."""
        if exclude_pet_ids is None:
            exclude_pet_ids = []

        # Get all potential matches (exclude own pet and already swiped)
        query = db.query(Pet).filter(
            Pet.id != pet.id,
            Pet.owner_id != pet.owner_id,
            Pet.id.notin_(exclude_pet_ids)
        )

        potential_matches = query.all()

        # Calculate scores
        scored_pets = []
        for candidate in potential_matches:
            score = MatchingService.calculate_match_score(pet, candidate)
            scored_pets.append((candidate, score))

        # Sort by score (highest first)
        scored_pets.sort(key=lambda x: x[1], reverse=True)

        # Return top matches
        return scored_pets[:limit]

    @staticmethod
    def process_swipe(
        db: Session,
        user_id: int,
        pet_id: int,
        target_pet_id: int,
        action: str
    ) -> Tuple[bool, int]:
        """Process a swipe action and check for mutual match."""
        # Record swipe
        swipe = Swipe(
            user_id=user_id,
            pet_id=pet_id,
            target_pet_id=target_pet_id,
            action=action
        )
        db.add(swipe)
        db.commit()

        # If pass, no match possible
        if action != "like":
            return False, None

        # Check if other user also liked
        target_pet = db.query(Pet).filter(Pet.id == target_pet_id).first()
        if not target_pet:
            return False, None

        mutual_like = db.query(Swipe).filter(
            Swipe.user_id == target_pet.owner_id,
            Swipe.target_pet_id == pet_id,
            Swipe.action == "like"
        ).first()

        if mutual_like:
            # Create match
            existing_match = db.query(Match).filter(
                ((Match.pet1_id == pet_id) & (Match.pet2_id == target_pet_id)) |
                ((Match.pet1_id == target_pet_id) & (Match.pet2_id == pet_id))
            ).first()

            if not existing_match:
                match = Match(
                    pet1_id=pet_id,
                    pet2_id=target_pet_id
                )
                db.add(match)
                db.commit()
                db.refresh(match)
                return True, match.id

        return False, None

    @staticmethod
    def get_already_swiped_pet_ids(db: Session, pet_id: int) -> List[int]:
        """Get list of pet IDs that have already been swiped on."""
        swipes = db.query(Swipe).filter(Swipe.pet_id == pet_id).all()
        return [swipe.target_pet_id for swipe in swipes]
