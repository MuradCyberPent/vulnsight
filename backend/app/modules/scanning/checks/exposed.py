"""Feature: exposed file finder (.env, .git, backups, ...). (Member 3)"""
import re
import uuid
from concurrent.futures import ThreadPoolExecutor

import requests

from app.core.checks import register_check
from app.core.finding_utils import USER_AGENT, finding, netloc
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def _not_html(b: bytes) -> bool:
    return b"<html" not in b[:600].lower() and b"<!doctype" not in b[:600].lower()


def _sql(b):
    return bool(re.search(rb"CREATE TABLE|INSERT INTO|DROP TABLE|MySQL dump", b, re.I))


# path, severity, title, validator(bytes)->bool, explanation, fix
CHECKS = [
    ("/.env", "Critical", "Environment file (.env) is public",
     lambda b: _not_html(b) and bool(re.search(rb"^[A-Za-z_][A-Za-z0-9_]*\s*=", b, re.M)),
     "A .env file usually holds passwords, API keys and database logins. Anyone can download it.",
     "Delete it from the web folder or block access in your server config, then CHANGE every secret inside it."),
    ("/.git/HEAD", "Critical", "Git repository is exposed (.git folder)",
     lambda b: b.startswith(b"ref:"),
     "Attackers can download your whole source code history, often including passwords.",
     "Block access to '/.git' in your web server, or deploy without the .git folder. Rotate any secrets in the history."),
    ("/.git/config", "High", "Git config file is exposed",
     lambda b: b"[core]" in b, "Reveals repository settings and sometimes private repository URLs.",
     "Block access to '/.git' in your web server."),
    ("/id_rsa", "Critical", "Private SSH key is public",
     lambda b: b"PRIVATE KEY" in b, "Anyone can use this key to log in as you.",
     "Remove the file and replace the key pair immediately."),
    ("/.aws/credentials", "Critical", "AWS credentials file is public",
     lambda b: b"aws_access_key_id" in b.lower(), "Attackers can use these keys to control your AWS account.",
     "Remove the file and deactivate/rotate the AWS keys right now."),
    ("/backup.zip", "High", "Backup archive is downloadable (backup.zip)", lambda b: b.startswith(b"PK\x03\x04"),
     "Backups contain your site code and often data. Attackers guess these file names.", "Move backups out of the web folder."),
    ("/site.zip", "High", "Backup archive is downloadable (site.zip)", lambda b: b.startswith(b"PK\x03\x04"),
     "Backups contain your site code and often data.", "Move backups out of the web folder."),
    ("/www.zip", "High", "Backup archive is downloadable (www.zip)", lambda b: b.startswith(b"PK\x03\x04"),
     "Backups contain your site code and often data.", "Move backups out of the web folder."),
    ("/backup.tar.gz", "High", "Backup archive is downloadable (backup.tar.gz)", lambda b: b.startswith(b"\x1f\x8b"),
     "Backups contain your site code and often data.", "Move backups out of the web folder."),
    ("/backup.sql", "Critical", "Database backup is downloadable (backup.sql)", _sql,
     "A database dump can contain every user, email and password hash.", "Delete it and move backups out of the web folder."),
    ("/db.sql", "Critical", "Database backup is downloadable (db.sql)", _sql,
     "A database dump can contain every user, email and password hash.", "Delete it and move backups out of the web folder."),
    ("/dump.sql", "Critical", "Database backup is downloadable (dump.sql)", _sql,
     "A database dump can contain every user, email and password hash.", "Delete it and move backups out of the web folder."),
    ("/database.sql", "Critical", "Database backup is downloadable (database.sql)", _sql,
     "A database dump can contain every user, email and password hash.", "Delete it and move backups out of the web folder."),
    ("/config.php.bak", "High", "Config backup is readable (config.php.bak)",
     lambda b: b"<?php" in b or b"password" in b.lower(),
     "Because it no longer ends in .php, the server shows its source code, including passwords.", "Delete backup copies of config files from the web folder."),
    ("/config.php~", "High", "Editor backup of config is readable (config.php~)",
     lambda b: b"<?php" in b or b"password" in b.lower(),
     "Text editors leave '~' copies that the server shows as plain text.", "Delete editor backup files from the web folder."),
    ("/wp-config.php.bak", "Critical", "WordPress config backup is readable",
     lambda b: b"DB_PASSWORD" in b or b"DB_NAME" in b,
     "Contains your WordPress database name, user and password.", "Delete it and change the database password."),
    ("/.htpasswd", "High", ".htpasswd file is public",
     lambda b: _not_html(b) and bool(re.match(rb"^[^:\s]+:\S+", b)),
     "Contains usernames and password hashes for protected areas.", "Block access to dotfiles in the web server config."),
    ("/.DS_Store", "Low", "macOS .DS_Store file is public",
     lambda b: b.startswith(b"\x00\x00\x00\x01Bud1"),
     "Lists the names of files and folders in the directory, which helps attackers find hidden things.", "Delete .DS_Store files before uploading."),
    ("/phpinfo.php", "Medium", "phpinfo() page is public",
     lambda b: b"phpinfo()" in b or b"PHP Version" in b,
     "Shows detailed server settings, paths and versions that help an attacker.", "Delete the phpinfo file."),
    ("/info.php", "Medium", "phpinfo() page is public (info.php)",
     lambda b: b"phpinfo()" in b or b"PHP Version" in b,
     "Shows detailed server settings, paths and versions that help an attacker.", "Delete the phpinfo file."),
    ("/server-status", "Medium", "Apache server-status page is public",
     lambda b: b"Apache Server Status" in b,
     "Shows live requests, visitor IPs and internal URLs.", "Restrict /server-status to localhost."),
    ("/phpmyadmin/", "Medium", "phpMyAdmin is reachable",
     lambda b: b"phpMyAdmin" in b, "A database admin login exposed to the internet attracts constant password guessing.",
     "Restrict it by IP, put it behind a VPN, or remove it."),
    ("/adminer.php", "Medium", "Adminer database tool is reachable",
     lambda b: b"Adminer" in b, "A database admin login exposed to the internet attracts constant password guessing.",
     "Remove it or restrict access by IP."),
    ("/actuator/env", "High", "Spring Boot actuator /env is public",
     lambda b: b"propertySources" in b or b"activeProfiles" in b,
     "Exposes configuration values, sometimes including secrets.", "Disable or secure actuator endpoints."),
    ("/docker-compose.yml", "Medium", "docker-compose.yml is public",
     lambda b: b"services:" in b, "Reveals your internal architecture and may include passwords.", "Do not publish deployment files in the web folder."),
]


