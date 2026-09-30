from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.content.controller import ContentController
from app.modules.content.models import VirtualLabStatus
from app.modules.content.schemas import (
    MaterialCreate,
    MaterialResponse,
    MaterialUpdate,
    ModuleCreate,
    ModuleResponse,
    ModuleUpdate,
    VirtualLabCreate,
    VirtualLabResponse,
    VirtualLabUpdate,
    VerifyInquiryRequest,
    VerifyInquiryResponse,
    AILabGenerateRequest,
    AILabGenerateResponse,
    AIMaterialGenerateRequest,
    AIMaterialGenerateResponse,
    AIChemBotRequest,
    AIChemBotResponse,
)
from app.modules.content.chemistry_engine import ChemistryEngine
from app.services.ai_generator import AIGenerator
from app.modules.users.models import User, UserRole
from app.utils.dependencies import (
    get_current_user,
    get_db,
    require_record,
    require_teacher,
)

router = APIRouter(prefix="/content", tags=["Content"])


# =============================================================================
# Modules Endpoints
# =============================================================================

@router.get(
    "/modules",
    response_model=List[ModuleResponse],
    summary="List modules by class ID",
)
async def list_modules(
    class_id: int = Query(..., description="Parent class ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ContentController.get_modules_by_class(db, class_id=class_id)


@router.post(
    "/modules",
    response_model=ModuleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new chapter/module (Teacher only)",
)
async def create_module(
    payload: ModuleCreate,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    return await ContentController.create_module(db, obj_in=payload)


@router.get(
    "/modules/{module_uuid}",
    response_model=ModuleResponse,
    summary="Get module by UUID",
)
async def get_module(
    module_uuid: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return require_record(
        await ContentController.get_module_by_uuid(db, module_uuid=module_uuid),
        detail=f"Module '{module_uuid}' not found.",
    )


@router.patch(
    "/modules/{module_uuid}",
    response_model=ModuleResponse,
    summary="Update module by UUID (Teacher only)",
)
async def update_module(
    module_uuid: UUID,
    payload: ModuleUpdate,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    module = require_record(
        await ContentController.get_module_by_uuid(db, module_uuid=module_uuid),
        detail=f"Module '{module_uuid}' not found.",
    )
    return await ContentController.update_module(db, db_obj=module, obj_in=payload)


@router.delete(
    "/modules/{module_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete module by UUID (Teacher only)",
)
async def delete_module(
    module_uuid: UUID,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    module = require_record(
        await ContentController.get_module_by_uuid(db, module_uuid=module_uuid),
        detail=f"Module '{module_uuid}' not found.",
    )
    await ContentController.delete_module(db, module_id=module.id)


# =============================================================================
# Materials Endpoints
# =============================================================================

@router.get(
    "/materials",
    response_model=List[MaterialResponse],
    summary="List materials by module ID",
)
async def list_materials(
    module_id: int = Query(..., description="Parent module ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Students can only view published materials
    published_only = (current_user.role == UserRole.STUDENT)
    return await ContentController.get_materials_by_module(
        db, module_id=module_id, published_only=published_only
    )


@router.post(
    "/materials",
    response_model=MaterialResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new material item (Teacher only)",
)
async def create_material(
    payload: MaterialCreate,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    return await ContentController.create_material(db, obj_in=payload)


@router.get(
    "/materials/{material_uuid}",
    response_model=MaterialResponse,
    summary="Get material by UUID",
)
async def get_material(
    material_uuid: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    material = require_record(
        await ContentController.get_material_by_uuid(db, material_uuid=material_uuid),
        detail=f"Material '{material_uuid}' not found.",
    )
    if current_user.role == UserRole.STUDENT and not material.is_published:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This material is currently in draft mode.",
        )
    return material


@router.patch(
    "/materials/{material_uuid}",
    response_model=MaterialResponse,
    summary="Update material by UUID (Teacher only)",
)
async def update_material(
    material_uuid: UUID,
    payload: MaterialUpdate,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    material = require_record(
        await ContentController.get_material_by_uuid(db, material_uuid=material_uuid),
        detail=f"Material '{material_uuid}' not found.",
    )
    return await ContentController.update_material(db, db_obj=material, obj_in=payload)


@router.delete(
    "/materials/{material_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete material by UUID (Teacher only)",
)
async def delete_material(
    material_uuid: UUID,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    material = require_record(
        await ContentController.get_material_by_uuid(db, material_uuid=material_uuid),
        detail=f"Material '{material_uuid}' not found.",
    )
    await ContentController.delete_material(db, material_id=material.id)


# =============================================================================
# Virtual Lab Endpoints (1-to-1 attached to Material)
# =============================================================================

@router.get(
    "/labs",
    response_model=List[VirtualLabResponse],
    summary="List all virtual lab configurations",
)
async def list_virtual_labs(
    status: Optional[VirtualLabStatus] = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ContentController.list_virtual_labs(
        db, skip=skip, limit=limit, status=status
    )


@router.get(
    "/labs/{lab_uuid}",
    response_model=VirtualLabResponse,
    summary="Get virtual lab configuration by its own UUID",
)
async def get_virtual_lab_by_uuid(
    lab_uuid: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    lab = await ContentController.get_virtual_lab_by_uuid(db, lab_uuid=lab_uuid)
    if not lab:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Virtual lab '{lab_uuid}' not found.",
        )
    return lab


@router.get(
    "/materials/{material_uuid}/lab",
    response_model=VirtualLabResponse,
    summary="Get virtual lab configuration by material UUID",
)
async def get_virtual_lab(
    material_uuid: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    material = require_record(
        await ContentController.get_material_by_uuid(db, material_uuid=material_uuid),
        detail=f"Material '{material_uuid}' not found.",
    )
    lab = await ContentController.get_virtual_lab_by_material(db, material_id=material.id)
    if not lab:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No virtual lab configured for material '{material_uuid}'.",
        )
    return lab


@router.put(
    "/materials/{material_uuid}/lab",
    response_model=VirtualLabResponse,
    summary="Create or update virtual lab configuration for a material (Teacher only)",
)
async def upsert_virtual_lab(
    material_uuid: UUID,
    payload: VirtualLabCreate,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    material = require_record(
        await ContentController.get_material_by_uuid(db, material_uuid=material_uuid),
        detail=f"Material '{material_uuid}' not found.",
    )
    payload_data = payload.model_dump()
    payload_data["material_id"] = material.id
    updated_payload = VirtualLabCreate(**payload_data)
    return await ContentController.create_or_update_virtual_lab(db, obj_in=updated_payload)


@router.patch(
    "/labs/{lab_uuid}",
    response_model=VirtualLabResponse,
    summary="Update virtual lab by UUID (Teacher only)",
)
async def update_virtual_lab(
    lab_uuid: UUID,
    payload: VirtualLabUpdate,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    lab = require_record(
        await ContentController.get_virtual_lab_by_uuid(db, lab_uuid=lab_uuid),
        detail=f"Virtual lab '{lab_uuid}' not found.",
    )
    return await ContentController.update_virtual_lab(db, db_obj=lab, obj_in=payload)


@router.delete(
    "/labs/{lab_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete virtual lab by UUID (Teacher only)",
)
async def delete_virtual_lab(
    lab_uuid: UUID,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    lab = require_record(
        await ContentController.get_virtual_lab_by_uuid(db, lab_uuid=lab_uuid),
        detail=f"Virtual lab '{lab_uuid}' not found.",
    )
    await ContentController.delete_virtual_lab(db, lab_id=lab.id)


@router.post(
    "/labs/verify-inquiry",
    response_model=VerifyInquiryResponse,
    summary="Verify student answer for E-LKPD inquiry question",
)
async def verify_inquiry_answer(
    payload: VerifyInquiryRequest,
    current_user: User = Depends(get_current_user),
):
    is_correct, correct_val, explanation = ChemistryEngine.verify_stoichiometry_inquiry(
        stage=payload.stage,
        user_answer=payload.user_answer,
        inputs=payload.inputs,
    )
    return VerifyInquiryResponse(
        is_correct=is_correct,
        correct_value=correct_val,
        explanation=explanation,
    )


# =============================================================================
# AI Generation Endpoints (Powered by AIGenerator & PromptEngine)
# =============================================================================

@router.post(
    "/labs/generate-ai",
    response_model=AILabGenerateResponse,
    summary="Generate virtual lab simulation parameters using AI (Teacher only)",
)
async def generate_virtual_lab_ai(
    payload: AILabGenerateRequest,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    mat_title = None
    mat_content = None
    if payload.material_uuid:
        mat = await ContentController.get_material_by_uuid(db, material_uuid=payload.material_uuid)
        if mat:
            mat_title = mat.title
            mat_content = mat.content_html

    try:
        config_data = await AIGenerator.generate_virtual_lab(
            teacher_prompt=payload.teacher_prompt,
            material_title=mat_title,
            material_content=mat_content,
        )
        return AILabGenerateResponse(
            config_data=config_data,
            ai_prompt_history=payload.teacher_prompt,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal generate lab via AI: {str(exc)}",
        )


@router.post(
    "/materials/generate-ai",
    response_model=AIMaterialGenerateResponse,
    summary="Generate chemistry learning material content using AI (Teacher only)",
)
async def generate_material_ai(
    payload: AIMaterialGenerateRequest,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    mod_title = None
    if payload.module_id:
        mod = await ContentController.get_module_by_id(db, module_id=payload.module_id)
        if mod:
            mod_title = mod.title

    try:
        data = await AIGenerator.generate_material(
            topic=payload.topic,
            module_title=mod_title,
        )
        return AIMaterialGenerateResponse(
            title=data.get("title", payload.topic),
            content_html=data.get("content_html", ""),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal generate materi via AI: {str(exc)}",
        )


@router.post(
    "/chembot/chat",
    response_model=AIChemBotResponse,
    summary="Chat with Kimi AI Tutor (Students & Teachers)",
)
async def chat_with_chembot(
    payload: AIChemBotRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        answer = await AIGenerator.ask_chembot(payload.question)
        return AIChemBotResponse(answer=answer)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Kimi mengalami kendala: {str(exc)}",
        )

