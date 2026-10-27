import enum
import uuid as py_uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Date, DateTime, Enum, Float, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.modules.classes.models import Class
    from app.modules.users.models import User


class AttendanceStatus(str, enum.Enum):
    PRESENT = "present"
    SICK = "sick"
    PERMITTED = "permitted"
    ABSENT = "absent"


class TeachingJournal(Base):
    __tablename__ = "teaching_journals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uuid: Mapped[py_uuid.UUID] = mapped_column(
        UUID(as_uuid=True), default=py_uuid.uuid4, unique=True, nullable=False, index=True
    )
    teacher_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    class_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    start_time: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # e.g. "07:30"
    end_time: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)    # e.g. "09:00"

    # List of material IDs planned and completed (JSON array of ints)
    planned_materials: Mapped[List[int]] = mapped_column(JSONB, default=list, nullable=False)
    completed_materials: Mapped[List[int]] = mapped_column(JSONB, default=list, nullable=False)

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    teacher: Mapped["User"] = relationship("User")
    class_: Mapped["Class"] = relationship("Class")
    attendances: Mapped[List["JournalAttendance"]] = relationship(
        "JournalAttendance", back_populates="journal", cascade="all, delete-orphan"
    )


class JournalAttendance(Base):
    __tablename__ = "journal_attendances"
    __table_args__ = (
        UniqueConstraint("journal_id", "student_id", name="uq_journal_student_attendance"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    journal_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("teaching_journals.id", ondelete="CASCADE"), nullable=False, index=True
    )
    student_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[AttendanceStatus] = mapped_column(
        Enum(
            AttendanceStatus,
            name="attendance_status",
            native_enum=True,
            values_callable=lambda x: [e.value for e in x],
        ),
        default=AttendanceStatus.PRESENT,
        nullable=False,
    )
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    journal: Mapped["TeachingJournal"] = relationship("TeachingJournal", back_populates="attendances")
    student: Mapped["User"] = relationship("User")


__all__ = ["AttendanceStatus", "TeachingJournal", "JournalAttendance"]
