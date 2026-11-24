"""Risk scoring: Low / Medium / High / Critical. (Member 2)"""
WEIGHTS = {"Critical": 40, "High": 18, "Medium": 6, "Low": 2, "Info": 0}


def compute_risk(findings: list[dict]) -> tuple[int, str]:
    score = min(100, sum(WEIGHTS[f["severity"]] for f in findings))
    if score >= 70:
        level = "Critical"
    elif score >= 40:
        level = "High"
    elif score >= 15:
        level = "Medium"
    else:
        level = "Low"
    # One really bad finding should never hide behind a low total.
    severities = {f["severity"] for f in findings}
    if "Critical" in severities and level in ("Low", "Medium"):
        level = "High"
    elif "High" in severities and level == "Low":
        level = "Medium"
    return score, level


# Plug into the scan runner: when a scan finishes, store its score and level.
from app.core import hooks  # noqa: E402


def apply_risk(scan, findings: list[dict]) -> None:
    scan.risk_score, scan.risk_level = compute_risk(findings)


hooks.post_scan.append(apply_risk)
