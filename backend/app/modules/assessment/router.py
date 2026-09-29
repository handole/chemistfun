from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.modules.assessment.controller import AssessmentController
from app.modules.assessment.schemas import (
    EvaluationMetricCreate,
    EvaluationMetricResponse,
    EvaluationMetricUpdate,
    QuestionCreate,
    QuestionResponse,
    QuestionStudentView,
    QuestionUpdate,
    QuizCreate,
    QuizResponse,
    QuizUpdate,
    StudentAnswerResponse,
    StudentAnswerSave,
    StudentQuizAttemptCreate,
    StudentQuizAttemptResponse,
)
from app.modules.users.models import User, UserRole
from app.utils.dependencies import (
    get_current_user,
    get_db,
    require_record,
    require_student,
    require_teacher,
)

router = APIRouter(prefix="/assessment", tags=["Assessment"])


# =========================================================================
# Evaluation Metrics
# =========================================================================

@router.get(
    "/metrics",
    response_model=List[EvaluationMetricResponse],
    summary="List evaluation metrics by module ID (Authenticated)",
)
def list_metrics(
    module_id: int = Query(..., description="Filter by module ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return AssessmentController.get_metrics_by_module(db, module_id=module_id)


@router.post(
    "/metrics",
    response_model=EvaluationMetricResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new evaluation metric (Teacher only)",
)
def create_metric(
    payload: EvaluationMetricCreate,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    return AssessmentController.create_metric(db, obj_in=payload)


@router.get(
    "/metrics/{metric_uuid}",
    response_model=EvaluationMetricResponse,
    summary="Get evaluation metric by UUID (Authenticated)",
)
def get_metric(
    metric_uuid: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return require_record(
        AssessmentController.get_metric_by_uuid(db, metric_uuid=metric_uuid),
        detail=f"Evaluation metric '{metric_uuid}' not found.",
    )


@router.patch(
    "/metrics/{metric_uuid}",
    response_model=EvaluationMetricResponse,
    summary="Update evaluation metric by UUID (Teacher only)",
)
def update_metric(
    metric_uuid: UUID,
    payload: EvaluationMetricUpdate,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    metric = require_record(
        AssessmentController.get_metric_by_uuid(db, metric_uuid=metric_uuid),
        detail=f"Evaluation metric '{metric_uuid}' not found.",
    )
    return AssessmentController.update_metric(db, db_obj=metric, obj_in=payload)


@router.delete(
    "/metrics/{metric_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete evaluation metric by UUID (Teacher only)",
)
def delete_metric(
    metric_uuid: UUID,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    metric = require_record(
        AssessmentController.get_metric_by_uuid(db, metric_uuid=metric_uuid),
        detail=f"Evaluation metric '{metric_uuid}' not found.",
    )
    AssessmentController.delete_metric(db, metric_id=metric.id)


# =========================================================================
# Quizzes
# =========================================================================

@router.post(
    "/quizzes",
    response_model=QuizResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new quiz for a module (Teacher only)",
)
def create_quiz(
    payload: QuizCreate,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    existing = AssessmentController.get_quiz_by_module(db, module_id=payload.module_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Module {payload.module_id} already has a quiz. Use PATCH to update it.",
        )
    return AssessmentController.create_quiz(db, obj_in=payload)


@router.get(
    "/quizzes/{quiz_uuid}",
    response_model=QuizResponse,
    summary="Get quiz by UUID (Authenticated)",
)
def get_quiz(
    quiz_uuid: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return require_record(
        AssessmentController.get_quiz_by_uuid(db, quiz_uuid=quiz_uuid),
        detail=f"Quiz '{quiz_uuid}' not found.",
    )


@router.patch(
    "/quizzes/{quiz_uuid}",
    response_model=QuizResponse,
    summary="Update quiz by UUID (Teacher only)",
)
def update_quiz(
    quiz_uuid: UUID,
    payload: QuizUpdate,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    quiz = require_record(
        AssessmentController.get_quiz_by_uuid(db, quiz_uuid=quiz_uuid),
        detail=f"Quiz '{quiz_uuid}' not found.",
    )
    return AssessmentController.update_quiz(db, db_obj=quiz, obj_in=payload)


@router.delete(
    "/quizzes/{quiz_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete quiz by UUID (Teacher only)",
)
def delete_quiz(
    quiz_uuid: UUID,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    quiz = require_record(
        AssessmentController.get_quiz_by_uuid(db, quiz_uuid=quiz_uuid),
        detail=f"Quiz '{quiz_uuid}' not found.",
    )
    AssessmentController.delete_quiz(db, quiz_id=quiz.id)


# =========================================================================
# Questions
# =========================================================================

@router.get(
    "/quizzes/{quiz_uuid}/questions",
    response_model=List[QuestionResponse],
    summary="List questions with correct answers (Teacher only)",
)
def list_questions(
    quiz_uuid: UUID,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    quiz = require_record(
        AssessmentController.get_quiz_by_uuid(db, quiz_uuid=quiz_uuid),
        detail=f"Quiz '{quiz_uuid}' not found.",
    )
    return AssessmentController.get_questions_by_quiz(db, quiz_id=quiz.id)


@router.get(
    "/quizzes/{quiz_uuid}/questions/student-view",
    response_model=List[QuestionStudentView],
    summary="List questions without correct answers (Student quiz view)",
)
def list_questions_student_view(
    quiz_uuid: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    quiz = require_record(
        AssessmentController.get_quiz_by_uuid(db, quiz_uuid=quiz_uuid),
        detail=f"Quiz '{quiz_uuid}' not found.",
    )
    if not quiz.is_active and current_user.role == UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This quiz is currently inactive.",
        )
    return AssessmentController.get_questions_by_quiz(db, quiz_id=quiz.id)


@router.post(
    "/questions",
    response_model=QuestionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new question (Teacher only)",
)
def create_question(
    payload: QuestionCreate,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    return AssessmentController.create_question(db, obj_in=payload)


@router.get(
    "/questions/{question_uuid}",
    response_model=QuestionResponse,
    summary="Get question with answer by UUID (Teacher only)",
)
def get_question(
    question_uuid: UUID,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    return require_record(
        AssessmentController.get_question_by_uuid(db, question_uuid=question_uuid),
        detail=f"Question '{question_uuid}' not found.",
    )


@router.patch(
    "/questions/{question_uuid}",
    response_model=QuestionResponse,
    summary="Update question by UUID (Teacher only)",
)
def update_question(
    question_uuid: UUID,
    payload: QuestionUpdate,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    question = require_record(
        AssessmentController.get_question_by_uuid(db, question_uuid=question_uuid),
        detail=f"Question '{question_uuid}' not found.",
    )
    return AssessmentController.update_question(db, db_obj=question, obj_in=payload)


@router.delete(
    "/questions/{question_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete question by UUID (Teacher only)",
)
def delete_question(
    question_uuid: UUID,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    question = require_record(
        AssessmentController.get_question_by_uuid(db, question_uuid=question_uuid),
        detail=f"Question '{question_uuid}' not found.",
    )
    AssessmentController.delete_question(db, question_id=question.id)


# =========================================================================
# Student Quiz Attempts
# =========================================================================

@router.post(
    "/attempts/start",
    response_model=StudentQuizAttemptResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start a new quiz attempt (Student)",
)
def start_attempt(
    payload: StudentQuizAttemptCreate,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
):
    student_id = payload.student_id if payload.student_id else current_user.id
    if student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot start quiz attempts on behalf of another student.",
        )

    # Verify quiz is active
    quiz = AssessmentController.get_quiz_by_id(db, quiz_id=payload.quiz_id)
    if not quiz or not quiz.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quiz does not exist or is currently inactive.",
        )

    return AssessmentController.start_attempt(
        db, student_id=student_id, quiz_id=payload.quiz_id
    )


@router.get(
    "/attempts/{attempt_uuid}",
    response_model=StudentQuizAttemptResponse,
    summary="Get quiz attempt by UUID (Student owner or Teacher)",
)
def get_attempt(
    attempt_uuid: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    attempt = require_record(
        AssessmentController.get_attempt_by_uuid(db, attempt_uuid=attempt_uuid),
        detail=f"Attempt '{attempt_uuid}' not found.",
    )
    # Students can only inspect their own attempts
    if current_user.role == UserRole.STUDENT and attempt.student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own quiz attempts.",
        )
    return attempt


@router.get(
    "/attempts",
    response_model=List[StudentQuizAttemptResponse],
    summary="List quiz attempts (Students see only their own)",
)
def list_attempts(
    student_id: Optional[int] = Query(default=None, description="Student user ID filter"),
    quiz_id: Optional[int] = Query(default=None, description="Optional quiz ID filter"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role == UserRole.STUDENT:
        # Enforce student seeing only their own attempts
        effective_student_id = current_user.id
    else:
        # Teachers can filter by student_id or see all
        effective_student_id = student_id if student_id else current_user.id

    return AssessmentController.get_student_attempts(
        db, student_id=effective_student_id, quiz_id=quiz_id
    )


@router.post(
    "/attempts/{attempt_uuid}/submit",
    response_model=StudentQuizAttemptResponse,
    summary="Submit quiz attempt and compute Radar Chart data (Student owner)",
)
def submit_attempt(
    attempt_uuid: UUID,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
):
    attempt = require_record(
        AssessmentController.get_attempt_by_uuid(db, attempt_uuid=attempt_uuid),
        detail=f"Attempt '{attempt_uuid}' not found.",
    )
    if attempt.student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only submit your own quiz attempts.",
        )
    if attempt.completed_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This attempt has already been finalized and submitted.",
        )
    return AssessmentController.submit_attempt(db, attempt_id=attempt.id)


# =========================================================================
# Student Answers (auto-save)
# =========================================================================

@router.post(
    "/answers",
    response_model=StudentAnswerResponse,
    status_code=status.HTTP_200_OK,
    summary="Auto-save answer during an ongoing attempt (Student owner)",
)
def save_answer(
    payload: StudentAnswerSave,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
):
    attempt = AssessmentController.get_attempt_by_id(db, attempt_id=payload.attempt_id)
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quiz attempt {payload.attempt_id} not found.",
        )
    if attempt.student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot record answers for another student's attempt.",
        )
    if attempt.completed_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot record answers on a submitted attempt.",
        )

    return AssessmentController.save_student_answer(
        db,
        attempt_id=payload.attempt_id,
        question_id=payload.question_id,
        selected_answer=payload.selected_answer,
    )


@router.get(
    "/attempts/{attempt_uuid}/answers",
    response_model=List[StudentAnswerResponse],
    summary="List saved answers for an attempt (Student owner or Teacher)",
)
def list_attempt_answers(
    attempt_uuid: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    attempt = require_record(
        AssessmentController.get_attempt_by_uuid(db, attempt_uuid=attempt_uuid),
        detail=f"Attempt '{attempt_uuid}' not found.",
    )
    if current_user.role == UserRole.STUDENT and attempt.student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view answers for your own quiz attempts.",
        )
    return AssessmentController.get_attempt_answers(db, attempt_id=attempt.id)
