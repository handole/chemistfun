import secrets
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.classes.models import Class, ClassStudent
from app.modules.classes.schemas import ClassCreate, ClassUpdate
from app.modules.users.models import User


class ClassController:
    @staticmethod
    def _generate_enrollment_code() -> str:
        """Generate a random 6-character alphanumeric uppercase code."""
        return secrets.token_hex(3).upper()

    @staticmethod
    async def get_by_id(db: AsyncSession, class_id: int) -> Optional[Class]:
        result = await db.execute(select(Class).where(Class.id == class_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_uuid(db: AsyncSession, class_uuid: UUID) -> Optional[Class]:
        result = await db.execute(select(Class).where(Class.uuid == class_uuid))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_code(db: AsyncSession, enrollment_code: str) -> Optional[Class]:
        result = await db.execute(
            select(Class).where(Class.enrollment_code == enrollment_code.strip().upper())
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_multi(
        db: AsyncSession,
        teacher_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Class]:
        query = select(Class)
        if teacher_id is not None:
            query = query.where(Class.teacher_id == teacher_id)
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def create_class(db: AsyncSession, obj_in: ClassCreate) -> Class:
        code = obj_in.enrollment_code
        if not code:
            code = ClassController._generate_enrollment_code()
            # Ensure unique code
            check_res = await db.execute(select(Class).where(Class.enrollment_code == code))
            while check_res.scalar_one_or_none():
                code = ClassController._generate_enrollment_code()
                check_res = await db.execute(select(Class).where(Class.enrollment_code == code))
        else:
            code = code.strip().upper()

        db_obj = Class(
            teacher_id=obj_in.teacher_id,
            name=obj_in.name,
            enrollment_code=code,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def update_class(
        db: AsyncSession,
        db_obj: Class,
        obj_in: Union[ClassUpdate, Dict[str, Any]],
    ) -> Class:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        if "enrollment_code" in update_data and update_data["enrollment_code"]:
            update_data["enrollment_code"] = update_data["enrollment_code"].strip().upper()

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def delete_class(db: AsyncSession, class_id: int) -> Optional[Class]:
        class_obj = await ClassController.get_by_id(db, class_id=class_id)
        if class_obj:
            await db.delete(class_obj)
            await db.commit()
        return class_obj

    # --- Student Enrollment Operations ---

    @staticmethod
    async def enroll_student(db: AsyncSession, class_id: int, student_id: int) -> ClassStudent:
        result = await db.execute(
            select(ClassStudent).where(
                ClassStudent.class_id == class_id,
                ClassStudent.student_id == student_id,
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            return existing

        enrollment = ClassStudent(class_id=class_id, student_id=student_id)
        db.add(enrollment)
        await db.commit()
        await db.refresh(enrollment)
        return enrollment

    @staticmethod
    async def enroll_by_code(
        db: AsyncSession,
        enrollment_code: str,
        student_id: int,
    ) -> Optional[ClassStudent]:
        class_obj = await ClassController.get_by_code(db, enrollment_code)
        if not class_obj:
            return None
        return await ClassController.enroll_student(db, class_id=class_obj.id, student_id=student_id)

    @staticmethod
    async def unenroll_student(db: AsyncSession, class_id: int, student_id: int) -> bool:
        result = await db.execute(
            select(ClassStudent).where(
                ClassStudent.class_id == class_id,
                ClassStudent.student_id == student_id,
            )
        )
        enrollment = result.scalar_one_or_none()
        if enrollment:
            await db.delete(enrollment)
            await db.commit()
            return True
        return False

    @staticmethod
    async def get_enrolled_students(db: AsyncSession, class_id: int) -> List[User]:
        query = (
            select(User)
            .join(ClassStudent, ClassStudent.student_id == User.id)
            .where(ClassStudent.class_id == class_id)
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_student_classes(db: AsyncSession, student_id: int) -> List[Class]:
        query = (
            select(Class)
            .join(ClassStudent, ClassStudent.class_id == Class.id)
            .where(ClassStudent.student_id == student_id)
        )
        result = await db.execute(query)
        return list(result.scalars().all())


class_controller = ClassController()

__all__ = ["ClassController", "class_controller"]
