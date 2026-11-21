"""Start a scan and list the scan profiles. (Member 1)

The permission check and the scan limit come from Module 1 (users/scan_permission.py, Member 2).
"""
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.models import Scan, User
from app.core.scan_views import ScanOut, counts_for, scan_out
from app.modules.scanning.checks.ports import parse_ports
from app.modules.scanning.profiles import PROFILES
from app.modules.scanning.runner import run_scan
from app.modules.scanning.schemas import ScanCreate
from app.modules.users.scan_permission import check_scan_limit, check_scan_permission
from app.modules.users.security import get_current_user

router = APIRouter(prefix="/api", tags=["scanning"])


@router.get("/profiles")
def list_profiles():
    return [
        {"id": k, "label": v["label"], "description": v["description"], "steps": v["steps"]}
        for k, v in PROFILES.items()
    ]


@router.post("/scans", response_model=ScanOut, status_code=201)
def create_scan(
    data: ScanCreate,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Module 1: permission box ticked + target allowed
    target = check_scan_permission(data.authorized, data.target)

    ports_spec = None
    if data.ports and data.ports.strip():
        if data.profile == "web-only":
            raise HTTPException(400, "The web-only profile does not scan ports.")
        try:
            ports_spec = data.ports.strip()
            parse_ports(ports_spec, settings.MAX_CUSTOM_PORTS)
        except ValueError as e:
            raise HTTPException(400, str(e))

    running = (
        db.query(Scan)
        .filter(Scan.user_id == user.id, Scan.status.in_(["queued", "running"]))
        .count()
    )
    check_scan_limit(running)  # Module 1: at most 2 scans at a time

    scan = Scan(
        user_id=user.id, target=target["host"], resolved_ip=target["ip"],
        profile=data.profile, ports_spec=ports_spec, authorized=True, status="queued",
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)
    background.add_task(run_scan, scan.id)
    return scan_out(scan, counts_for(db, [scan.id])[scan.id])
