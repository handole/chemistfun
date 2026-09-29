from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.modules.auth.schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserProfileResponse,
    UserSummary,
)
from app.modules.users.controller import UserController
from app.modules.users.models import User
from app.modules.users.schemas import UserCreate
from app.utils.dependencies import get_current_user, get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new teacher or student account and receive a JWT token",
)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user account and immediately issue a JWT access token."""
    existing = UserController.get_by_email(db, email=payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered.",
        )

    user_in = UserCreate(
        email=payload.email,
        password=payload.password,
        full_name=payload.full_name,
        role=payload.role,
    )
    user = UserController.create(db, obj_in=user_in)

    token_claims = {
        "sub": str(user.uuid),
        "user_id": user.id,
        "email": user.email,
        "role": user.role.value,
    }
    access_token = create_access_token(data=token_claims)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserSummary.model_validate(user),
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate with email and password to receive a JWT token",
)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate credentials and generate a signed JWT access token."""
    user = UserController.authenticate(
        db, email=payload.email, password=payload.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_claims = {
        "sub": str(user.uuid),
        "user_id": user.id,
        "email": user.email,
        "role": user.role.value,
    }
    access_token = create_access_token(data=token_claims)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserSummary.model_validate(user),
    )


@router.get(
    "/me",
    response_model=UserProfileResponse,
    summary="Get current authenticated user profile",
)
def get_me(current_user: User = Depends(get_current_user)):
    """Return profile information of the currently authenticated user."""
    return current_user
