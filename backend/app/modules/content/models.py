import enum
import uuid as py_uuid
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.modules.classes.models import Class
    from app.modules.assessment.models import EvaluationMetric, Quiz


class VirtualLabStatus(str, enum.Enum):
    DRAFT = "draft"
    GENERATING = "generating"
    READY = "ready"
    ERROR = "error"


class Module(Base):
    """Bab atau topik besar di dalam kelas."""
    __tablename__ = "modules"

    id: Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True)
    uuid: Mapped[py_uuid.UUID] = mapped_column(UUID(as_uuid=True),default=py_uuid.uuid4,unique=True,nullable=False,index=True)
    class_id: Mapped[int] = mapped_column(Integer,ForeignKey("classes.id", ondelete="CASCADE"),nullable=False,index=True)
    title: Mapped[str] = mapped_column(String(255),nullable=False)
    order_index: Mapped[int] = mapped_column(Integer,default=0,nullable=False)

    # Relationships
    class_: Mapped["Class"] = relationship("Class",back_populates="modules")
    materials: Mapped[List["Material"]] = relationship("Material",back_populates="module",cascade="all, delete-orphan",order_by="Material.order_index")
    evaluation_metrics: Mapped[List["EvaluationMetric"]] = relationship("EvaluationMetric",back_populates="module",cascade="all, delete-orphan")
    quiz: Mapped[Optional["Quiz"]] = relationship("Quiz",back_populates="module",uselist=False,cascade="all, delete-orphan")


class Material(Base):
    """Materi teoritikal di dalam modul."""
    __tablename__ = "materials"

    id: Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True)
    uuid: Mapped[py_uuid.UUID] = mapped_column(UUID(as_uuid=True),default=py_uuid.uuid4,unique=True,nullable=False,index=True)
    module_id: Mapped[int] = mapped_column(Integer,ForeignKey("modules.id", ondelete="CASCADE"),nullable=False,index=True)
    title: Mapped[str] = mapped_column(String(255),nullable=False)
    content_html: Mapped[Optional[str]] = mapped_column(Text,nullable=True)
    order_index: Mapped[int] = mapped_column(Integer,default=0,nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean,default=False,nullable=False)

    # Relationships
    module: Mapped["Module"] = relationship("Module",back_populates="materials")
    virtual_lab: Mapped[Optional["VirtualLab"]] = relationship("VirtualLab",back_populates="material",uselist=False,cascade="all, delete-orphan")


class VirtualLab(Base):
    """Menyimpan konfigurasi animasi simulasi (termasuk hasil generate AI)."""
    __tablename__ = "virtual_labs"

    id: Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True)
    uuid: Mapped[py_uuid.UUID] = mapped_column(UUID(as_uuid=True),default=py_uuid.uuid4,unique=True,nullable=False,index=True)
    material_id: Mapped[int] = mapped_column(Integer,ForeignKey("materials.id", ondelete="CASCADE"),unique=True,nullable=False)
    ai_prompt_history: Mapped[Optional[str]] = mapped_column(Text,nullable=True)
    config_data: Mapped[Dict[str, Any]] = mapped_column(JSONB,default=dict,nullable=False)
    status: Mapped[VirtualLabStatus] = mapped_column(Enum(    VirtualLabStatus,    name="virtual_lab_status",    native_enum=True,    values_callable=lambda x: [e.value for e in x],),default=VirtualLabStatus.DRAFT,nullable=False)

    # Relationships
    material: Mapped["Material"] = relationship("Material",back_populates="virtual_lab")


__all__ = ["VirtualLabStatus", "Module", "Material", "VirtualLab"]
