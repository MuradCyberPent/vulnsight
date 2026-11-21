"""Read one scan: its live progress and its findings so far. (Member 1: Live Scan Progress)

The scan page asks for this every 1.5 seconds while a scan is running.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.finding_utils import SEVERITY_ORDER
from app.core.models import User
from app.core.scan_views import FindingOut, ScanDetailOut, counts_for, scan_out
from app.modules.users.security import get_current_user
from app.modules.users.workspace import own_scan

router = APIRouter(prefix="/api", tags=["scanning"])


@router.get("/scans/{scan_id:int}", response_model=ScanDetailOut)
def get_scan(scan_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    scan = own_scan(db, scan_id, user)
    base = scan_out(scan, counts_for(db, [scan.id])[scan.id])
    findings = sorted(scan.findings, key=lambda f: (SEVERITY_ORDER.index(f.severity), f.category, f.title))
    return ScanDetailOut(**base.model_dump(), findings=[FindingOut.model_validate(f) for f in findings])
