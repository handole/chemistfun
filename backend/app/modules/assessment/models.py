import enum
import uuid as py_uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.modules.users.models import User
    from app.modules.content.models import Module


class QuestionType(str, enum.Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"


class EvaluationMetric(Base):
    """Indikator pemahaman untuk analisis Radar Chart."""
    __tablename__ = "evaluation_metrics"

    id: Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True)
    uuid: Mapped[py_uuid.UUID] = mapped_column(UUID(as_uuid=True),default=py_uuid.uuid4,unique=True,nullable=False,index=True)
    module_id: Mapped[int] = mapped_column(Integer,ForeignKey("modules.id", ondelete="CASCADE"),nullable=False,index=True)
    metric_name: Mapped[str] = mapped_column(String(255),nullable=False)

    # Relationships
    module: Mapped["Module"] = relationship("Module",back_populates="evaluation_metrics")
    questions: Mapped[List["Question"]] = relationship("Question",back_populates="metric")


class Quiz(Base):
    """Kuis evaluasi yang melekat pada modul (1-to-1)."""
    __tablename__ = "quizzes"

    id: Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True)
    uuid: Mapped[py_uuid.UUID] = mapped_column(UUID(as_uuid=True),default=py_uuid.uuid4,unique=True,nullable=False,index=True)
    module_id: Mapped[int] = mapped_column(Integer,ForeignKey("modules.id", ondelete="CASCADE"),unique=True,nullable=False)
    title: Mapped[str] = mapped_column(String(255),nullable=False)
    time_limit_minutes: Mapped[Optional[int]] = mapped_column(Integer,nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean,default=True,nullable=False)

    # Relationships
    module: Mapped["Module"] = relationship("Module",back_populates="quiz")
    questions: Mapped[List["Question"]] = relationship("Question",back_populates="quiz",cascade="all, delete-orphan")
    attempts: Mapped[List["StudentQuizAttempt"]] = relationship("StudentQuizAttempt",back_populates="quiz",cascade="all, delete-orphan")


class Question(Base):
    """Butir soal kuis yang menguji indikator metrik tertentu."""
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True)
    uuid: Mapped[py_uuid.UUID] = mapped_column(UUID(as_uuid=True),default=py_uuid.uuid4,unique=True,nullable=False,index=True)
    quiz_id: Mapped[int] = mapped_column(Integer,ForeignKey("quizzes.id", ondelete="CASCADE"),nullable=False,index=True)
    metric_id: Mapped[Optional[int]] = mapped_column(Integer,ForeignKey("evaluation_metrics.id", ondelete="SET NULL"),nullable=True,index=True)
    question_text: Mapped[str] = mapped_column(Text,nullable=False)
    question_type: Mapped[QuestionType] = mapped_column(Enum(    QuestionType,    name="question_type",    native_enum=True,    values_callable=lambda x: [e.value for e in x],),nullable=False)
    options: Mapped[List[Dict[str, Any]]] = mapped_column(JSONB,nullable=False)
    correct_answer: Mapped[str] = mapped_column(String(50),nullable=False)
    weight_score: Mapped[int] = mapped_column(Integer,default=1,nullable=False)

    # Relationships
    quiz: Mapped["Quiz"] = relationship("Quiz",back_populates="questions")
    metric: Mapped[Optional["EvaluationMetric"]] = relationship("EvaluationMetric",back_populates="questions")
    student_answers: Mapped[List["StudentAnswer"]] = relationship("StudentAnswer",back_populates="question",cascade="all, delete-orphan")


class StudentQuizAttempt(Base):
    """Mencatat saat siswa memulai dan menyelesaikan kuis beserta analitiknya."""
    __tablename__ = "student_quiz_attempts"

    id: Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True)
    uuid: Mapped[py_uuid.UUID] = mapped_column(UUID(as_uuid=True),default=py_uuid.uuid4,unique=True,nullable=False,index=True)
    student_id: Mapped[int] = mapped_column(Integer,ForeignKey("users.id", ondelete="CASCADE"),nullable=False,index=True)
    quiz_id: Mapped[int] = mapped_column(Integer,ForeignKey("quizzes.id", ondelete="CASCADE"),nullable=False,index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True),nullable=True)
    total_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2),nullable=True)
    radar_chart_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB,nullable=True)

    # Relationships
    student: Mapped["User"] = relationship("User",back_populates="quiz_attempts")
    quiz: Mapped["Quiz"] = relationship("Quiz",back_populates="attempts")
    answers: Mapped[List["StudentAnswer"]] = relationship("StudentAnswer",back_populates="attempt",cascade="all, delete-orphan")


class StudentAnswer(Base):
    """Mencatat setiap jawaban yang dipilih siswa."""
    __tablename__ = "student_answers"

    id: Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True)
    uuid: Mapped[py_uuid.UUID] = mapped_column(UUID(as_uuid=True),default=py_uuid.uuid4,unique=True,nullable=False,index=True)
    attempt_id: Mapped[int] = mapped_column(Integer,ForeignKey("student_quiz_attempts.id", ondelete="CASCADE"),nullable=False,index=True)
    question_id: Mapped[int] = mapped_column(Integer,ForeignKey("questions.id", ondelete="CASCADE"),nullable=False,index=True)
    selected_answer: Mapped[Optional[str]] = mapped_column(String(50),nullable=True)
    is_correct: Mapped[Optional[bool]] = mapped_column(Boolean,nullable=True)

    # Relationships
    attempt: Mapped["StudentQuizAttempt"] = relationship("StudentQuizAttempt",back_populates="answers")
    question: Mapped["Question"] = relationship("Question",back_populates="student_answers")


__all__ = [
    "QuestionType",
    "EvaluationMetric",
    "Quiz",
    "Question",
    "StudentQuizAttempt",
    "StudentAnswer",
]
