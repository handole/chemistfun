import enum
import uuid as py_uuid
from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import DateTime, Enum, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.modules.classes.models import Class, ClassStudent
    from app.modules.assessment.models import StudentQuizAttempt


class UserRole(str, enum.Enum):
    TEACHER = "teacher"
    STUDENT = "student"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True)
    uuid: Mapped[py_uuid.UUID] = mapped_column(UUID(as_uuid=True),default=py_uuid.uuid4,unique=True,nullable=False,index=True)
    email: Mapped[str] = mapped_column(String(255),unique=True,nullable=False,index=True)
    password_hash: Mapped[str] = mapped_column(String(255),nullable=False)
    full_name: Mapped[str] = mapped_column(String(255),nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role", native_enum=True, values_callable=lambda x: [e.value for e in x],),nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now(),nullable=False)

    # Relationships
    taught_classes: Mapped[List["Class"]] = relationship("Class",back_populates="teacher",cascade="all, delete-orphan")
    class_enrollments: Mapped[List["ClassStudent"]] = relationship("ClassStudent",back_populates="student",cascade="all, delete-orphan")
    quiz_attempts: Mapped[List["StudentQuizAttempt"]] = relationship("StudentQuizAttempt",back_populates="student",cascade="all, delete-orphan")


__all__ = ["UserRole", "User"]