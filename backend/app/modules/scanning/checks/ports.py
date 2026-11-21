"""Feature: port scanner + service/banner detection. (Member 1)"""
import re
import socket
from concurrent.futures import ThreadPoolExecutor

from app.core.checks import register_check
from app.core.finding_utils import finding

COMMON_PORTS = {
    21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp", 53: "dns", 80: "http", 110: "pop3",
    111: "rpcbind", 135: "msrpc", 139: "netbios", 143: "imap", 443: "https", 445: "smb",
    465: "smtps", 587: "submission", 993: "imaps", 995: "pop3s", 1433: "mssql",
    1521: "oracle", 2049: "nfs", 3306: "mysql", 3389: "rdp", 5432: "postgresql",
    5900: "vnc", 6379: "redis", 8000: "http-alt", 8080: "http-proxy", 8443: "https-alt",
    9200: "elasticsearch", 11211: "memcached", 27017: "mongodb",
}

FULL_PORT_SPEC = "1-1024,1433,1521,2049,3306,3389,5432,5900,6379,8000,8080,8443,9200,11211,27017"

HTTP_PORTS = {80, 8000, 8080, 8888}
TLS_PORTS = {443, 465, 993, 995, 8443}

# port -> (severity, title, explanation, fix)
RISKY = {
    23: ("High", "Telnet is open", "Telnet sends everything, including passwords, as plain readable text.", "Turn Telnet off and use SSH instead."),
    21: ("Medium", "FTP is open", "FTP sends passwords without encryption, so anyone on the network can read them.", "Use SFTP (over SSH) instead, or restrict FTP to trusted IPs."),
    3389: ("High", "Remote Desktop (RDP) is open to the internet", "RDP is a favourite target for password guessing and ransomware attacks.", "Put RDP behind a VPN or firewall rule that only allows your own IP."),
    445: ("High", "Windows file sharing (SMB) is open", "SMB has had serious wormable bugs (like EternalBlue) and should never face the internet.", "Block port 445 at the firewall."),
    139: ("Medium", "NetBIOS is open", "Old Windows networking service that leaks information about your machine.", "Block port 139 at the firewall."),
    135: ("Medium", "Windows RPC is open", "Windows RPC has a long history of vulnerabilities and should not be public.", "Block port 135 at the firewall."),
    111: ("Medium", "rpcbind is open", "rpcbind can reveal which network services a machine offers.", "Close it or restrict it to trusted IPs."),
    2049: ("Medium", "NFS file sharing is open", "NFS can expose whole folders to anyone who can reach it.", "Restrict NFS to internal IPs only."),
    5900: ("High", "VNC remote screen is open", "VNC often has weak or no passwords and gives full control of the machine.", "Tunnel VNC through SSH or a VPN, and close the public port."),
    3306: ("High", "MySQL database is open to the internet", "Databases should only be reachable by your own application, not the whole internet.", "Bind MySQL to 127.0.0.1 or block port 3306 at the firewall."),
    5432: ("High", "PostgreSQL database is open to the internet", "Databases should only be reachable by your own application, not the whole internet.", "Restrict PostgreSQL with listen_addresses and pg_hba.conf, and block port 5432."),
    1433: ("High", "Microsoft SQL Server is open to the internet", "Databases should only be reachable by your own application, not the whole internet.", "Block port 1433 at the firewall."),
    1521: ("High", "Oracle database is open to the internet", "Databases should only be reachable by your own application, not the whole internet.", "Block port 1521 at the firewall."),
    6379: ("High", "Redis is open to the internet", "Redis was built for trusted networks and often runs without a password.", "Bind Redis to localhost, enable a password, and block port 6379."),
    27017: ("High", "MongoDB is open to the internet", "Many MongoDB servers have been wiped or held for ransom because they were left open.", "Enable authentication and block port 27017 at the firewall."),
    9200: ("High", "Elasticsearch is open to the internet", "Open Elasticsearch servers regularly leak huge amounts of data.", "Enable security features and block port 9200 from the internet."),
    11211: ("High", "Memcached is open to the internet", "Open Memcached leaks cached data and can be abused for DDoS attacks.", "Bind Memcached to localhost and block port 11211."),
}


