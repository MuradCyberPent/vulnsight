"""Admin-only views: all users and all scans. (Member 3)"""
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.modules.users.admin_access import require_admin
from app.core.database import get_db
from app.core.models import Scan, User
from app.core.scan_views import ScanOut, counts_for, scan_out

router = APIRouter(prefix="/api/admin", tags=["admin"], dependencies=[Depends(require_admin)])


@router.get("/users")
def users(db: Session = Depends(get_db)):
    rows = (
        db.query(User, func.count(Scan.id))
        .outerjoin(Scan, Scan.user_id == User.id)
        .group_by(User.id)
        .order_by(User.id)
        .all()
    )
    return [
        {"id": u.id, "username": u.username, "email": u.email, "role": u.role,
         "created_at": u.created_at, "scan_count": n}
        for u, n in rows
    ]


@router.get("/scans", response_model=list[ScanOut])
def all_scans(db: Session = Depends(get_db)):
    scans = db.query(Scan).order_by(Scan.id.desc()).limit(300).all()
    counts = counts_for(db, [s.id for s in scans])
    return [scan_out(s, counts[s.id], owner=True) for s in scans]
