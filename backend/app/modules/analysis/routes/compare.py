"""Compare two scans: what is new, fixed, or still open. (Member 3)"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.finding_utils import SEVERITY_ORDER
from app.core.models import User
from app.core.scan_views import CompareItem, CompareOut, counts_for, scan_out
from app.modules.users.security import get_current_user
from app.modules.users.workspace import own_scan

router = APIRouter(prefix="/api", tags=["analysis"])


@router.get("/scans/compare", response_model=CompareOut)
def compare(a: int, b: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Compare an older scan (a) with a newer one (b)."""
    scan_a, scan_b = own_scan(db, a, user), own_scan(db, b, user)
    counts = counts_for(db, [a, b])

    def index(scan):
        return {(f.category, f.key): f for f in scan.findings if f.severity != "Info"}

    ia, ib = index(scan_a), index(scan_b)

    def item(f):
        return CompareItem(category=f.category, severity=f.severity, title=f.title, key=f.key)

    order = lambda items: sorted(items, key=lambda i: SEVERITY_ORDER.index(i.severity))
    return CompareOut(
        scan_a=scan_out(scan_a, counts[a]),
        scan_b=scan_out(scan_b, counts[b]),
        new=order(item(ib[k]) for k in ib if k not in ia),
        fixed=order(item(ia[k]) for k in ia if k not in ib),
        unchanged=order(item(ib[k]) for k in ib if k in ia),
        score_change=scan_b.risk_score - scan_a.risk_score,
    )
