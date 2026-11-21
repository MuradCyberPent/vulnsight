"""Feature: HTTP security headers check (also finds the web server banner). (Member 2)"""
import re

import requests
import urllib3

from app.core.checks import register_check
from app.core.finding_utils import USER_AGENT, finding, netloc

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# header, severity, title, explanation, fix
CHECKS = [
    ("strict-transport-security", "Medium", "Missing HSTS header",
     "HSTS tells browsers to ALWAYS use HTTPS for your site, which blocks downgrade and sniffing attacks.",
     "Add the header: Strict-Transport-Security: max-age=31536000; includeSubDomains"),
    ("content-security-policy", "Medium", "Missing Content-Security-Policy (CSP)",
     "CSP limits which scripts can run on your pages, making cross-site scripting (XSS) much harder.",
     "Add a Content-Security-Policy header, starting with: default-src 'self'"),
    ("x-frame-options", "Low", "Missing X-Frame-Options (clickjacking protection)",
     "Without it, another website can load your page invisibly in a frame and trick users into clicking things.",
     "Add the header: X-Frame-Options: DENY (or use CSP 'frame-ancestors')."),
    ("x-content-type-options", "Low", "Missing X-Content-Type-Options",
     "Stops browsers from guessing file types, which can turn an uploaded file into running code.",
     "Add the header: X-Content-Type-Options: nosniff"),
    ("referrer-policy", "Low", "Missing Referrer-Policy",
     "Controls how much of your page address is shared with other sites when users click links.",
     "Add the header: Referrer-Policy: strict-origin-when-cross-origin"),
    ("permissions-policy", "Low", "Missing Permissions-Policy",
     "Lets you switch off browser features (camera, microphone, location) your site never uses.",
     "Add the header: Permissions-Policy: camera=(), microphone=(), geolocation=()"),
]


def _get(url: str, timeout: int = 8):
    # Redirects are NOT followed on purpose: a redirect could point at an internal address.
    return requests.get(url, headers=USER_AGENT, timeout=timeout, verify=False, allow_redirects=False)


@register_check("headers", "HTTP security headers", 20)
def run(ctx: dict) -> list[dict]:
    host = netloc(ctx["host"])
    resp = scheme = None
    for s in ("https", "http"):
        try:
            resp = _get(f"{s}://{host}/")
            scheme = s
            break
        except requests.RequestException:
            continue

    if resp is None:
        ctx["web_scheme"] = None
        return [finding(
            "Web", "Info", "No web server found on ports 80 or 443", "web-none",
            "Neither http:// nor https:// answered.",
            "We could not reach a website on the standard web ports, so web checks were skipped.",
            "If you expected a website here, check that it is running and the firewall allows 80/443.",
        )]

    ctx["web_scheme"] = scheme
    h = resp.headers
    results = []

    results.append(finding(
        "Web", "Info", f"Website answered on {scheme}:// (status {resp.status_code})", "web-reachable",
        f"Requested {scheme}://{ctx['host']}/ and received HTTP {resp.status_code}.",
        "The website is reachable. The checks below look at the security settings it sends to browsers.",
    ))

    if scheme == "http":
        results.append(finding(
            "Web", "High", "Website does not offer HTTPS", "https-missing",
            "https://" + ctx["host"] + "/ did not answer.",
            "Without HTTPS, everything users type (including passwords) travels as readable text.",
            "Install a free certificate (Let's Encrypt) and serve the site over HTTPS.",
        ))
    else:
        # Does plain HTTP get sent to HTTPS?
        try:
            plain = _get(f"http://{host}/", timeout=5)
            loc = plain.headers.get("Location", "")
            if not (300 <= plain.status_code < 400 and loc.lower().startswith("https://")):
                results.append(finding(
                    "Web", "Medium", "HTTP is not redirected to HTTPS", "http-no-redirect",
                    f"http://{ctx['host']}/ answered with status {plain.status_code} instead of redirecting.",
                    "Visitors who type the plain http:// address stay on an unencrypted connection.",
                    "Configure the server to redirect all http:// requests to https:// (301).",
                ))
        except requests.RequestException:
            pass

    csp = h.get("content-security-policy", "")
    for name, sev, title, why, fix in CHECKS:
        if name == "strict-transport-security" and scheme != "https":
            continue
        present = name in h
        if name == "x-frame-options" and "frame-ancestors" in csp.lower():
            present = True
        if name == "x-content-type-options" and present and h[name].lower() != "nosniff":
            present = False
        if not present:
            results.append(finding("Web", sev, title, f"header-missing:{name}",
                                   f"The response did not include '{name}'.", why, fix))

    # Version leaks
    for hdr in ("server", "x-powered-by"):
        value = h.get(hdr)
        if value:
            ctx["banners"].append((f"HTTP {hdr} header", f"{hdr.title()}: {value}"))
            if re.search(r"\d", value):
                results.append(finding(
                    "Web", "Low", f"'{hdr.title()}' header reveals a version", f"header-leak:{hdr}",
                    f"{hdr.title()}: {value}",
                    "Telling the world your exact software version helps attackers pick the right exploit.",
                    "Configure your server to hide version numbers (e.g. 'server_tokens off;' in nginx).",
                ))

    # Cookie flags
    cookies = resp.raw.headers.getlist("Set-Cookie") if hasattr(resp.raw.headers, "getlist") else []
    no_http_only, no_secure, no_samesite = [], [], []
    for c in cookies:
        name = c.split("=", 1)[0].strip()
        low = c.lower()
        if "httponly" not in low:
            no_http_only.append(name)
        if scheme == "https" and "secure" not in low:
            no_secure.append(name)
        if "samesite" not in low:
            no_samesite.append(name)
    for names, flag, why, fix in [
        (no_http_only, "HttpOnly", "JavaScript can read these cookies, so an XSS bug could steal user sessions.", "Add the HttpOnly flag to the cookie."),
        (no_secure, "Secure", "These cookies can be sent over unencrypted connections.", "Add the Secure flag to the cookie."),
        (no_samesite, "SameSite", "Without SameSite, other websites can trigger requests that carry these cookies (CSRF).", "Add SameSite=Lax (or Strict) to the cookie."),
    ]:
        if names:
            results.append(finding("Web", "Low", f"Cookie missing the {flag} flag", f"cookie-flag:{flag.lower()}",
                                   "Cookies: " + ", ".join(sorted(set(names))), why, fix))
    return results
