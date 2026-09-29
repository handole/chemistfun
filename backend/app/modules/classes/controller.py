import secrets
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.classes.models import Class, ClassStudent
from app.modules.classes.schemas import ClassCreate, ClassUpdate
from app.modules.users.models import User


class ClassController:
    @staticmethod
    def _generate_enrollment_code() -> str:
        """Generate a random 6-character alphanumeric uppercase code."""
        return secrets.token_hex(3).upper()

    @staticmethod
    def get_by_id(db: Session, class_id: int) -> Optional[Class]:
        return db.scalar(select(Class).where(Class.id == class_id))

    @staticmethod
    def get_by_uuid(db: Session, class_uuid: UUID) -> Optional[Class]:
        return db.scalar(select(Class).where(Class.uuid == class_uuid))

    @staticmethod
    def get_by_code(db: Session, enrollment_code: str) -> Optional[Class]:
        return db.scalar(select(Class).where(Class.enrollment_code == enrollment_code.strip().upper()))

    @staticmethod
    def get_multi(
        db: Session,
        teacher_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Class]:
        query = select(Class)
        if teacher_id is not None:
            query = query.where(Class.teacher_id == teacher_id)
        query = query.offset(skip).limit(limit)
        return list(db.scalars(query).all())

    @staticmethod
    def create_class(db: Session, obj_in: ClassCreate) -> Class:
        code = obj_in.enrollment_code
        if not code:
            code = ClassController._generate_enrollment_code()
            # Ensure unique code
            while db.scalar(select(Class).where(Class.enrollment_code == code)):
                code = ClassController._generate_enrollment_code()
        else:
            code = code.strip().upper()

        db_obj = Class(
            teacher_id=obj_in.teacher_id,
            name=obj_in.name,
            enrollment_code=code,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def update_class(
        db: Session,
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
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete_class(db: Session, class_id: int) -> Optional[Class]:
        class_obj = ClassController.get_by_id(db, class_id=class_id)
        if class_obj:
            db.delete(class_obj)
            db.commit()
        return class_obj

    # --- Student Enrollment Operations ---

    @staticmethod
    def enroll_student(db: Session, class_id: int, student_id: int) -> ClassStudent:
        existing = db.scalar(
            select(ClassStudent).where(
                ClassStudent.class_id == class_id,
                ClassStudent.student_id == student_id,
            )
        )
        if existing:
            return existing

        enrollment = ClassStudent(class_id=class_id, student_id=student_id)
        db.add(enrollment)
        db.commit()
        db.refresh(enrollment)
        return enrollment

    @staticmethod
    def enroll_by_code(
        db: Session,
        enrollment_code: str,
        student_id: int,
    ) -> Optional[ClassStudent]:
        class_obj = ClassController.get_by_code(db, enrollment_code)
        if not class_obj:
            return None
        return ClassController.enroll_student(db, class_id=class_obj.id, student_id=student_id)

    @staticmethod
    def unenroll_student(db: Session, class_id: int, student_id: int) -> bool:
        enrollment = db.scalar(
            select(ClassStudent).where(
                ClassStudent.class_id == class_id,
                ClassStudent.student_id == student_id,
            )
        )
        if enrollment:
            db.delete(enrollment)
            db.commit()
            return True
        return False

    @staticmethod
    def get_enrolled_students(db: Session, class_id: int) -> List[User]:
        query = (
            select(User)
            .join(ClassStudent, ClassStudent.student_id == User.id)
            .where(ClassStudent.class_id == class_id)
        )
        return list(db.scalars(query).all())

    @staticmethod
    def get_student_classes(db: Session, student_id: int) -> List[Class]:
        query = (
            select(Class)
            .join(ClassStudent, ClassStudent.class_id == Class.id)
            .where(ClassStudent.student_id == student_id)
        )
        return list(db.scalars(query).all())


class_controller = ClassController()

__all__ = ["ClassController", "class_controller"]

