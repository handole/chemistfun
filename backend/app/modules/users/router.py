from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.controller import UserController
from app.modules.users.models import User, UserRole
from app.modules.users.schemas import UserCreate, UserResponse, UserUpdate
from app.utils.dependencies import (
    get_current_user,
    get_db,
    require_record,
    require_teacher,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/",
    response_model=List[UserResponse],
    summary="List all users (Teacher only)",
)
async def list_users(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    role: Optional[UserRole] = Query(default=None, description="Filter by role: teacher or student"),
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    return await UserController.get_multi(db, skip=skip, limit=limit, role=role)


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user (Teacher only, otherwise use /auth/register)",
)
async def create_user(
    payload: UserCreate,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    existing = await UserController.get_by_email(db, email=payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered.",
        )
    return await UserController.create(db, obj_in=payload)


@router.get(
    "/{user_uuid}",
    response_model=UserResponse,
    summary="Get user by UUID (Authenticated)",
)
async def get_user(
    user_uuid: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return require_record(
        await UserController.get_by_uuid(db, user_uuid=user_uuid),
        detail=f"User '{user_uuid}' not found.",
    )


@router.patch(
    "/{user_uuid}",
    response_model=UserResponse,
    summary="Update user by UUID (Self or Teacher)",
)
async def update_user(
    user_uuid: UUID,
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = require_record(
        await UserController.get_by_uuid(db, user_uuid=user_uuid),
        detail=f"User '{user_uuid}' not found.",
    )
    # Users can only update their own profile unless they are a teacher
    if current_user.role != UserRole.TEACHER and current_user.id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to edit this user's profile.",
        )

    # Check email uniqueness if being modified
    if payload.email and payload.email != user.email:
        if await UserController.get_by_email(db, email=payload.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use by another account.",
            )

    # Only teachers can elevate or change roles
    if payload.role and payload.role != user.role and current_user.role != UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers can modify account roles.",
        )

    return await UserController.update(db, db_obj=user, obj_in=payload)


@router.delete(
    "/{user_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user by UUID (Teacher only)",
)
async def delete_user(
    user_uuid: UUID,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    user = require_record(
        await UserController.get_by_uuid(db, user_uuid=user_uuid),
        detail=f"User '{user_uuid}' not found.",
    )
    # Prevent self-deletion
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account.",
        )
    await UserController.delete(db, user_id=user.id)
