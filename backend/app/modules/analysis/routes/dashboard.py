"""Dashboard numbers: totals, open issues by severity, riskiest targets, recent scans. (Member 1)"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.finding_utils import SEVERITY_ORDER
from app.core.models import Scan, User
from app.core.scan_views import counts_for, scan_out
from app.modules.users.security import get_current_user

router = APIRouter(prefix="/api", tags=["analysis"])


@router.get("/stats")
def stats(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    scans = db.query(Scan).filter(Scan.user_id == user.id).order_by(Scan.id.desc()).all()
    done = [s for s in scans if s.status == "completed"]
    latest: dict[str, Scan] = {}
    for s in done:  # newest first, so first one we meet per target is the latest
        latest.setdefault(s.target, s)
    counts = counts_for(db, [s.id for s in latest.values()])
    totals = {sev: sum(counts[s.id][sev] for s in latest.values()) for sev in SEVERITY_ORDER}
    return {
        "total_scans": len(scans),
        "targets": len(latest),
        "average_risk": round(sum(s.risk_score for s in latest.values()) / len(latest)) if latest else 0,
        "open_findings": totals,
        "latest_by_target": [
            {"scan_id": s.id, "target": s.target, "risk_score": s.risk_score, "risk_level": s.risk_level}
            for s in sorted(latest.values(), key=lambda x: -x.risk_score)[:6]
        ],
        "recent": [scan_out(s, counts_for(db, [s.id])[s.id]) for s in scans[:5]],
    }
