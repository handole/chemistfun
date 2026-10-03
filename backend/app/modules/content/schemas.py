from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.classes.models import GradeLevel
from app.modules.content.models import VirtualLabStatus


# --- Module Schemas ---

class ModuleBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Module/Chapter title")
    order_index: int = Field(default=0, ge=0, description="Display order index")


class ModuleCreate(ModuleBase):
    grade_level: GradeLevel = Field(default=GradeLevel.X, description="Grade level: X, XI, or XII")


class ModuleUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    grade_level: Optional[GradeLevel] = None
    order_index: Optional[int] = Field(None, ge=0)


class ModuleResponse(ModuleBase):
    id: int
    uuid: UUID
    grade_level: GradeLevel

    model_config = ConfigDict(from_attributes=True)


# --- Material Schemas ---

class MaterialBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Material title")
    content_html: Optional[str] = Field(None, description="Rich text / HTML content")
    order_index: int = Field(default=0, ge=0, description="Display order index")
    is_published: bool = Field(default=False, description="Publication status")


class MaterialCreate(MaterialBase):
    module_id: int = Field(..., description="ID of the parent module")


class MaterialUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content_html: Optional[str] = None
    order_index: Optional[int] = Field(None, ge=0)
    is_published: Optional[bool] = None


class MaterialResponse(MaterialBase):
    id: int
    uuid: UUID
    module_id: int

    model_config = ConfigDict(from_attributes=True)


# --- VirtualLab Schemas ---

class VirtualLabBase(BaseModel):
    ai_prompt_history: Optional[str] = Field(None, description="Teacher prompt history to AI")
    config_data: Dict[str, Any] = Field(default_factory=dict, description="AI/Simulation config parameters for Vue.js")
    status: VirtualLabStatus = Field(default=VirtualLabStatus.DRAFT, description="Status of the virtual lab")


class VirtualLabCreate(VirtualLabBase):
    material_id: int = Field(..., description="1-to-1 material ID")


class VirtualLabUpdate(BaseModel):
    ai_prompt_history: Optional[str] = None
    config_data: Optional[Dict[str, Any]] = None
    status: Optional[VirtualLabStatus] = None


class VirtualLabResponse(VirtualLabBase):
    id: int
    uuid: UUID
    material_id: int

    model_config = ConfigDict(from_attributes=True)


class VerifyInquiryRequest(BaseModel):
    stage: int = Field(..., ge=1, le=5, description="Stage number 1 to 5")
    user_answer: Any = Field(..., description="Student answer (float, string, or dict)")
    inputs: Dict[str, Any] = Field(default_factory=dict, description="Current simulation state/inputs")


class VerifyInquiryResponse(BaseModel):
    is_correct: bool
    correct_value: Optional[Any] = None
    explanation: str


class AILabGenerateRequest(BaseModel):
    teacher_prompt: str = Field(..., min_length=3, description="Prompt guru ke AI")
    material_uuid: Optional[UUID] = Field(None, description="UUID materi kimia terkait")


class AILabGenerateResponse(BaseModel):
    config_data: Dict[str, Any]
    ai_prompt_history: str


class AIMaterialGenerateRequest(BaseModel):
    topic: str = Field(..., min_length=2, description="Topik sub-materi yang ingin dibuat")
    module_id: Optional[int] = Field(None, description="ID modul terkait")


class AIMaterialGenerateResponse(BaseModel):
    title: str
    content_html: str


class AIChemBotRequest(BaseModel):
    question: str = Field(..., min_length=2, description="Pertanyaan kimia siswa")


class AIChemBotResponse(BaseModel):
    answer: str



__all__ = [
    "ModuleBase",
    "ModuleCreate",
    "ModuleUpdate",
    "ModuleResponse",
    "MaterialBase",
    "MaterialCreate",
    "MaterialUpdate",
    "MaterialResponse",
    "VirtualLabBase",
    "VirtualLabCreate",
    "VirtualLabUpdate",
    "VirtualLabResponse",
    "VerifyInquiryRequest",
    "VerifyInquiryResponse",
    "AILabGenerateRequest",
    "AILabGenerateResponse",
    "AIMaterialGenerateRequest",
    "AIMaterialGenerateResponse",
    "AIChemBotRequest",
    "AIChemBotResponse",
]

