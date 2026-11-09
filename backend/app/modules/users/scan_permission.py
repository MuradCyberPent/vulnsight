"""Scan permission check (scope guard + scan limit). (Member 2)

Decide whether a target is allowed to be scanned at all.

Rules:
  * only ONE host per scan (no ranges like 10.0.0.0/24)
  * link-local (169.254.x.x, includes cloud metadata), multicast, reserved: always blocked
  * private / loopback addresses: blocked unless ALLOW_PRIVATE_TARGETS=true
    (this stops your deployed server from being used to attack its own network)
"""
import ipaddress
import re
import socket
from urllib.parse import urlparse

from fastapi import HTTPException

from app.core.config import settings


class ScopeError(ValueError):
    """Raised with a friendly message when a target is not allowed."""


_HOSTNAME = re.compile(
    r"^(?=.{1,253}$)([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\.)*[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$"
)


def normalize_target(raw: str) -> str:
    """'https://Example.com:8443/path' -> 'example.com'"""
    raw = (raw or "").strip()
    if "://" in raw:
        raw = urlparse(raw).hostname or ""
    else:
        raw = raw.split("/")[0]
        if raw.startswith("["):  # [::1] or [::1]:80
            raw = raw[1:].split("]")[0]
        elif raw.count(":") == 1:  # host:port
            raw = raw.split(":")[0]
    return raw.strip(".").lower()


def validate_target(raw: str, allow_private: bool) -> dict:
    host = normalize_target(raw)
    if not host:
        raise ScopeError("Enter a domain name or IP address, for example example.com")

    try:
        ips = [ipaddress.ip_address(host)]
        is_ip = True
    except ValueError:
        is_ip = False
        if not _HOSTNAME.match(host):
            raise ScopeError("That doesn't look like a valid domain name or IP address.")
        try:
            infos = socket.getaddrinfo(host, None, proto=socket.IPPROTO_TCP)
        except socket.gaierror:
            raise ScopeError(f"Could not find '{host}'. Check the spelling and your internet connection.")
        ips = []
        for info in infos:
            ip = ipaddress.ip_address(info[4][0])
            if ip not in ips:
                ips.append(ip)

    for ip in ips:
        if ip.is_link_local or ip.is_multicast or ip.is_unspecified or ip.is_reserved:
            raise ScopeError("This address is in a range that can never be scanned.")
        if not ip.is_global and not allow_private:
            raise ScopeError(
                "Private and local addresses are blocked on this server. "
                "(Set ALLOW_PRIVATE_TARGETS=true in backend/.env to practise on your own lab.)"
            )

    # Prefer IPv4 when both exist (simpler for port scanning)
    ips.sort(key=lambda i: i.version)
    return {"host": host, "ip": str(ips[0]), "is_ip": is_ip}


def check_scan_permission(authorized: bool, target: str) -> dict:
    """Step 1 and 2 of starting a scan: the permission box must be ticked and the target must be allowed."""
    if not authorized:
        raise HTTPException(400, "Please confirm that you own this target or have permission to test it.")
    try:
        return validate_target(target, settings.ALLOW_PRIVATE_TARGETS)
    except ScopeError as e:
        raise HTTPException(400, str(e))


def check_scan_limit(active_scans: int) -> None:
    """A user may have at most MAX_CONCURRENT_SCANS scans queued or running."""
    if active_scans >= settings.MAX_CONCURRENT_SCANS:
        raise HTTPException(429, "You already have scans running. Wait for one to finish.")
