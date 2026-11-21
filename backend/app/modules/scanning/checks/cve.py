"""Feature: outdated version check (compares banners with data/cve.json). (Member 2)"""
import json
import re
from functools import lru_cache
from pathlib import Path

from app.core.checks import register_check
from app.core.finding_utils import finding

CVE_FILE = Path(__file__).resolve().parents[4] / "data" / "cve.json"


@lru_cache(maxsize=1)
def load_db() -> dict:
    with open(CVE_FILE, encoding="utf-8") as f:
        return json.load(f)


def version_tuple(v: str) -> tuple:
    return tuple(int(n) for n in re.findall(r"\d+", v))


def _pad(a: tuple, b: tuple):
    n = max(len(a), len(b))
    return a + (0,) * (n - len(a)), b + (0,) * (n - len(b))


def is_affected(version: str, min_version: str, fixed_in: str) -> bool:
    v, lo = _pad(version_tuple(version), version_tuple(min_version))
    v2, hi = _pad(version_tuple(version), version_tuple(fixed_in))
    return lo <= v and v2 < hi


def detect_software(banners: list) -> dict:
    """[(source, text)] -> {'nginx': '1.18.0', ...}"""
    found = {}
    for _src, text in banners:
        for product, pattern in load_db()["products"].items():
            m = re.search(pattern, text, re.I)
            if m and product not in found:
                found[product] = m.group(1)
    return found


@register_check("cve", "Known vulnerabilities", 80)
def run(ctx: dict) -> list[dict]:
    db = load_db()
    software = detect_software(ctx.get("banners", []))
    results = []

    for product, version in software.items():
        results.append(finding(
            "Software", "Info", f"Detected {product} {version}", f"software:{product}",
            f"The server announced {product} version {version}.",
            "Servers often announce what they run. That is useful for you, and for attackers looking for known bugs.",
            "Hide version numbers where you can (for example 'server_tokens off;' in nginx, 'ServerTokens Prod' in Apache).",
        ))

    for vuln in db["vulnerabilities"]:
        version = software.get(vuln["product"])
        if version and is_affected(version, vuln["min_version"], vuln["fixed_in"]):
            cvss = f" (CVSS {vuln['cvss']})" if vuln.get("cvss") else ""
            results.append(finding(
                "Known vulnerabilities", vuln["severity"],
                f"{vuln['product']} {version} is outdated: {vuln['id']}", f"cve:{vuln['id']}",
                f"{vuln['description']}{cvss} Found: {vuln['product']} {version}; fixed in {vuln['fixed_in']}.",
                "The version number this server reports has a publicly known weakness. "
                "Attackers scan the internet for exactly these versions.",
                vuln["fix"],
            ))
    return results
