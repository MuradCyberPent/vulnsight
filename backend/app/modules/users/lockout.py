"""Account lockout after too many wrong passwords. (Member 2)

Plugs into the login route through core/hooks.py, so Member 1's login code does not need to change.
"""
from datetime import timedelta

from fastapi import HTTPException, status

from app.core import hooks
from app.core.config import settings
from app.core.database import utcnow


def reject_if_locked(user) -> None:
    if user and user.locked_until and user.locked_until > utcnow():
        minutes = int((user.locked_until - utcnow()).total_seconds() // 60) + 1
        raise HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS,
            f"Too many failed attempts. Try again in about {minutes} minute(s).",
        )


def count_failure(db, user) -> None:
    user.failed_attempts += 1
    if user.failed_attempts >= settings.MAX_LOGIN_ATTEMPTS:
        user.locked_until = utcnow() + timedelta(minutes=settings.LOCKOUT_MINUTES)
        user.failed_attempts = 0
    db.commit()


def clear_failures(db, user) -> None:
    user.failed_attempts = 0
    user.locked_until = None
    db.commit()


hooks.login_before.append(reject_if_locked)
hooks.login_failed.append(count_failure)
hooks.login_success.append(clear_failures)
