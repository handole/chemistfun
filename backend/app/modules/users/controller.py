from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.modules.users.models import User, UserRole
from app.modules.users.schemas import UserCreate, UserUpdate


class UserController:
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        return db.scalar(select(User).where(User.id == user_id))

    @staticmethod
    def get_by_uuid(db: Session, user_uuid: UUID) -> Optional[User]:
        return db.scalar(select(User).where(User.uuid == user_uuid))

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        return db.scalar(select(User).where(User.email == email))

    @staticmethod
    def get_multi(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        role: Optional[UserRole] = None,
    ) -> List[User]:
        query = select(User)
        if role:
            query = query.where(User.role == role)
        query = query.offset(skip).limit(limit)
        return list(db.scalars(query).all())

    @staticmethod
    def create(db: Session, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            password_hash=hash_password(obj_in.password),
            full_name=obj_in.full_name,
            role=obj_in.role,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def update(
        db: Session,
        db_obj: User,
        obj_in: Union[UserUpdate, Dict[str, Any]],
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        if "password" in update_data and update_data["password"]:
            password = update_data.pop("password")
            db_obj.password_hash = hash_password(password)

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, user_id: int) -> Optional[User]:
        user = UserController.get_by_id(db, user_id=user_id)
        if user:
            db.delete(user)
            db.commit()
        return user

    @staticmethod
    def authenticate(db: Session, email: str, password: str) -> Optional[User]:
        user = UserController.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user


user_controller = UserController()

__all__ = ["UserController", "user_controller"]

