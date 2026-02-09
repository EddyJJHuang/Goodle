import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal, engine, Base
from app.models import User, Pet
from app.core.security import get_password_hash
import random


def create_demo_users(db):
    """Create demo users."""
    users = [
        {"email": "alice@example.com", "name": "Alice Johnson", "password": "password123"},
        {"email": "bob@example.com", "name": "Bob Smith", "password": "password123"},
        {"email": "carol@example.com", "name": "Carol Williams", "password": "password123"},
        {"email": "david@example.com", "name": "David Brown", "password": "password123"},
        {"email": "emma@example.com", "name": "Emma Davis", "password": "password123"},
    ]

    created_users = []
    for user_data in users:
        user = User(
            email=user_data["email"],
            name=user_data["name"],
            hashed_password=get_password_hash(user_data["password"])
        )
        db.add(user)
        created_users.append(user)

    db.commit()
    for user in created_users:
        db.refresh(user)

    return created_users


def create_demo_pets(db, users):
    """Create 20 demo pets with diverse characteristics."""
    breeds = [
        "Golden Retriever", "Labrador", "German Shepherd", "Beagle", "Bulldog",
        "Poodle", "Husky", "Corgi", "Shiba Inu", "Border Collie",
        "Dachshund", "Chihuahua", "Pomeranian", "Boxer", "Rottweiler"
    ]

    sizes = ["small", "medium", "large"]
    genders = ["male", "female"]

    personality_options = [
        ["friendly", "energetic", "playful"],
        ["calm", "gentle", "affectionate"],
        ["intelligent", "curious", "active"],
        ["loyal", "protective", "brave"],
        ["social", "outgoing", "cheerful"],
        ["independent", "confident", "alert"],
        ["shy", "quiet", "sweet"],
        ["adventurous", "bold", "fearless"]
    ]

    looking_for_options = [
        "playmate", "walking_buddy", "training_partner", "social_companion"
    ]

    pet_names = [
        "Max", "Bella", "Charlie", "Luna", "Cooper", "Daisy", "Rocky", "Sadie",
        "Buddy", "Molly", "Duke", "Lucy", "Bear", "Maggie", "Jack", "Sophie",
        "Oliver", "Chloe", "Milo", "Zoe"
    ]

    pets = []
    for i in range(20):
        owner = random.choice(users)
        breed = random.choice(breeds)

        # Size based on breed
        if breed in ["Chihuahua", "Pomeranian", "Dachshund"]:
            size = "small"
        elif breed in ["Golden Retriever", "German Shepherd", "Husky", "Rottweiler"]:
            size = "large"
        else:
            size = random.choice(sizes)

        pet = Pet(
            name=pet_names[i],
            owner_id=owner.id,
            breed=breed,
            size=size,
            gender=random.choice(genders),
            age=random.randint(6, 96),  # 6 months to 8 years
            vaccinated=random.choice([True, True, False]),  # 2/3 chance vaccinated
            neutered=random.choice([True, False]),
            personality_tags=random.choice(personality_options),
            activity_level=round(random.uniform(30, 90), 1),
            sociability=round(random.uniform(30, 90), 1),
            emotional_stability=round(random.uniform(40, 95), 1),
            playfulness=round(random.uniform(30, 95), 1),
            health_score=round(random.uniform(60, 100), 1),
            photos=[
                f"https://via.placeholder.com/400x400?text={pet_names[i]}",
                f"https://via.placeholder.com/400x400?text={pet_names[i]}_2"
            ],
            videos=[
                f"https://via.placeholder.com/video_{pet_names[i]}.mp4"
            ],
            looking_for=random.choice(looking_for_options),
            bio=f"Hi! I'm {pet_names[i]}, a {breed}. I love to play and make new friends!"
        )
        db.add(pet)
        pets.append(pet)

    db.commit()
    for pet in pets:
        db.refresh(pet)

    return pets


def seed_database():
    """Main function to seed the database."""
    print("[*] Starting database seeding...")

    # Create tables
    Base.metadata.create_all(bind=engine)
    print("[+] Database tables created")

    # Create session
    db = SessionLocal()

    try:
        # Check if data already exists
        existing_users = db.query(User).count()
        if existing_users > 0:
            print("[!] Database already has data. Skipping seed.")
            return

        # Create demo data
        print("[*] Creating demo users...")
        users = create_demo_users(db)
        print(f"[+] Created {len(users)} users")

        print("[*] Creating demo pets...")
        pets = create_demo_pets(db, users)
        print(f"[+] Created {len(pets)} pets")

        print("[+] Database seeding completed successfully!")
        print("\n[*] Demo credentials:")
        print("   Email: alice@example.com")
        print("   Password: password123")
        print("\n   (You can also use bob, carol, david, or emma @example.com)")

    except Exception as e:
        print(f"[-] Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