def _fetch(base: str, path: str):
    """Download only the first 2 KB of a file."""
    try:
        r = requests.get(base + path, headers=USER_AGENT, timeout=6, verify=False,
                         allow_redirects=False, stream=True)
        try:
            body = next(r.iter_content(2048), b"")
        finally:
            r.close()
        return r.status_code, body
    except requests.RequestException:
        return None, b""


@register_check("exposed", "Exposed files", 40)
def run(ctx: dict) -> list[dict]:
    scheme = ctx.get("web_scheme")
    if not scheme:
        return []
    base = f"{scheme}://{netloc(ctx['host'])}"

    # A site that answers 200 for everything would cause false alarms; our validators
    # check file contents, so that is handled, but we still note it.
    status, _ = _fetch(base, f"/vulnsight-{uuid.uuid4().hex[:8]}")
    catch_all = status == 200

    def check(spec):
        path, sev, title, validator, why, fix = spec
        status, body = _fetch(base, path)
        if status == 200 and body and validator(body):
            return finding("Exposed files", sev, title, f"exposed:{path}",
                           f"{base}{path} returned content that looks like the real file.", why, fix)
        return None

    with ThreadPoolExecutor(max_workers=12) as pool:
        results = [r for r in pool.map(check, CHECKS) if r]

    # robots.txt is information, not a vulnerability
    status, body = _fetch(base, "/robots.txt")
    if status == 200 and re.search(rb"user-agent", body, re.I) and _not_html(body):
        paths = re.findall(r"(?im)^\s*disallow:\s*(\S+)", body.decode("utf-8", "replace"))
        if paths:
            results.append(finding(
                "Exposed files", "Info", f"robots.txt lists {len(paths)} hidden path(s)", "exposed:/robots.txt",
                "Paths: " + ", ".join(paths[:10]) + (" ..." if len(paths) > 10 else ""),
                "robots.txt asks search engines to skip these pages, but attackers read it as a map of interesting places.",
                "Never rely on robots.txt to hide anything. Protect sensitive pages with a login.",
            ))
    if not results:
        note = " (this site answers 200 for unknown pages, so only file contents were trusted)" if catch_all else ""
        results.append(finding(
            "Exposed files", "Info", "No common sensitive files found", "exposed:none",
            f"Checked {len(CHECKS) + 1} common paths{note}.",
            "None of the well-known risky files were reachable. That is a good sign, but not a guarantee.",
        ))
    return results
