"""Role-based access control: only admins may pass. (Member 3)"""
from fastapi import Depends, HTTPException, status

from app.core.models import User
from app.modules.users.security import get_current_user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admins only.")
    return user
