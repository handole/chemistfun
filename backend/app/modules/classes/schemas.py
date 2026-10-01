from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from app.modules.classes.models import GradeLevel


# --- Class Schemas ---

class ClassBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Class name, e.g. X-1 or XI-Kimia-A")
    grade_level: GradeLevel = Field(default=GradeLevel.X, description="Grade level: X, XI, or XII")


class ClassCreate(ClassBase):
    teacher_id: Optional[int] = Field(None, description="ID of the teacher user (inferred from auth token if omitted)")
    enrollment_code: Optional[str] = Field(None, max_length=50, description="Unique join code, auto-generated if empty")


class ClassUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    grade_level: Optional[GradeLevel] = None
    enrollment_code: Optional[str] = Field(None, max_length=50)


class ClassResponse(ClassBase):
    id: int
    uuid: UUID
    teacher_id: int
    enrollment_code: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- ClassStudent (Junction) Schemas ---

class ClassStudentBase(BaseModel):
    class_id: int
    student_id: int


class ClassStudentCreate(BaseModel):
    student_id: int = Field(..., description="ID of the student user to enroll")


class ClassEnrollByCode(BaseModel):
    enrollment_code: str = Field(..., min_length=4, max_length=50, description="Class enrollment code")
    student_id: Optional[int] = Field(None, description="ID of the student user (inferred from auth token if omitted)")


class ClassStudentResponse(ClassStudentBase):
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)


__all__ = [
    "ClassBase",
    "ClassCreate",
    "ClassUpdate",
    "ClassResponse",
    "ClassStudentBase",
    "ClassStudentCreate",
    "ClassEnrollByCode",
    "ClassStudentResponse",
]
