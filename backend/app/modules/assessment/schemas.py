from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.assessment.models import QuestionType


# --- EvaluationMetric Schemas ---

class EvaluationMetricBase(BaseModel):
    metric_name: str = Field(..., min_length=1, max_length=255, description="Indicator/Competency name for radar chart")


class EvaluationMetricCreate(EvaluationMetricBase):
    module_id: int = Field(..., description="ID of the parent module")


class EvaluationMetricUpdate(BaseModel):
    metric_name: Optional[str] = Field(None, min_length=1, max_length=255)


class EvaluationMetricResponse(EvaluationMetricBase):
    id: int
    uuid: UUID
    module_id: int

    model_config = ConfigDict(from_attributes=True)


# --- Quiz Schemas ---

class QuizBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Quiz title")
    time_limit_minutes: Optional[int] = Field(None, ge=1, description="Time limit in minutes")
    is_active: bool = Field(default=True, description="Whether quiz is active")


class QuizCreate(QuizBase):
    module_id: int = Field(..., description="ID of the parent module (1-to-1)")


class QuizUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    time_limit_minutes: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None


class QuizResponse(QuizBase):
    id: int
    uuid: UUID
    module_id: int

    model_config = ConfigDict(from_attributes=True)


# --- Question Schemas ---

class QuestionBase(BaseModel):
    question_text: str = Field(..., min_length=1, description="Question text/prompt")
    question_type: QuestionType = Field(default=QuestionType.MULTIPLE_CHOICE, description="Question type")
    options: List[Dict[str, Any]] = Field(..., description="List of options, e.g. [{'id': 'A', 'text': '...'}]")
    correct_answer: str = Field(..., max_length=50, description="Correct option identifier, e.g. 'A'")
    weight_score: int = Field(default=1, ge=1, description="Weight/score for correct answer")


class QuestionCreate(QuestionBase):
    quiz_id: int = Field(..., description="ID of the parent quiz")
    metric_id: Optional[int] = Field(None, description="Optional evaluation metric ID")


class QuestionUpdate(BaseModel):
    metric_id: Optional[int] = None
    question_text: Optional[str] = Field(None, min_length=1)
    question_type: Optional[QuestionType] = None
    options: Optional[List[Dict[str, Any]]] = None
    correct_answer: Optional[str] = Field(None, max_length=50)
    weight_score: Optional[int] = Field(None, ge=1)


class QuestionResponse(QuestionBase):
    id: int
    uuid: UUID
    quiz_id: int
    metric_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class QuestionStudentView(BaseModel):
    """Question schema for students while taking the quiz (hides correct_answer)."""
    id: int
    uuid: UUID
    quiz_id: int
    question_text: str
    question_type: QuestionType
    options: List[Dict[str, Any]]
    weight_score: int

    model_config = ConfigDict(from_attributes=True)


# --- StudentQuizAttempt Schemas ---

class StudentQuizAttemptCreate(BaseModel):
    student_id: Optional[int] = Field(None, description="ID of the student user (inferred from auth token if omitted)")
    quiz_id: int = Field(..., description="ID of the quiz")


class StudentQuizAttemptResponse(BaseModel):
    id: int
    uuid: UUID
    student_id: int
    quiz_id: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_score: Optional[Decimal] = None
    radar_chart_data: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


# --- StudentAnswer Schemas ---

class StudentAnswerSave(BaseModel):
    attempt_id: int = Field(..., description="ID of the quiz attempt")
    question_id: int = Field(..., description="ID of the question being answered")
    selected_answer: str = Field(..., max_length=50, description="Option selected by student, e.g. 'A'")


class StudentAnswerResponse(BaseModel):
    id: int
    uuid: UUID
    attempt_id: int
    question_id: int
    selected_answer: Optional[str] = None
    is_correct: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)


__all__ = [
    "EvaluationMetricBase",
    "EvaluationMetricCreate",
    "EvaluationMetricUpdate",
    "EvaluationMetricResponse",
    "QuizBase",
    "QuizCreate",
    "QuizUpdate",
    "QuizResponse",
    "QuestionBase",
    "QuestionCreate",
    "QuestionUpdate",
    "QuestionResponse",
    "QuestionStudentView",
    "StudentQuizAttemptCreate",
    "StudentQuizAttemptResponse",
    "StudentAnswerSave",
    "StudentAnswerResponse",
]

