from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.journals.controller import JournalController
from app.modules.journals.schemas import (
    JournalCreate,
    JournalDetailResponse,
    JournalListItem,
    JournalUpdate,
)
from app.modules.users.models import User
from app.utils.dependencies import get_db, require_record, require_teacher

router = APIRouter(prefix="/journals", tags=["Journals"])


@router.get(
    "/",
    response_model=List[JournalListItem],
    summary="List teaching journals for current teacher",
)
async def list_journals(
    class_id: Optional[int] = Query(default=None, description="Filter by class ID"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    return await JournalController.list_journals(
        db, teacher_id=current_user.id, class_id=class_id, skip=skip, limit=limit
    )


@router.post(
    "/",
    response_model=JournalDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new teaching journal session",
)
async def create_journal(
    payload: JournalCreate,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    return await JournalController.create_journal(
        db, teacher_id=current_user.id, payload=payload
    )


@router.get(
    "/{journal_uuid}",
    response_model=JournalDetailResponse,
    summary="Get journal detail by UUID",
)
async def get_journal(
    journal_uuid: UUID,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    journal = require_record(
        await JournalController.get_by_uuid(db, journal_uuid=journal_uuid),
        detail=f"Journal '{journal_uuid}' not found.",
    )
    if journal.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view journals you created.",
        )
    return await JournalController.to_detail_response(db, journal.id)


@router.patch(
    "/{journal_uuid}",
    response_model=JournalDetailResponse,
    summary="Update teaching journal session",
)
async def update_journal(
    journal_uuid: UUID,
    payload: JournalUpdate,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    journal = require_record(
        await JournalController.get_by_uuid(db, journal_uuid=journal_uuid),
        detail=f"Journal '{journal_uuid}' not found.",
    )
    if journal.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit journals you created.",
        )
    return await JournalController.update_journal(db, journal=journal, payload=payload)


@router.delete(
    "/{journal_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete teaching journal session",
)
async def delete_journal(
    journal_uuid: UUID,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    journal = require_record(
        await JournalController.get_by_uuid(db, journal_uuid=journal_uuid),
        detail=f"Journal '{journal_uuid}' not found.",
    )
    if journal.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete journals you created.",
        )
    await JournalController.delete_journal(db, journal=journal)
