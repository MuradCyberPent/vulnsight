"""Download a finished scan as an HTML, JSON or TXT report. (Member 1)"""
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.models import User
from app.modules.analysis import reports
from app.modules.users.security import get_current_user
from app.modules.users.workspace import own_scan

router = APIRouter(prefix="/api", tags=["analysis"])


@router.get("/scans/{scan_id:int}/report")
def download_report(
    scan_id: int, format: str = "html",
    db: Session = Depends(get_db), user: User = Depends(get_current_user),
):
    scan = own_scan(db, scan_id, user)
    if scan.status not in ("completed", "failed"):
        raise HTTPException(409, "The scan is still running.")
    builders = {
        "html": (reports.build_html, "text/html"),
        "json": (reports.build_json, "application/json"),
        "txt": (reports.build_txt, "text/plain"),
    }
    if format not in builders:
        raise HTTPException(400, "Format must be html, json or txt.")
    build, mime = builders[format]
    return Response(
        build(scan), media_type=f"{mime}; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{reports.safe_filename(scan, format)}"'},
    )
