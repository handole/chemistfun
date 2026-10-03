from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.classes.models import GradeLevel
from app.modules.content.models import Material, Module, VirtualLab, VirtualLabStatus
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
    async def get_module_by_id(db: AsyncSession, module_id: int) -> Optional[Module]:
        result = await db.execute(select(Module).where(Module.id == module_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_module_by_uuid(db: AsyncSession, module_uuid: UUID) -> Optional[Module]:
        result = await db.execute(select(Module).where(Module.uuid == module_uuid))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_modules_by_grade_level(db: AsyncSession, grade_level: GradeLevel) -> List[Module]:
        query = (
            select(Module)
            .where(Module.grade_level == grade_level)
            .order_by(Module.order_index.asc(), Module.id.asc())
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_all_modules(db: AsyncSession) -> List[Module]:
        query = (
            select(Module)
            .order_by(Module.grade_level.asc(), Module.order_index.asc(), Module.id.asc())
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def create_module(db: AsyncSession, obj_in: ModuleCreate) -> Module:
        db_obj = Module(
            grade_level=obj_in.grade_level,
            title=obj_in.title,
            order_index=obj_in.order_index,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def update_module(
        db: AsyncSession,
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
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def delete_module(db: AsyncSession, module_id: int) -> Optional[Module]:
        module_obj = await ContentController.get_module_by_id(db, module_id=module_id)
        if module_obj:
            await db.delete(module_obj)
            await db.commit()
        return module_obj

    # =========================================================================
    # Material Operations
    # =========================================================================

    @staticmethod
    async def get_material_by_id(db: AsyncSession, material_id: int) -> Optional[Material]:
        result = await db.execute(select(Material).where(Material.id == material_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_material_by_uuid(db: AsyncSession, material_uuid: UUID) -> Optional[Material]:
        result = await db.execute(select(Material).where(Material.uuid == material_uuid))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_materials_by_module(
        db: AsyncSession,
        module_id: int,
        published_only: bool = False,
    ) -> List[Material]:
        query = select(Material).where(Material.module_id == module_id)
        if published_only:
            query = query.where(Material.is_published.is_(True))
        query = query.order_by(Material.order_index.asc(), Material.id.asc())
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def create_material(db: AsyncSession, obj_in: MaterialCreate) -> Material:
        db_obj = Material(
            module_id=obj_in.module_id,
            title=obj_in.title,
            content_html=obj_in.content_html,
            order_index=obj_in.order_index,
            is_published=obj_in.is_published,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def update_material(
        db: AsyncSession,
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
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def delete_material(db: AsyncSession, material_id: int) -> Optional[Material]:
        material_obj = await ContentController.get_material_by_id(db, material_id=material_id)
        if material_obj:
            await db.delete(material_obj)
            await db.commit()
        return material_obj

    # =========================================================================
    # VirtualLab Operations (1-to-1 with Material)
    # =========================================================================

    @staticmethod
    async def list_virtual_labs(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 50,
        status: Optional[VirtualLabStatus] = None,
    ) -> List[VirtualLab]:
        query = select(VirtualLab).offset(skip).limit(limit).order_by(VirtualLab.id.desc())
        if status:
            query = query.where(VirtualLab.status == status)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_virtual_lab_by_id(db: AsyncSession, lab_id: int) -> Optional[VirtualLab]:
        result = await db.execute(select(VirtualLab).where(VirtualLab.id == lab_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_virtual_lab_by_uuid(db: AsyncSession, lab_uuid: UUID) -> Optional[VirtualLab]:
        result = await db.execute(select(VirtualLab).where(VirtualLab.uuid == lab_uuid))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_virtual_lab_by_material(db: AsyncSession, material_id: int) -> Optional[VirtualLab]:
        result = await db.execute(select(VirtualLab).where(VirtualLab.material_id == material_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_or_update_virtual_lab(db: AsyncSession, obj_in: VirtualLabCreate) -> VirtualLab:
        existing = await ContentController.get_virtual_lab_by_material(db, material_id=obj_in.material_id)
        if existing:
            existing.ai_prompt_history = obj_in.ai_prompt_history
            existing.config_data = obj_in.config_data
            existing.status = obj_in.status
            db.add(existing)
            await db.commit()
            await db.refresh(existing)
            return existing

        db_obj = VirtualLab(
            material_id=obj_in.material_id,
            ai_prompt_history=obj_in.ai_prompt_history,
            config_data=obj_in.config_data,
            status=obj_in.status,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def update_virtual_lab(
        db: AsyncSession,
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
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def delete_virtual_lab(db: AsyncSession, lab_id: int) -> Optional[VirtualLab]:
        lab_obj = await ContentController.get_virtual_lab_by_id(db, lab_id=lab_id)
        if lab_obj:
            await db.delete(lab_obj)
            await db.commit()
        return lab_obj


content_controller = ContentController()

__all__ = ["ContentController", "content_controller"]
