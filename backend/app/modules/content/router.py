from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.modules.content.controller import ContentController
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
)
from app.modules.content.chemistry_engine import ChemistryEngine
from app.modules.users.models import User, UserRole
from app.utils.dependencies import (
    get_current_user,
    get_db,
    require_record,
    require_teacher,
)

router = APIRouter(prefix="/content", tags=["Content"])


# =========================================================================
# Modules
# =========================================================================

@router.get(
    "/modules",
    response_model=List[ModuleResponse],
    summary="List modules by class ID (Authenticated)",
)
def list_modules(
    class_id: int = Query(..., description="Filter by class ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ContentController.get_modules_by_class(db, class_id=class_id)


@router.post(
    "/modules",
    response_model=ModuleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new module (Teacher only)",
)
def create_module(
    payload: ModuleCreate,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    return ContentController.create_module(db, obj_in=payload)


@router.get(
    "/modules/{module_uuid}",
    response_model=ModuleResponse,
    summary="Get module by UUID (Authenticated)",
)
def get_module(
    module_uuid: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return require_record(
        ContentController.get_module_by_uuid(db, module_uuid=module_uuid),
        detail=f"Module '{module_uuid}' not found.",
    )


@router.patch(
    "/modules/{module_uuid}",
    response_model=ModuleResponse,
    summary="Update module by UUID (Teacher only)",
)
def update_module(
    module_uuid: UUID,
    payload: ModuleUpdate,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    module = require_record(
        ContentController.get_module_by_uuid(db, module_uuid=module_uuid),
        detail=f"Module '{module_uuid}' not found.",
    )
    return ContentController.update_module(db, db_obj=module, obj_in=payload)


@router.delete(
    "/modules/{module_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete module by UUID (Teacher only)",
)
def delete_module(
    module_uuid: UUID,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    module = require_record(
        ContentController.get_module_by_uuid(db, module_uuid=module_uuid),
        detail=f"Module '{module_uuid}' not found.",
    )
    ContentController.delete_module(db, module_id=module.id)


# =========================================================================
# Materials
# =========================================================================

@router.get(
    "/materials",
    response_model=List[MaterialResponse],
    summary="List materials by module ID (Students see published only)",
)
def list_materials(
    module_id: int = Query(..., description="Filter by module ID"),
    published_only: bool = Query(default=False, description="Explicit published-only filter"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Enforce published_only=True for students
    effective_published_only = published_only or (current_user.role == UserRole.STUDENT)
    return ContentController.get_materials_by_module(
        db, module_id=module_id, published_only=effective_published_only
    )


@router.post(
    "/materials",
    response_model=MaterialResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new material (Teacher only)",
)
def create_material(
    payload: MaterialCreate,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    return ContentController.create_material(db, obj_in=payload)


@router.get(
    "/materials/{material_uuid}",
    response_model=MaterialResponse,
    summary="Get material by UUID (Authenticated)",
)
def get_material(
    material_uuid: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    material = require_record(
        ContentController.get_material_by_uuid(db, material_uuid=material_uuid),
        detail=f"Material '{material_uuid}' not found.",
    )
    # Students cannot view unpublished drafts
    if current_user.role == UserRole.STUDENT and not material.is_published:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material is not published yet.",
        )
    return material


@router.patch(
    "/materials/{material_uuid}",
    response_model=MaterialResponse,
    summary="Update material by UUID (Teacher only)",
)
def update_material(
    material_uuid: UUID,
    payload: MaterialUpdate,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    material = require_record(
        ContentController.get_material_by_uuid(db, material_uuid=material_uuid),
        detail=f"Material '{material_uuid}' not found.",
    )
    return ContentController.update_material(db, db_obj=material, obj_in=payload)


@router.delete(
    "/materials/{material_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete material by UUID (Teacher only)",
)
def delete_material(
    material_uuid: UUID,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    material = require_record(
        ContentController.get_material_by_uuid(db, material_uuid=material_uuid),
        detail=f"Material '{material_uuid}' not found.",
    )
    ContentController.delete_material(db, material_id=material.id)


# =========================================================================
# Virtual Labs  (1-to-1 with Material)
# =========================================================================

@router.get(
    "/materials/{material_uuid}/lab",
    response_model=VirtualLabResponse,
    summary="Get virtual lab configuration for a material (Authenticated)",
)
def get_virtual_lab(
    material_uuid: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    material = require_record(
        ContentController.get_material_by_uuid(db, material_uuid=material_uuid),
        detail=f"Material '{material_uuid}' not found.",
    )
    if current_user.role == UserRole.STUDENT and not material.is_published:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material is not published yet.",
        )
    return require_record(
        ContentController.get_virtual_lab_by_material(db, material_id=material.id),
        detail=f"Virtual lab for material '{material_uuid}' not found.",
    )


@router.put(
    "/materials/{material_uuid}/lab",
    response_model=VirtualLabResponse,
    status_code=status.HTTP_200_OK,
    summary="Create or update virtual lab configuration (Teacher only)",
)
def upsert_virtual_lab(
    material_uuid: UUID,
    payload: VirtualLabCreate,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    material = require_record(
        ContentController.get_material_by_uuid(db, material_uuid=material_uuid),
        detail=f"Material '{material_uuid}' not found.",
    )
    payload_data = payload.model_dump()
    payload_data["material_id"] = material.id
    updated_payload = VirtualLabCreate(**payload_data)
    return ContentController.create_or_update_virtual_lab(db, obj_in=updated_payload)


@router.patch(
    "/labs/{lab_uuid}",
    response_model=VirtualLabResponse,
    summary="Update virtual lab by UUID (Teacher only)",
)
def update_virtual_lab(
    lab_uuid: UUID,
    payload: VirtualLabUpdate,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    lab = require_record(
        ContentController.get_virtual_lab_by_uuid(db, lab_uuid=lab_uuid),
        detail=f"Virtual lab '{lab_uuid}' not found.",
    )
    return ContentController.update_virtual_lab(db, db_obj=lab, obj_in=payload)


@router.delete(
    "/labs/{lab_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete virtual lab by UUID (Teacher only)",
)
def delete_virtual_lab(
    lab_uuid: UUID,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    lab = require_record(
        ContentController.get_virtual_lab_by_uuid(db, lab_uuid=lab_uuid),
        detail=f"Virtual lab '{lab_uuid}' not found.",
    )
    ContentController.delete_virtual_lab(db, lab_id=lab.id)


@router.post(
    "/labs/verify-inquiry",
    response_model=VerifyInquiryResponse,
    summary="Verify student answer for E-LKPD inquiry question",
)
def verify_inquiry_answer(
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

