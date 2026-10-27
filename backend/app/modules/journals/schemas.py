from datetime import date as py_date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.journals.models import AttendanceStatus


# --- Attendance Schemas ---

class AttendanceItem(BaseModel):
    student_id: int
    status: AttendanceStatus = AttendanceStatus.PRESENT
    score: Optional[float] = None
    notes: Optional[str] = None


class AttendanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    status: AttendanceStatus
    score: Optional[float] = None
    notes: Optional[str] = None
    student_name: Optional[str] = None
    student_email: Optional[str] = None


# --- Journal Schemas ---

class JournalCreate(BaseModel):
    class_id: int
    title: str = Field(..., max_length=255)
    date: py_date
    start_time: Optional[str] = Field(None, max_length=10)
    end_time: Optional[str] = Field(None, max_length=10)
    planned_materials: List[int] = Field(default_factory=list)
    completed_materials: List[int] = Field(default_factory=list)
    notes: Optional[str] = None
    attendances: List[AttendanceItem] = Field(default_factory=list)


class JournalUpdate(BaseModel):
    class_id: Optional[int] = None
    title: Optional[str] = Field(None, max_length=255)
    date: Optional[py_date] = None
    start_time: Optional[str] = Field(None, max_length=10)
    end_time: Optional[str] = Field(None, max_length=10)
    planned_materials: Optional[List[int]] = None
    completed_materials: Optional[List[int]] = None
    notes: Optional[str] = None
    attendances: Optional[List[AttendanceItem]] = None


class JournalListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: UUID
    teacher_id: int
    class_id: int
    class_name: Optional[str] = None
    title: str
    date: py_date
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    planned_materials: List[int]
    completed_materials: List[int]
    total_students: int = 0
    present_students: int = 0
    avg_score: Optional[float] = None
    created_at: datetime


class JournalDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: UUID
    teacher_id: int
    class_id: int
    class_name: Optional[str] = None
    title: str
    date: py_date
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    planned_materials: List[int]
    completed_materials: List[int]
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    attendances: List[AttendanceResponse] = Field(default_factory=list)
