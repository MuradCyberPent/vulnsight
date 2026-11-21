"""Runs the checks for one scan in the background and saves the results. (Member 1)

Checks come from core/checks.py (each check file registers itself).
When everything is done, the functions in core/hooks.post_scan run (Module 3 uses this for risk scoring).
"""
import ipaddress
import traceback

from app.core import checks as registry
from app.core import hooks
from app.core.database import SessionLocal, utcnow
from app.core.models import Finding, Scan
from app.modules.scanning.profiles import PROFILES


def run_scan(scan_id: int) -> None:
    db = SessionLocal()
    try:
        scan = db.get(Scan, scan_id)
        profile = PROFILES[scan.profile]
        steps = [s for s in registry.ordered_checks() if s in profile["steps"]]
        scan.status = "running"
        db.commit()

        ctx = {
            "host": scan.target,
            "ip": scan.resolved_ip,
            "is_ip": _is_ip(scan.target),
            "ports_spec": scan.ports_spec or profile["ports"],
            "banners": [],
            "open_ports": [],
        }
        all_findings: list[dict] = []
        seen = set()

        for i, name in enumerate(steps):
            label, func = registry.CHECKS[name]["label"], registry.CHECKS[name]["run"]
            scan.progress_text = f"Running: {label}"
            scan.progress_pct = int(i / len(steps) * 100)
            db.commit()
            try:
                new = func(ctx)
            except Exception as e:  # one broken check must not stop the whole scan
                new = [{
                    "category": "Scanner", "severity": "Info", "title": f"{label} could not finish",
                    "key": f"error:{name}", "details": f"{type(e).__name__}: {e}",
                    "explanation": "This check hit an error (a timeout or a blocked connection, for example). The rest of the scan continued.",
                    "fix": "Run the scan again. If it keeps failing, the target may be blocking scanners.",
                }]
            for f in new:
                ident = (f["category"], f["key"])
                if ident in seen:
                    continue
                seen.add(ident)
                all_findings.append(f)
                db.add(Finding(scan_id=scan.id, **f))
            db.commit()

        for hook in hooks.post_scan:  # e.g. calculate the risk score
            hook(scan, all_findings)
        scan.progress_pct, scan.progress_text = 100, "Finished"
        scan.status = "completed"
        scan.finished_at = utcnow()
        db.commit()
    except Exception as e:
        db.rollback()
        traceback.print_exc()
        scan = db.get(Scan, scan_id)
        if scan:
            scan.status, scan.error = "failed", f"{type(e).__name__}: {e}"
            scan.finished_at = utcnow()
            db.commit()
    finally:
        db.close()


def _is_ip(value: str) -> bool:
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False
