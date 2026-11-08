"""Shared helpers used by every scanner."""

SEVERITY_ORDER = ["Critical", "High", "Medium", "Low", "Info"]


def finding(category, severity, title, key, details="", explanation="", fix=""):
    """Every scanner returns a list of these small dictionaries."""
    assert severity in SEVERITY_ORDER, severity
    return {
        "category": category,
        "severity": severity,
        "title": title,
        "key": key,  # stable id: lets us compare two scans later
        "details": details,
        "explanation": explanation,
        "fix": fix,
    }


def netloc(host: str) -> str:
    """IPv6 addresses need [brackets] inside URLs."""
    return f"[{host}]" if ":" in host else host


USER_AGENT = {"User-Agent": "VulnSight/1.0 (authorized security assessment)"}
