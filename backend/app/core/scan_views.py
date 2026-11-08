"""Response shapes and helpers for scans that several modules share."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.finding_utils import SEVERITY_ORDER
from app.core.models import Finding, Scan


class FindingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    category: str
    severity: str
    title: str
    key: str
    details: str
    explanation: str
    fix: str


class ScanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    target: str
    resolved_ip: Optional[str]
    profile: str
    ports_spec: Optional[str]
    status: str
    progress_pct: int
    progress_text: Optional[str]
    risk_score: int
    risk_level: str
    error: Optional[str]
    started_at: datetime
    finished_at: Optional[datetime]
    counts: dict[str, int] = {}
    owner_name: Optional[str] = None  # only filled in for admin views


class ScanDetailOut(ScanOut):
    findings: list[FindingOut] = []


class CompareItem(BaseModel):
    category: str
    severity: str
    title: str
    key: str


class CompareOut(BaseModel):
    scan_a: ScanOut
    scan_b: ScanOut
    new: list[CompareItem]
    fixed: list[CompareItem]
    unchanged: list[CompareItem]
    score_change: int


def counts_for(db: Session, scan_ids: list[int]) -> dict[int, dict[str, int]]:
    """How many findings of each severity every scan has."""
    out = {i: {s: 0 for s in SEVERITY_ORDER} for i in scan_ids}
    if scan_ids:
        rows = (
            db.query(Finding.scan_id, Finding.severity, func.count(Finding.id))
            .filter(Finding.scan_id.in_(scan_ids))
            .group_by(Finding.scan_id, Finding.severity)
            .all()
        )
        for sid, sev, n in rows:
            out[sid][sev] = n
    return out


def scan_out(scan: Scan, counts: dict, owner: bool = False) -> ScanOut:
    data = ScanOut.model_validate(scan)
    data.counts = counts
    if owner:
        data.owner_name = scan.owner.username
    return data
