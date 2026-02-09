from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..core import get_db, get_current_user, get_password_hash, verify_password, create_access_token
from ..models import User
from ..schemas import UserCreate, UserLogin, UserResponse, UserWithToken, ApiResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=ApiResponse[UserWithToken])
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        name=user_data.name,
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create token
    access_token = create_access_token(data={"sub": str(new_user.id)})

    user_response = UserResponse(
        id=str(new_user.id),
        email=new_user.email,
        name=new_user.name,
        avatar=new_user.avatar
    )

    return ApiResponse.success(
        data=UserWithToken(token=access_token, user=user_response),
        message="User registered successfully"
    )


@router.post("/login", response_model=ApiResponse[UserWithToken])
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    # Find user
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Verify password
    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Create token
    access_token = create_access_token(data={"sub": str(user.id)})

    user_response = UserResponse(
        id=str(user.id),
        email=user.email,
        name=user.name,
        avatar=user.avatar
    )

    return ApiResponse.success(
        data=UserWithToken(token=access_token, user=user_response),
        message="Login successful"
    )


@router.get("/me", response_model=ApiResponse[UserResponse])
def get_me(current_user: User = Depends(get_current_user)):
    user_response = UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        name=current_user.name,
        avatar=current_user.avatar
    )

    return ApiResponse.success(data=user_response)
