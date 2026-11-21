"""Feature: subdomain lookup (tries a short list of common names). (Member 3)"""
import secrets
from concurrent.futures import ThreadPoolExecutor

import dns.resolver

from app.core.checks import register_check
from app.core.finding_utils import finding
from .dns_check import lookup, make_resolver

WORDLIST = [
    "www", "mail", "webmail", "smtp", "ftp", "api", "dev", "test", "staging", "stage", "beta",
    "admin", "portal", "vpn", "remote", "blog", "shop", "store", "cdn", "static", "assets",
    "app", "m", "mobile", "secure", "intranet", "support", "docs", "status", "git", "gitlab",
    "jenkins", "grafana", "kibana", "dashboard", "db", "old", "backup", "demo", "ns1", "ns2",
]
SENSITIVE = {"dev", "test", "staging", "stage", "beta", "admin", "jenkins", "git", "gitlab",
             "grafana", "kibana", "db", "backup", "old", "intranet", "vpn", "remote", "demo"}


@register_check("subdomains", "Subdomains", 60)
def run(ctx: dict) -> list[dict]:
    if ctx["is_ip"]:
        return []
    host = ctx["host"]
    try:
        resolver = make_resolver()
    except dns.resolver.NoResolverConfiguration:
        return []

    # Wildcard DNS answers for everything; that would make every guess look real.
    if lookup(resolver, f"{secrets.token_hex(6)}.{host}", "A"):
        return [finding("Subdomains", "Info", "Wildcard DNS detected, subdomain guessing skipped", "subdomains-wildcard",
                        "Random made-up subdomains resolve, so guesses cannot be trusted.",
                        "The domain answers for any name, so we cannot tell real subdomains from fake ones.")]

    def check(word):
        name = f"{word}.{host}"
        ips = lookup(resolver, name, "A") or lookup(resolver, name, "AAAA")
        return (name, ips[0]) if ips else None

    with ThreadPoolExecutor(max_workers=20) as pool:
        found = [r for r in pool.map(check, WORDLIST) if r]

    if not found:
        return [finding("Subdomains", "Info", "No common subdomains found", "subdomains-none",
                        f"Tried {len(WORDLIST)} common names.", "None of the guessed names exist.")]

    results = [finding(
        "Subdomains", "Info", f"{len(found)} subdomain(s) found", "subdomains-found",
        "\n".join(f"{n}  ->  {ip}" for n, ip in found),
        "Every subdomain is another place that needs to be kept updated and protected. Forgotten ones are a common way in.",
        "Remove DNS entries for services you no longer use.",
    )]
    risky = [n for n, _ in found if n.split(".")[0] in SENSITIVE]
    if risky:
        results.append(finding(
            "Subdomains", "Low", "Test or admin-style subdomains are public", "subdomains-sensitive",
            "\n".join(risky),
            "Names like dev, staging or admin often point at less-protected systems with weak passwords or old code.",
            "Put these behind a VPN or login, or remove them from public DNS.",
        ))
    return results
