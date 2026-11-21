"""Feature: DNS lookup (records, email protection, zone-transfer test). (Member 3)"""
import dns.exception
import dns.query
import dns.resolver
import dns.zone

from app.core.checks import register_check
from app.core.finding_utils import finding


def make_resolver() -> dns.resolver.Resolver:
    r = dns.resolver.Resolver()
    r.timeout = 2
    r.lifetime = 4
    return r


def lookup(resolver, name: str, rtype: str) -> list[str]:
    try:
        return [a.to_text() for a in resolver.resolve(name, rtype)]
    except (dns.exception.DNSException, OSError):
        return []


@register_check("dns", "DNS records", 50)
def run(ctx: dict) -> list[dict]:
    if ctx["is_ip"]:
        return [finding("DNS", "Info", "DNS checks skipped (target is an IP address)", "dns-skipped",
                        "DNS records only exist for domain names.", "Scan a domain name to see its DNS records.")]
    host = ctx["host"]
    try:
        resolver = make_resolver()
    except dns.resolver.NoResolverConfiguration:
        return [finding("DNS", "Info", "DNS checks skipped (no DNS resolver configured)", "dns-skipped",
                        "This computer has no DNS server configured.", "Check your network settings.")]

    records = {t: lookup(resolver, host, t) for t in ("A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA")}
    results = []
    lines = [f"{t}: {', '.join(v)}" for t, v in records.items() if v]
    results.append(finding(
        "DNS", "Info", "DNS records found" if lines else "No DNS records found", "dns-records",
        "\n".join(lines) or "The resolver returned no records.",
        "DNS is the internet's phone book. These records show where your site and email live.",
    ))

    # Email spoofing protection (only matters if the domain receives mail)
    if records["MX"]:
        spf = [t for t in records["TXT"] if "v=spf1" in t.lower()]
        if not spf:
            results.append(finding(
                "DNS", "Medium", "No SPF record (email can be forged)", "dns-no-spf",
                "No TXT record starting with v=spf1.",
                "SPF lists which servers may send email for your domain. Without it, scammers can send mail that appears to come from you.",
                "Add a TXT record such as: v=spf1 include:_spf.yourmailprovider.com -all",
            ))
        elif any(" +all" in t or " ?all" in t for t in spf):
            results.append(finding(
                "DNS", "High", "SPF record allows anyone to send email", "dns-open-spf",
                "SPF: " + spf[0],
                "The record ends in +all or ?all, which makes SPF useless.",
                "End your SPF record with '-all' (or '~all').",
            ))
        dmarc = lookup(resolver, f"_dmarc.{host}", "TXT")
        if not any("v=dmarc1" in t.lower() for t in dmarc):
            results.append(finding(
                "DNS", "Low", "No DMARC record", "dns-no-dmarc",
                f"No TXT record found at _dmarc.{host}.",
                "DMARC tells other mail servers what to do with fake emails that claim to be from your domain.",
                "Add a TXT record at _dmarc with: v=DMARC1; p=quarantine; rua=mailto:you@yourdomain.com",
            ))

    # Zone transfer test
    for ns in [n.rstrip(".") for n in records["NS"]][:4]:
        ns_ips = lookup(resolver, ns, "A")
        if not ns_ips:
            continue
        try:
            zone = dns.zone.from_xfr(dns.query.xfr(ns_ips[0], host, lifetime=5))
            results.append(finding(
                "DNS", "High", "DNS zone transfer is allowed", "dns-axfr",
                f"Name server {ns} handed over {len(zone.nodes)} records.",
                "Anyone can download a complete list of your DNS records, including internal hostnames.",
                "Restrict zone transfers (AXFR) to your secondary name servers only.",
            ))
            break
        except Exception:
            continue
    return results
