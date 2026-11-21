"""Scan profiles: Quick, Full and Web-only. (Member 1)

Each profile lists which checks to run (names come from the files in checks/).
"""
from app.modules.scanning.checks.ports import FULL_PORT_SPEC

PROFILES = {
    "quick": {
        "label": "Quick",
        "description": "Common ports, web headers, SSL and known-vulnerable versions. Takes under a minute.",
        "steps": ["ports", "headers", "ssl", "cve"],
        "ports": "common",
    },
    "full": {
        "label": "Full",
        "description": "Everything: ports 1-1024 and popular service ports, web, SSL, files, DNS, subdomains, cloud buckets.",
        "steps": ["ports", "headers", "ssl", "exposed", "dns", "subdomains", "cloud", "cve"],
        "ports": FULL_PORT_SPEC,
    },
    "web-only": {
        "label": "Web only",
        "description": "Skips port scanning. Checks headers, SSL, exposed files and software versions.",
        "steps": ["headers", "ssl", "exposed", "cve"],
        "ports": None,
    },
}
