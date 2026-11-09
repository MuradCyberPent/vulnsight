"""Private workspace: a user can only ever reach their own scans. (Member 3)"""
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.models import Scan, User


def own_scan(db: Session, scan_id: int, user: User) -> Scan:
    scan = db.get(Scan, scan_id)
    # Same 404 whether it doesn't exist or belongs to someone else (no information leak).
    if not scan or scan.user_id != user.id:
        raise HTTPException(404, "Scan not found.")
    return scan
