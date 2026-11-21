"""Feature: SSL/TLS checker (certificate expiry, hostname mismatch, weak protocols). (Member 2)"""
import socket
import ssl
from datetime import datetime, timezone

from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from app.core.checks import register_check
from app.core.finding_utils import finding


def _handshake(ip, host, is_ip, port, min_v=None, max_v=None, timeout=6):
    """Open a TLS connection WITHOUT trust checks (so we can still read bad certificates)."""
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    if min_v is not None:
        ctx.minimum_version = min_v
        ctx.maximum_version = max_v
        try:
            ctx.set_ciphers("ALL:@SECLEVEL=0")  # allow old protocols just for this test
        except ssl.SSLError:
            pass
    with socket.create_connection((ip, port), timeout=timeout) as sock:
        with ctx.wrap_socket(sock, server_hostname=None if is_ip else host) as tls:
            return tls.getpeercert(binary_form=True), tls.version(), tls.cipher()


def _name_matches(pattern: str, host: str) -> bool:
    pattern, host = pattern.lower(), host.lower()
    if pattern.startswith("*."):
        return "." in host and host.split(".", 1)[1] == pattern[2:]
    return pattern == host


@register_check("ssl", "SSL/TLS", 30)
def run(ctx: dict) -> list[dict]:
    host, ip, is_ip, port = ctx["host"], ctx["ip"], ctx["is_ip"], 443
    try:
        der, version, cipher = _handshake(ip, host, is_ip, port)
    except (OSError, ssl.SSLError):
        return [finding(
            "SSL/TLS", "Info", "No HTTPS service on port 443", "ssl-none",
            f"Could not complete a TLS connection to {host}:443.",
            "There is no encrypted website on the standard HTTPS port, so certificate checks were skipped.",
        )]

    results = []
    cert = x509.load_der_x509_certificate(der)
    not_after = getattr(cert, "not_valid_after_utc", None)
    if not_after is None:  # older cryptography versions
        not_after = cert.not_valid_after.replace(tzinfo=timezone.utc)
    days_left = (not_after - datetime.now(timezone.utc)).days
    date_text = not_after.strftime("%Y-%m-%d")

    # Expiry
    if days_left < 0:
        results.append(finding(
            "SSL/TLS", "High", "SSL certificate has expired", "ssl-expired",
            f"The certificate expired on {date_text} ({-days_left} days ago).",
            "Browsers show a big red warning page, and many users will leave. The connection is also no longer trusted.",
            "Renew the certificate now. With Let's Encrypt run 'certbot renew' and set up automatic renewal.",
        ))
    elif days_left <= 14:
        results.append(finding(
            "SSL/TLS", "High", f"SSL certificate expires in {days_left} days", "ssl-expiring",
            f"Valid until {date_text}.", "When it expires, visitors will see security warnings.",
            "Renew the certificate now and enable automatic renewal.",
        ))
    elif days_left <= 30:
        results.append(finding(
            "SSL/TLS", "Medium", f"SSL certificate expires in {days_left} days", "ssl-expiring",
            f"Valid until {date_text}.", "When it expires, visitors will see security warnings.",
            "Renew the certificate soon and enable automatic renewal.",
        ))
    else:
        results.append(finding(
            "SSL/TLS", "Info", f"SSL certificate is valid for {days_left} more days", "ssl-valid",
            f"Valid until {date_text}.", "The certificate is within its validity period.",
        ))

    # Names / hostname mismatch
    try:
        sans = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName).value.get_values_for_type(x509.DNSName)
    except x509.ExtensionNotFound:
        sans = []
    cn_attrs = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)
    names = list(sans) or [a.value for a in cn_attrs]
    if not is_ip:
        if not any(_name_matches(n, host) for n in names):
            results.append(finding(
                "SSL/TLS", "High", "Certificate does not match the hostname", "ssl-hostname-mismatch",
                f"Certificate is for: {', '.join(names) or 'unknown'}. You scanned: {host}.",
                "The certificate belongs to a different website name, so browsers will warn visitors.",
                "Get a certificate that includes this exact hostname.",
            ))

    # Self-signed / untrusted
    self_signed = cert.issuer == cert.subject
    if self_signed:
        results.append(finding(
            "SSL/TLS", "Medium", "Certificate is self-signed", "ssl-self-signed",
            "The certificate was signed by itself, not by a trusted authority.",
            "Browsers cannot verify who this server really is, so users see a warning (and could be tricked by an impostor).",
            "Use a certificate from a trusted authority. Let's Encrypt is free.",
        ))
    elif not is_ip:
        try:
            verify = ssl.create_default_context()
            with socket.create_connection((ip, port), timeout=6) as sock:
                with verify.wrap_socket(sock, server_hostname=host):
                    pass
        except ssl.SSLCertVerificationError as e:
            if days_left >= 0 and any(_name_matches(n, host) for n in names):
                results.append(finding(
                    "SSL/TLS", "Medium", "Certificate is not trusted", "ssl-untrusted",
                    f"Verification failed: {e.verify_message}.",
                    "Your computer could not build a trusted chain from this certificate to a known authority.",
                    "Install the full certificate chain (including intermediate certificates) on the server.",
                ))
        except (OSError, ssl.SSLError):
            pass

    # Key strength / signature
    pub = cert.public_key()
    if isinstance(pub, rsa.RSAPublicKey) and pub.key_size < 2048:
        results.append(finding(
            "SSL/TLS", "High", f"Weak RSA key ({pub.key_size} bits)", "ssl-weak-key",
            f"The certificate uses a {pub.key_size}-bit RSA key.",
            "Short keys can be broken with enough computing power.",
            "Generate a new key of at least 2048 bits and reissue the certificate.",
        ))
    sig = cert.signature_hash_algorithm.name if cert.signature_hash_algorithm else ""
    if sig in ("sha1", "md5"):
        results.append(finding(
            "SSL/TLS", "Medium", f"Certificate signed with weak hash ({sig.upper()})", "ssl-weak-signature",
            f"Signature algorithm uses {sig.upper()}.", "This hash can be forged, so the signature is not reliable.",
            "Reissue the certificate using SHA-256 or better.",
        ))

    # Protocols
    weak = []
    for label, ver in (("TLS 1.0", ssl.TLSVersion.TLSv1), ("TLS 1.1", ssl.TLSVersion.TLSv1_1)):
        try:
            _handshake(ip, host, is_ip, port, ver, ver, timeout=5)
            weak.append(label)
        except (OSError, ssl.SSLError, ValueError):
            pass
    if weak:
        results.append(finding(
            "SSL/TLS", "High", f"Outdated protocols enabled: {', '.join(weak)}", "ssl-weak-protocol",
            f"The server still accepts {', '.join(weak)} connections.",
            "These old versions have known attacks (like BEAST and POODLE) and were retired in 2021.",
            "Disable TLS 1.0 and 1.1; allow only TLS 1.2 and TLS 1.3.",
        ))
    else:
        results.append(finding(
            "SSL/TLS", "Info", f"Modern TLS in use ({version})", "ssl-protocol",
            f"Negotiated {version} with cipher {cipher[0] if cipher else 'unknown'}. TLS 1.0/1.1 were not accepted.",
            "The server uses modern encryption settings.",
        ))
    return results
