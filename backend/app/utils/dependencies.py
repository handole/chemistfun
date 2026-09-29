from typing import Callable, Generator
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import decode_access_token
from app.modules.users.controller import UserController
from app.modules.users.models import User, UserRole

# HTTP Bearer scheme for Swagger UI & API header authorization
security_scheme = HTTPBearer(auto_error=True)


def get_db() -> Generator[Session, None, None]:
    """Dependency: Provide a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def require_record(record, detail: str = "Record not found"):
    """Raise 404 if record is None."""
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    return record


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Validate Bearer JWT token and retrieve the current authenticated User."""
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid, expired, or missing authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("user_id")
    if user_id is None:
        # Fallback to sub (UUID)
        sub = payload.get("sub")
        if sub:
            try:
                user = UserController.get_by_uuid(db, user_uuid=UUID(sub))
            except Exception:
                user = None
        else:
            user = None
    else:
        user = UserController.get_by_id(db, user_id=int(user_id))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User associated with this token no longer exists.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def require_role(*allowed_roles: UserRole) -> Callable[..., User]:
    """Factory dependency: Ensure the authenticated user possesses one of the allowed roles."""
    def role_dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            roles_str = ", ".join(r.value for r in allowed_roles)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: this operation requires one of the following roles: [{roles_str}].",
            )
        return current_user

    return role_dependency


# Convenience shortcuts for specific roles
require_teacher = require_role(UserRole.TEACHER)
require_student = require_role(UserRole.STUDENT)
