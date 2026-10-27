from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.classes.models import Class
from app.modules.journals.models import AttendanceStatus, JournalAttendance, TeachingJournal
from app.modules.journals.schemas import (
    AttendanceItem,
    AttendanceResponse,
    JournalCreate,
    JournalDetailResponse,
    JournalListItem,
    JournalUpdate,
)
from app.modules.users.models import User


class JournalController:
    @staticmethod
    async def get_by_id(db: AsyncSession, journal_id: int) -> Optional[TeachingJournal]:
        query = (
            select(TeachingJournal)
            .where(TeachingJournal.id == journal_id)
            .options(
                selectinload(TeachingJournal.class_),
                selectinload(TeachingJournal.attendances).selectinload(JournalAttendance.student),
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_uuid(db: AsyncSession, journal_uuid: UUID) -> Optional[TeachingJournal]:
        query = (
            select(TeachingJournal)
            .where(TeachingJournal.uuid == journal_uuid)
            .options(
                selectinload(TeachingJournal.class_),
                selectinload(TeachingJournal.attendances).selectinload(JournalAttendance.student),
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_journals(
        db: AsyncSession,
        teacher_id: int,
        class_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[JournalListItem]:
        query = (
            select(TeachingJournal)
            .where(TeachingJournal.teacher_id == teacher_id)
            .options(
                selectinload(TeachingJournal.class_),
                selectinload(TeachingJournal.attendances),
            )
            .order_by(TeachingJournal.date.desc(), TeachingJournal.id.desc())
        )
        if class_id:
            query = query.where(TeachingJournal.class_id == class_id)

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        journals = list(result.scalars().all())

        items = []
        for j in journals:
            total_students = len(j.attendances)
            present_students = sum(1 for a in j.attendances if a.status == AttendanceStatus.PRESENT)
            scored = [a.score for a in j.attendances if a.score is not None]
            avg_score = round(sum(scored) / len(scored), 1) if scored else None
            items.append(
                JournalListItem(
                    id=j.id,
                    uuid=j.uuid,
                    teacher_id=j.teacher_id,
                    class_id=j.class_id,
                    class_name=j.class_.name if j.class_ else None,
                    title=j.title,
                    date=j.date,
                    start_time=j.start_time,
                    end_time=j.end_time,
                    planned_materials=j.planned_materials or [],
                    completed_materials=j.completed_materials or [],
                    total_students=total_students,
                    present_students=present_students,
                    avg_score=avg_score,
                    created_at=j.created_at,
                )
            )
        return items

    @staticmethod
    async def create_journal(
        db: AsyncSession,
        teacher_id: int,
        payload: JournalCreate,
    ) -> JournalDetailResponse:
        journal = TeachingJournal(
            teacher_id=teacher_id,
            class_id=payload.class_id,
            title=payload.title,
            date=payload.date,
            start_time=payload.start_time,
            end_time=payload.end_time,
            planned_materials=payload.planned_materials,
            completed_materials=payload.completed_materials,
            notes=payload.notes,
        )
        db.add(journal)
        await db.flush()

        # Add attendances
        for att in payload.attendances:
            ja = JournalAttendance(
                journal_id=journal.id,
                student_id=att.student_id,
                status=att.status,
                score=att.score,
                notes=att.notes,
            )
            db.add(ja)

        await db.commit()
        await db.refresh(journal)

        return await JournalController.to_detail_response(db, journal.id)

    @staticmethod
    async def update_journal(
        db: AsyncSession,
        journal: TeachingJournal,
        payload: JournalUpdate,
    ) -> JournalDetailResponse:
        if payload.class_id is not None:
            journal.class_id = payload.class_id
        if payload.title is not None:
            journal.title = payload.title
        if payload.date is not None:
            journal.date = payload.date
        if payload.start_time is not None:
            journal.start_time = payload.start_time
        if payload.end_time is not None:
            journal.end_time = payload.end_time
        if payload.planned_materials is not None:
            journal.planned_materials = payload.planned_materials
        if payload.completed_materials is not None:
            journal.completed_materials = payload.completed_materials
        if payload.notes is not None:
            journal.notes = payload.notes

        # Handle attendances update if provided
        if payload.attendances is not None:
            # Map existing attendances
            existing_attendances = {a.student_id: a for a in journal.attendances}
            incoming_student_ids = set()

            for att in payload.attendances:
                incoming_student_ids.add(att.student_id)
                if att.student_id in existing_attendances:
                    # Update existing record
                    curr = existing_attendances[att.student_id]
                    curr.status = att.status
                    curr.score = att.score
                    curr.notes = att.notes
                    db.add(curr)
                else:
                    # Insert new record
                    new_att = JournalAttendance(
                        journal_id=journal.id,
                        student_id=att.student_id,
                        status=att.status,
                        score=att.score,
                        notes=att.notes,
                    )
                    db.add(new_att)

            # Delete removed attendances
            for s_id, att in existing_attendances.items():
                if s_id not in incoming_student_ids:
                    await db.delete(att)

        db.add(journal)
        await db.commit()

        return await JournalController.to_detail_response(db, journal.id)

    @staticmethod
    async def delete_journal(db: AsyncSession, journal: TeachingJournal) -> None:
        await db.delete(journal)
        await db.commit()

    @staticmethod
    async def to_detail_response(db: AsyncSession, journal_id: int) -> JournalDetailResponse:
        j = await JournalController.get_by_id(db, journal_id)
        if not j:
            raise ValueError(f"Journal {journal_id} not found")

        att_responses = []
        for att in j.attendances:
            att_responses.append(
                AttendanceResponse(
                    id=att.id,
                    student_id=att.student_id,
                    status=att.status,
                    score=att.score,
                    notes=att.notes,
                    student_name=att.student.full_name if att.student else None,
                    student_email=att.student.email if att.student else None,
                )
            )

        return JournalDetailResponse(
            id=j.id,
            uuid=j.uuid,
            teacher_id=j.teacher_id,
            class_id=j.class_id,
            class_name=j.class_.name if j.class_ else None,
            title=j.title,
            date=j.date,
            start_time=j.start_time,
            end_time=j.end_time,
            planned_materials=j.planned_materials or [],
            completed_materials=j.completed_materials or [],
            notes=j.notes,
            created_at=j.created_at,
            updated_at=j.updated_at,
            attendances=att_responses,
        )


journal_controller = JournalController()

__all__ = ["JournalController", "journal_controller"]
