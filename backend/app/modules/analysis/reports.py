"""Feature: report export (HTML, JSON, TXT)."""
import json
import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.finding_utils import SEVERITY_ORDER

_env = Environment(
    loader=FileSystemLoader(Path(__file__).parent / "templates"),
    autoescape=select_autoescape(["html"]),  # banners come from the target: always escape them!
)


def _fmt(dt):
    return dt.strftime("%Y-%m-%d %H:%M UTC") if dt else "-"


def _sorted(findings):
    return sorted(findings, key=lambda f: (SEVERITY_ORDER.index(f.severity), f.category, f.title))


def _counts(findings):
    return {s: sum(1 for f in findings if f.severity == s) for s in SEVERITY_ORDER}


def build_json(scan) -> str:
    data = {
        "tool": "VulnSight",
        "scan": {
            "id": scan.id, "target": scan.target, "ip": scan.resolved_ip, "profile": scan.profile,
            "status": scan.status, "risk_score": scan.risk_score, "risk_level": scan.risk_level,
            "started_at": _fmt(scan.started_at), "finished_at": _fmt(scan.finished_at),
        },
        "summary": _counts(scan.findings),
        "findings": [
            {"severity": f.severity, "category": f.category, "title": f.title, "details": f.details,
             "explanation": f.explanation, "fix": f.fix}
            for f in _sorted(scan.findings)
        ],
    }
    return json.dumps(data, indent=2)


def build_txt(scan) -> str:
    line = "=" * 70
    out = [line, f"VulnSight report: {scan.target}", line,
           f"Scan ID:    {scan.id}", f"IP address: {scan.resolved_ip}", f"Profile:    {scan.profile}",
           f"Started:    {_fmt(scan.started_at)}", f"Finished:   {_fmt(scan.finished_at)}",
           f"Risk:       {scan.risk_level} ({scan.risk_score}/100)", ""]
    counts = _counts(scan.findings)
    out.append("Summary: " + ", ".join(f"{k} {v}" for k, v in counts.items()))
    out.append("")
    for f in _sorted(scan.findings):
        out += ["-" * 70, f"[{f.severity.upper()}] {f.title}  ({f.category})"]
        if f.details:
            out.append(f"Details: {f.details}")
        if f.explanation:
            out.append(f"What it means: {f.explanation}")
        if f.fix:
            out.append(f"How to fix: {f.fix}")
        out.append("")
    out.append("Only scan systems you own or have written permission to test.")
    return "\n".join(out)


def build_html(scan) -> str:
    return _env.get_template("report.html").render(
        scan=scan, findings=_sorted(scan.findings), counts=_counts(scan.findings),
        started=_fmt(scan.started_at), finished=_fmt(scan.finished_at),
    )


def safe_filename(scan, ext: str) -> str:
    name = re.sub(r"[^A-Za-z0-9.-]", "_", scan.target)
    return f"vulnsight-{name}-scan{scan.id}.{ext}"
