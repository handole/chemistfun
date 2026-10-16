import secrets

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import TEACHER_INVITE_CODE
from app.core.rate_limiter import (
    get_client_ip,
    login_rate_limiter,
    register_rate_limiter,
)
from app.core.security import create_access_token
from app.modules.auth.schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserProfileResponse,
    UserSummary,
)
from app.modules.users.controller import UserController
from app.modules.users.models import User, UserRole
from app.modules.users.schemas import UserCreate
from app.utils.dependencies import get_current_user, get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new teacher or student account and receive a JWT token",
)
async def register(
    payload: RegisterRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user account and immediately issue a JWT access token."""
    client_ip = get_client_ip(request)
    allowed, retry_after = register_rate_limiter.is_allowed(f"reg_{client_ip}")
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Terlalu banyak permintaan pendaftaran. Silakan tunggu {retry_after} detik.",
            headers={"Retry-After": str(retry_after)},
        )

    if payload.role == UserRole.TEACHER:
        is_code_valid = bool(
            TEACHER_INVITE_CODE
            and payload.teacher_invite_code
            and secrets.compare_digest(payload.teacher_invite_code.strip(), TEACHER_INVITE_CODE)
        )
        if not is_code_valid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Pendaftaran role Guru memerlukan kode undangan resmi yang valid.",
            )

    existing = await UserController.get_by_email(db, email=payload.email)
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
    user = await UserController.create(db, obj_in=user_in)

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
async def login(
    payload: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate credentials and generate a signed JWT access token."""
    client_ip = get_client_ip(request)
    email_key = payload.email.strip().lower()

    # Rate limit by IP (password spraying prevention) and by account (brute-force prevention)
    ip_allowed, ip_retry = login_rate_limiter.is_allowed(f"ip_{client_ip}")
    acc_allowed, acc_retry = login_rate_limiter.is_allowed(f"acc_{email_key}")
    if not ip_allowed or not acc_allowed:
        retry_after = max(ip_retry, acc_retry)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Terlalu banyak percobaan login. Silakan tunggu {retry_after} detik.",
            headers={"Retry-After": str(retry_after)},
        )

    user = await UserController.authenticate(
        db, email=payload.email, password=payload.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Reset account limiter on successful login
    login_rate_limiter.reset(f"acc_{email_key}")

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
async def get_me(current_user: User = Depends(get_current_user)):
    """Return profile information of the currently authenticated user."""
    return current_user