def parse_ports(spec: str, limit: int) -> list[int]:
    """'22,80,443' or '1-1024' or '1-100,443' -> sorted list of ports."""
    ports: set[int] = set()
    try:
        for part in spec.split(","):
            part = part.strip()
            if not part:
                continue
            if "-" in part:
                a, b = part.split("-", 1)
                lo, hi = sorted((int(a), int(b)))
                ports.update(range(lo, hi + 1))
            else:
                ports.add(int(part))
    except ValueError:
        raise ValueError("Ports must look like 22,80,443 or 1-1024")
    if not ports:
        raise ValueError("Ports must look like 22,80,443 or 1-1024")
    if min(ports) < 1 or max(ports) > 65535:
        raise ValueError("Ports must be between 1 and 65535")
    if len(ports) > limit:
        raise ValueError(f"Too many ports (maximum {limit} per scan)")
    return sorted(ports)


def _probe(ip: str, port: int, timeout: float):
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return port
    except OSError:
        return None


def scan_ports(ip: str, ports: list[int], timeout: float = 0.8, workers: int = 100) -> list[int]:
    """Try to connect to every port at once (threads); return the ones that answered."""
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = pool.map(lambda p: _probe(ip, p, timeout), ports)
        return sorted(p for p in results if p)


def grab_banner(ip: str, port: int, host: str) -> str:
    """Read the greeting a service sends (or ask politely for one)."""
    if port in TLS_PORTS:
        return ""  # encrypted; the HTTP/SSL checks handle these
    try:
        with socket.create_connection((ip, port), timeout=2) as s:
            s.settimeout(2)
            if port in HTTP_PORTS:
                s.sendall(f"HEAD / HTTP/1.0\r\nHost: {host}\r\nUser-Agent: VulnSight\r\n\r\n".encode())
            elif port == 6379:
                s.sendall(b"PING\r\n")
            data = s.recv(1024)
    except OSError:
        return ""
    if not data:
        return ""

    if port == 3306 and len(data) > 5 and data[4] == 10:  # MySQL handshake packet
        return "MySQL " + data[5:].split(b"\x00")[0].decode("ascii", "replace")

    text = re.sub(r"[^\x20-\x7e\r\n]", "", data.decode("utf-8", "replace")).strip()
    if port in HTTP_PORTS:
        lines = text.splitlines()
        server = next((l for l in lines if l.lower().startswith("server:")), "")
        return server or (lines[0] if lines else "")
    return text.splitlines()[0][:200] if text else ""


def identify_service(port: int, banner: str) -> str:
    b = banner.upper()
    if b.startswith("SSH-"):
        return "ssh"
    if "SMTP" in b or "ESMTP" in b:
        return "smtp"
    if "FTP" in b:
        return "ftp"
    if b.startswith("HTTP/") or b.startswith("SERVER:"):
        return "http"
    if "MYSQL" in b:
        return "mysql"
    if b.startswith("+PONG") or "NOAUTH" in b:
        return "redis"
    return COMMON_PORTS.get(port, "unknown")


@register_check("ports", "Port scan and banners", 10)
def run(ctx: dict) -> list[dict]:
    spec = ctx.get("ports_spec")
    ports = list(COMMON_PORTS) if not spec or spec == "common" else parse_ports(spec, 65535)
    open_ports = scan_ports(ctx["ip"], ports)
    ctx["open_ports"] = open_ports

    results = []
    if not open_ports:
        results.append(finding(
            "Ports", "Info", "No open ports found", "ports-none",
            f"Checked {len(ports)} ports on {ctx['ip']}; none accepted a connection.",
            "Nothing answered on the ports we tried. That is good: fewer open doors means less to attack. "
            "(A firewall can also hide ports, so this is not proof of safety.)",
        ))
        return results

    for port in open_ports:
        banner = grab_banner(ctx["ip"], port, ctx["host"])
        if banner:
            ctx["banners"].append((f"port {port}", banner))
        service = identify_service(port, banner)
        detail = f"Port {port}/tcp is open. Service: {service}."
        if banner:
            detail += f" Banner: {banner}"

        if port == 6379 and banner.startswith("+PONG"):
            results.append(finding(
                "Ports", "Critical", "Redis accepts commands without a password", f"port-open:{port}", detail,
                "Anyone on the internet can read, change or delete everything stored in this Redis server, "
                "and often take over the whole machine.",
                "Set 'requirepass' in redis.conf, bind Redis to 127.0.0.1, and block port 6379 at the firewall.",
            ))
        elif port in RISKY:
            sev, title, why, fix = RISKY[port]
            results.append(finding("Ports", sev, title, f"port-open:{port}", detail, why, fix))
        else:
            results.append(finding(
                "Ports", "Info", f"Open port {port}/tcp ({service})", f"port-open:{port}", detail,
                "This port accepts connections. Open ports are not automatically bad, but every open port "
                "is something that must be kept updated. Close anything you do not need.",
                "If this service is not needed, stop it or block the port in your firewall.",
            ))
    return results
