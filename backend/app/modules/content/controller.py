from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.content.models import Material, Module, VirtualLab
from app.modules.content.schemas import (
    MaterialCreate,
    MaterialUpdate,
    ModuleCreate,
    ModuleUpdate,
    VirtualLabCreate,
    VirtualLabUpdate,
)


class ContentController:
    # =========================================================================
    # Module Operations
    # =========================================================================

    @staticmethod
    def get_module_by_id(db: Session, module_id: int) -> Optional[Module]:
        return db.scalar(select(Module).where(Module.id == module_id))

    @staticmethod
    def get_module_by_uuid(db: Session, module_uuid: UUID) -> Optional[Module]:
        return db.scalar(select(Module).where(Module.uuid == module_uuid))

    @staticmethod
    def get_modules_by_class(db: Session, class_id: int) -> List[Module]:
        query = (
            select(Module)
            .where(Module.class_id == class_id)
            .order_by(Module.order_index.asc(), Module.id.asc())
        )
        return list(db.scalars(query).all())

    @staticmethod
    def create_module(db: Session, obj_in: ModuleCreate) -> Module:
        db_obj = Module(
            class_id=obj_in.class_id,
            title=obj_in.title,
            order_index=obj_in.order_index,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def update_module(
        db: Session,
        db_obj: Module,
        obj_in: Union[ModuleUpdate, Dict[str, Any]],
    ) -> Module:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete_module(db: Session, module_id: int) -> Optional[Module]:
        module_obj = ContentController.get_module_by_id(db, module_id=module_id)
        if module_obj:
            db.delete(module_obj)
            db.commit()
        return module_obj

    # =========================================================================
    # Material Operations
    # =========================================================================

    @staticmethod
    def get_material_by_id(db: Session, material_id: int) -> Optional[Material]:
        return db.scalar(select(Material).where(Material.id == material_id))

    @staticmethod
    def get_material_by_uuid(db: Session, material_uuid: UUID) -> Optional[Material]:
        return db.scalar(select(Material).where(Material.uuid == material_uuid))

    @staticmethod
    def get_materials_by_module(
        db: Session,
        module_id: int,
        published_only: bool = False,
    ) -> List[Material]:
        query = select(Material).where(Material.module_id == module_id)
        if published_only:
            query = query.where(Material.is_published.is_(True))
        query = query.order_by(Material.order_index.asc(), Material.id.asc())
        return list(db.scalars(query).all())

    @staticmethod
    def create_material(db: Session, obj_in: MaterialCreate) -> Material:
        db_obj = Material(
            module_id=obj_in.module_id,
            title=obj_in.title,
            content_html=obj_in.content_html,
            order_index=obj_in.order_index,
            is_published=obj_in.is_published,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def update_material(
        db: Session,
        db_obj: Material,
        obj_in: Union[MaterialUpdate, Dict[str, Any]],
    ) -> Material:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete_material(db: Session, material_id: int) -> Optional[Material]:
        material_obj = ContentController.get_material_by_id(db, material_id=material_id)
        if material_obj:
            db.delete(material_obj)
            db.commit()
        return material_obj

    # =========================================================================
    # VirtualLab Operations (1-to-1 with Material)
    # =========================================================================

    @staticmethod
    def get_virtual_lab_by_id(db: Session, lab_id: int) -> Optional[VirtualLab]:
        return db.scalar(select(VirtualLab).where(VirtualLab.id == lab_id))

    @staticmethod
    def get_virtual_lab_by_uuid(db: Session, lab_uuid: UUID) -> Optional[VirtualLab]:
        return db.scalar(select(VirtualLab).where(VirtualLab.uuid == lab_uuid))

    @staticmethod
    def get_virtual_lab_by_material(db: Session, material_id: int) -> Optional[VirtualLab]:
        return db.scalar(select(VirtualLab).where(VirtualLab.material_id == material_id))

    @staticmethod
    def create_or_update_virtual_lab(db: Session, obj_in: VirtualLabCreate) -> VirtualLab:
        existing = ContentController.get_virtual_lab_by_material(db, material_id=obj_in.material_id)
        if existing:
            existing.ai_prompt_history = obj_in.ai_prompt_history
            existing.config_data = obj_in.config_data
            existing.status = obj_in.status
            db.add(existing)
            db.commit()
            db.refresh(existing)
            return existing

        db_obj = VirtualLab(
            material_id=obj_in.material_id,
            ai_prompt_history=obj_in.ai_prompt_history,
            config_data=obj_in.config_data,
            status=obj_in.status,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def update_virtual_lab(
        db: Session,
        db_obj: VirtualLab,
        obj_in: Union[VirtualLabUpdate, Dict[str, Any]],
    ) -> VirtualLab:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete_virtual_lab(db: Session, lab_id: int) -> Optional[VirtualLab]:
        lab_obj = ContentController.get_virtual_lab_by_id(db, lab_id=lab_id)
        if lab_obj:
            db.delete(lab_obj)
            db.commit()
        return lab_obj


content_controller = ContentController()

__all__ = ["ContentController", "content_controller"]

