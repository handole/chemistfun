from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.assessment.models import (
    EvaluationMetric,
    Question,
    Quiz,
    StudentAnswer,
    StudentQuizAttempt,
)
from app.modules.assessment.schemas import (
    EvaluationMetricCreate,
    EvaluationMetricUpdate,
    QuestionCreate,
    QuestionUpdate,
    QuizCreate,
    QuizUpdate,
)


class AssessmentController:
    # =========================================================================
    # EvaluationMetric Operations
    # =========================================================================

    @staticmethod
    async def get_metric_by_id(db: AsyncSession, metric_id: int) -> Optional[EvaluationMetric]:
        result = await db.execute(select(EvaluationMetric).where(EvaluationMetric.id == metric_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_metric_by_uuid(db: AsyncSession, metric_uuid: UUID) -> Optional[EvaluationMetric]:
        result = await db.execute(select(EvaluationMetric).where(EvaluationMetric.uuid == metric_uuid))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_metrics_by_module(db: AsyncSession, module_id: int) -> List[EvaluationMetric]:
        query = select(EvaluationMetric).where(EvaluationMetric.module_id == module_id).order_by(EvaluationMetric.id.asc())
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def create_metric(db: AsyncSession, obj_in: EvaluationMetricCreate) -> EvaluationMetric:
        db_obj = EvaluationMetric(
            module_id=obj_in.module_id,
            metric_name=obj_in.metric_name,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def update_metric(
        db: AsyncSession,
        db_obj: EvaluationMetric,
        obj_in: Union[EvaluationMetricUpdate, Dict[str, Any]],
    ) -> EvaluationMetric:
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
    async def delete_metric(db: AsyncSession, metric_id: int) -> Optional[EvaluationMetric]:
        metric_obj = await AssessmentController.get_metric_by_id(db, metric_id=metric_id)
        if metric_obj:
            await db.delete(metric_obj)
            await db.commit()
        return metric_obj

    # =========================================================================
    # Quiz Operations
    # =========================================================================

    @staticmethod
    async def get_quiz_by_id(db: AsyncSession, quiz_id: int) -> Optional[Quiz]:
        result = await db.execute(select(Quiz).where(Quiz.id == quiz_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_quiz_by_uuid(db: AsyncSession, quiz_uuid: UUID) -> Optional[Quiz]:
        result = await db.execute(select(Quiz).where(Quiz.uuid == quiz_uuid))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_quiz_by_module(db: AsyncSession, module_id: int) -> Optional[Quiz]:
        result = await db.execute(select(Quiz).where(Quiz.module_id == module_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_quiz(db: AsyncSession, obj_in: QuizCreate) -> Quiz:
        db_obj = Quiz(
            module_id=obj_in.module_id,
            title=obj_in.title,
            time_limit_minutes=obj_in.time_limit_minutes,
            is_active=obj_in.is_active,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def update_quiz(
        db: AsyncSession,
        db_obj: Quiz,
        obj_in: Union[QuizUpdate, Dict[str, Any]],
    ) -> Quiz:
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
    async def delete_quiz(db: AsyncSession, quiz_id: int) -> Optional[Quiz]:
        quiz_obj = await AssessmentController.get_quiz_by_id(db, quiz_id=quiz_id)
        if quiz_obj:
            await db.delete(quiz_obj)
            await db.commit()
        return quiz_obj

    # =========================================================================
    # Question Operations
    # =========================================================================

    @staticmethod
    async def get_question_by_id(db: AsyncSession, question_id: int) -> Optional[Question]:
        result = await db.execute(select(Question).where(Question.id == question_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_question_by_uuid(db: AsyncSession, question_uuid: UUID) -> Optional[Question]:
        result = await db.execute(select(Question).where(Question.uuid == question_uuid))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_questions_by_quiz(db: AsyncSession, quiz_id: int) -> List[Question]:
        query = select(Question).where(Question.quiz_id == quiz_id).order_by(Question.id.asc())
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def create_question(db: AsyncSession, obj_in: QuestionCreate) -> Question:
        db_obj = Question(
            quiz_id=obj_in.quiz_id,
            metric_id=obj_in.metric_id,
            question_text=obj_in.question_text,
            question_type=obj_in.question_type,
            options=obj_in.options,
            correct_answer=obj_in.correct_answer.strip().upper(),
            weight_score=obj_in.weight_score,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def update_question(
        db: AsyncSession,
        db_obj: Question,
        obj_in: Union[QuestionUpdate, Dict[str, Any]],
    ) -> Question:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        if "correct_answer" in update_data and update_data["correct_answer"]:
            update_data["correct_answer"] = update_data["correct_answer"].strip().upper()

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def delete_question(db: AsyncSession, question_id: int) -> Optional[Question]:
        question_obj = await AssessmentController.get_question_by_id(db, question_id=question_id)
        if question_obj:
            await db.delete(question_obj)
            await db.commit()
        return question_obj

    # =========================================================================
    # Student Quiz Attempt & Answers (Transaction & Analytics)
    # =========================================================================

    @staticmethod
    async def start_attempt(db: AsyncSession, student_id: int, quiz_id: int) -> StudentQuizAttempt:
        attempt = StudentQuizAttempt(
            student_id=student_id,
            quiz_id=quiz_id,
            started_at=datetime.now(timezone.utc),
        )
        db.add(attempt)
        await db.commit()
        await db.refresh(attempt)
        return attempt

    @staticmethod
    async def get_attempt_by_id(db: AsyncSession, attempt_id: int) -> Optional[StudentQuizAttempt]:
        result = await db.execute(select(StudentQuizAttempt).where(StudentQuizAttempt.id == attempt_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_attempt_by_uuid(db: AsyncSession, attempt_uuid: UUID) -> Optional[StudentQuizAttempt]:
        result = await db.execute(select(StudentQuizAttempt).where(StudentQuizAttempt.uuid == attempt_uuid))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_student_attempts(
        db: AsyncSession,
        student_id: int,
        quiz_id: Optional[int] = None,
    ) -> List[StudentQuizAttempt]:
        query = select(StudentQuizAttempt).where(StudentQuizAttempt.student_id == student_id)
        if quiz_id is not None:
            query = query.where(StudentQuizAttempt.quiz_id == quiz_id)
        query = query.order_by(StudentQuizAttempt.started_at.desc())
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_all_attempts(
        db: AsyncSession,
        quiz_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[StudentQuizAttempt]:
        query = select(StudentQuizAttempt)
        if quiz_id is not None:
            query = query.where(StudentQuizAttempt.quiz_id == quiz_id)
        query = query.order_by(StudentQuizAttempt.started_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def save_student_answer(
        db: AsyncSession,
        attempt_id: int,
        question_id: int,
        selected_answer: str,
    ) -> StudentAnswer:
        """Auto-save an answer for a question in an ongoing attempt."""
        selected_normalized = selected_answer.strip().upper()

        # Check correctness against question
        question = await AssessmentController.get_question_by_id(db, question_id=question_id)
        is_correct = False
        if question:
            is_correct = (selected_normalized == question.correct_answer.strip().upper())

        # Check if answer already recorded for this question in attempt
        result = await db.execute(
            select(StudentAnswer).where(
                StudentAnswer.attempt_id == attempt_id,
                StudentAnswer.question_id == question_id,
            )
        )
        existing_answer = result.scalar_one_or_none()
        if existing_answer:
            existing_answer.selected_answer = selected_normalized
            existing_answer.is_correct = is_correct
            db.add(existing_answer)
            await db.commit()
            await db.refresh(existing_answer)
            return existing_answer

        new_answer = StudentAnswer(
            attempt_id=attempt_id,
            question_id=question_id,
            selected_answer=selected_normalized,
            is_correct=is_correct,
        )
        db.add(new_answer)
        await db.commit()
        await db.refresh(new_answer)
        return new_answer

    @staticmethod
    async def get_attempt_answers(db: AsyncSession, attempt_id: int) -> List[StudentAnswer]:
        query = select(StudentAnswer).where(StudentAnswer.attempt_id == attempt_id)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def submit_attempt(db: AsyncSession, attempt_id: int) -> Optional[StudentQuizAttempt]:
        """
        Finalize quiz attempt:
        - Evaluates all answers.
        - Calculates total weighted score.
        - Aggregates score per evaluation_metric for the Radar Chart.
        """
        attempt = await AssessmentController.get_attempt_by_id(db, attempt_id=attempt_id)
        if not attempt:
            return None

        # Fetch all questions for this quiz
        questions = await AssessmentController.get_questions_by_quiz(db, quiz_id=attempt.quiz_id)
        # Fetch all recorded answers for this attempt
        answers = await AssessmentController.get_attempt_answers(db, attempt_id=attempt_id)
        answer_map = {ans.question_id: ans for ans in answers}

        # Track metrics for radar chart: metric_id -> stats
        metric_stats: Dict[Optional[int], Dict[str, Any]] = {}
        total_earned_score = 0
        total_max_score = 0
        correct_count = 0

        for q in questions:
            total_max_score += q.weight_score

            m_id = q.metric_id
            if m_id not in metric_stats:
                metric_stats[m_id] = {
                    "total_weight": 0,
                    "earned_weight": 0,
                    "total_questions": 0,
                    "correct_count": 0,
                }
            metric_stats[m_id]["total_weight"] += q.weight_score
            metric_stats[m_id]["total_questions"] += 1

            ans = answer_map.get(q.id)
            if ans and ans.is_correct:
                total_earned_score += q.weight_score
                correct_count += 1
                metric_stats[m_id]["earned_weight"] += q.weight_score
                metric_stats[m_id]["correct_count"] += 1

        # Calculate final percentage total score
        if total_max_score > 0:
            final_score = round((total_earned_score / total_max_score) * 100, 2)
        else:
            final_score = 0.0

        # Build Radar Chart data grouped per metric
        radar_metrics = []
        for m_id, stats in metric_stats.items():
            if m_id is not None:
                metric_obj = await AssessmentController.get_metric_by_id(db, metric_id=m_id)
                metric_name = metric_obj.metric_name if metric_obj else f"Metrik #{m_id}"
            else:
                metric_name = "Umum / Tanpa Metrik"

            earned_w = stats["earned_weight"]
            total_w = stats["total_weight"]
            pct = round((earned_w / total_w) * 100, 2) if total_w > 0 else 0.0

            radar_metrics.append({
                "metric_id": m_id,
                "metric_name": metric_name,
                "score_percentage": pct,
                "earned_weight": earned_w,
                "total_weight": total_w,
                "correct_count": stats["correct_count"],
                "total_questions": stats["total_questions"],
            })

        radar_data = {
            "metrics": radar_metrics,
            "summary": {
                "total_questions": len(questions),
                "answered_questions": len(answers),
                "correct_answers": correct_count,
                "final_score": final_score,
            },
        }

        # Update attempt
        attempt.completed_at = datetime.now(timezone.utc)
        attempt.total_score = Decimal(str(final_score))
        attempt.radar_chart_data = radar_data

        db.add(attempt)
        await db.commit()
        await db.refresh(attempt)
        return attempt


assessment_controller = AssessmentController()

__all__ = ["AssessmentController", "assessment_controller"]
