from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.content.models import VirtualLabStatus


# --- Module Schemas ---

class ModuleBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Module/Chapter title")
    order_index: int = Field(default=0, ge=0, description="Display order index")


class ModuleCreate(ModuleBase):
    class_id: int = Field(..., description="ID of the parent class")


class ModuleUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    order_index: Optional[int] = Field(None, ge=0)


class ModuleResponse(ModuleBase):
    id: int
    uuid: UUID
    class_id: int

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
]

