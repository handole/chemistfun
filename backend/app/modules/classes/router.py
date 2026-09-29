from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.modules.classes.controller import ClassController
from app.modules.classes.schemas import (
    ClassCreate,
    ClassEnrollByCode,
    ClassResponse,
    ClassStudentCreate,
    ClassStudentResponse,
    ClassUpdate,
)
from app.modules.users.models import User, UserRole
from app.modules.users.schemas import UserResponse
from app.utils.dependencies import (
    get_current_user,
    get_db,
    require_record,
    require_student,
    require_teacher,
)

router = APIRouter(prefix="/classes", tags=["Classes"])


@router.get(
    "/",
    response_model=List[ClassResponse],
    summary="List classes (all classes or filtered by teacher)",
)
def list_classes(
    teacher_id: Optional[int] = Query(default=None, description="Filter by teacher user ID"),
    my_classes: bool = Query(default=False, description="If true, return classes enrolled by current student"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List classes. Teachers browse own classes, students can see their enrolled classes or all."""
    if my_classes and current_user.role == UserRole.STUDENT:
        return ClassController.get_student_classes(db, student_id=current_user.id)
    return ClassController.get_multi(db, teacher_id=teacher_id, skip=skip, limit=limit)


@router.post(
    "/",
    response_model=ClassResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new class (Teacher only)",
)
def create_class(
    payload: ClassCreate,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    """Create a new class. The authenticated teacher is automatically assigned as owner."""
    if not payload.teacher_id:
        payload.teacher_id = current_user.id
    elif payload.teacher_id != current_user.id:
        # Teachers cannot assign classes to another teacher
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot assign class ownership to another user.",
        )
    return ClassController.create_class(db, obj_in=payload)


@router.get(
    "/{class_uuid}",
    response_model=ClassResponse,
    summary="Get class by UUID",
)
def get_class(
    class_uuid: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return require_record(
        ClassController.get_by_uuid(db, class_uuid=class_uuid),
        detail=f"Class '{class_uuid}' not found.",
    )


@router.patch(
    "/{class_uuid}",
    response_model=ClassResponse,
    summary="Update class by UUID (Teacher owner only)",
)
def update_class(
    class_uuid: UUID,
    payload: ClassUpdate,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    class_obj = require_record(
        ClassController.get_by_uuid(db, class_uuid=class_uuid),
        detail=f"Class '{class_uuid}' not found.",
    )
    if class_obj.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit classes that you teach.",
        )
    return ClassController.update_class(db, db_obj=class_obj, obj_in=payload)


@router.delete(
    "/{class_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete class by UUID (Teacher owner only)",
)
def delete_class(
    class_uuid: UUID,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    class_obj = require_record(
        ClassController.get_by_uuid(db, class_uuid=class_uuid),
        detail=f"Class '{class_uuid}' not found.",
    )
    if class_obj.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete classes that you teach.",
        )
    ClassController.delete_class(db, class_id=class_obj.id)


# --- Student Enrollment ---

@router.post(
    "/{class_uuid}/students",
    response_model=ClassStudentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Enroll a student by student ID (Teacher only)",
)
def enroll_student(
    class_uuid: UUID,
    payload: ClassStudentCreate,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    class_obj = require_record(
        ClassController.get_by_uuid(db, class_uuid=class_uuid),
        detail=f"Class '{class_uuid}' not found.",
    )
    if class_obj.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the class teacher can directly enroll students by ID.",
        )
    return ClassController.enroll_student(db, class_id=class_obj.id, student_id=payload.student_id)


@router.post(
    "/enroll",
    response_model=ClassStudentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Join a class using the enrollment code (Student)",
)
def enroll_by_code(
    payload: ClassEnrollByCode,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
):
    """Students join a class using the unique enrollment code."""
    student_id = payload.student_id if payload.student_id else current_user.id
    if student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot enroll on behalf of another user.",
        )

    enrollment = ClassController.enroll_by_code(
        db,
        enrollment_code=payload.enrollment_code,
        student_id=student_id,
    )
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Class with enrollment code '{payload.enrollment_code}' not found.",
        )
    return enrollment


@router.delete(
    "/{class_uuid}/students/{student_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Unenroll a student from a class",
)
def unenroll_student(
    class_uuid: UUID,
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    class_obj = require_record(
        ClassController.get_by_uuid(db, class_uuid=class_uuid),
        detail=f"Class '{class_uuid}' not found.",
    )
    # Permitted if student unenrolls themselves OR if teacher of this class unenrolls them
    is_self = (current_user.id == student_id)
    is_class_teacher = (current_user.role == UserRole.TEACHER and class_obj.teacher_id == current_user.id)
    if not (is_self or is_class_teacher):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to remove this enrollment.",
        )

    removed = ClassController.unenroll_student(db, class_id=class_obj.id, student_id=student_id)
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student {student_id} is not enrolled in this class.",
        )


@router.get(
    "/{class_uuid}/students",
    response_model=List[UserResponse],
    summary="List all enrolled students in a class (Teacher only)",
)
def get_enrolled_students(
    class_uuid: UUID,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    class_obj = require_record(
        ClassController.get_by_uuid(db, class_uuid=class_uuid),
        detail=f"Class '{class_uuid}' not found.",
    )
    if class_obj.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view students enrolled in your own classes.",
        )
    return ClassController.get_enrolled_students(db, class_id=class_obj.id)
