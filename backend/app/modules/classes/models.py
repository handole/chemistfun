import uuid as py_uuid
from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.modules.users.models import User
    from app.modules.content.models import Module


class Class(Base):
    __tablename__ = "classes"

    id: Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True)
    uuid: Mapped[py_uuid.UUID] = mapped_column(UUID(as_uuid=True),default=py_uuid.uuid4,unique=True,nullable=False,index=True)
    teacher_id: Mapped[int] = mapped_column(Integer,ForeignKey("users.id", ondelete="CASCADE"),nullable=False,index=True)
    name: Mapped[str] = mapped_column(String(255),nullable=False)
    enrollment_code: Mapped[str] = mapped_column(String(50),unique=True,nullable=False,index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False)

    # Relationships
    teacher: Mapped["User"] = relationship("User",back_populates="taught_classes")
    student_enrollments: Mapped[List["ClassStudent"]] = relationship("ClassStudent",back_populates="class_",cascade="all, delete-orphan")
    modules: Mapped[List["Module"]] = relationship("Module",back_populates="class_",cascade="all, delete-orphan")


class ClassStudent(Base):
    """Junction table connecting students to classes (Many-to-Many)."""
    __tablename__ = "class_students"

    class_id: Mapped[int] = mapped_column(Integer,ForeignKey("classes.id", ondelete="CASCADE"),primary_key=True)
    student_id: Mapped[int] = mapped_column(Integer,ForeignKey("users.id", ondelete="CASCADE"),primary_key=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False)

    # Relationships
    class_: Mapped["Class"] = relationship("Class",back_populates="student_enrollments")
    student: Mapped["User"] = relationship("User",back_populates="class_enrollments")


__all__ = ["Class", "ClassStudent"]
