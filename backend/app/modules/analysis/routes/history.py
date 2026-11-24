"""Scan history: list my scans, delete a scan. (Member 3)"""
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.models import Scan, User
from app.core.scan_views import ScanOut, counts_for, scan_out
from app.modules.users.security import get_current_user
from app.modules.users.workspace import own_scan

router = APIRouter(prefix="/api", tags=["analysis"])


@router.get("/scans", response_model=list[ScanOut])
def history(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    scans = db.query(Scan).filter(Scan.user_id == user.id).order_by(Scan.id.desc()).limit(200).all()
    counts = counts_for(db, [s.id for s in scans])
    return [scan_out(s, counts[s.id]) for s in scans]


@router.delete("/scans/{scan_id:int}", status_code=204)
def delete_scan(scan_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    scan = own_scan(db, scan_id, user)
    db.delete(scan)
    db.commit()
    return Response(status_code=204)
