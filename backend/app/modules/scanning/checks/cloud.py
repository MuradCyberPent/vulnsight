"""Feature: cloud misconfiguration check (public S3 and Google Cloud Storage buckets). (Member 3)"""
import re
from concurrent.futures import ThreadPoolExecutor

import requests

from app.core.checks import register_check
from app.core.finding_utils import USER_AGENT, finding

SUFFIXES = ["backup", "backups", "dev", "prod", "staging", "test", "assets", "static",
            "media", "uploads", "files", "logs", "data", "public", "cdn", "images"]
NOTE = ("Bucket names are guesses based on your domain, so confirm the bucket really belongs to you "
        "before acting on this result.")


def candidates(host: str) -> list[str]:
    parts = host.split(".")
    if len(parts) < 2:
        return []
    base = parts[-2]
    apex = ".".join(parts[-2:])
    names = {base, apex.replace(".", "-")}
    names.update(f"{base}-{s}" for s in SUFFIXES)
    return sorted(n for n in names if re.fullmatch(r"[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]", n))


def _get(url):
    try:
        return requests.get(url, headers=USER_AGENT, timeout=6, allow_redirects=False)
    except requests.RequestException:
        return None


def _check_s3(name):
    r = _get(f"https://{name}.s3.amazonaws.com/")
    if r is not None and r.status_code in (301, 307) and r.headers.get("x-amz-bucket-region"):
        r = _get(f"https://{name}.s3.{r.headers['x-amz-bucket-region']}.amazonaws.com/") or r
    if r is None:
        return None
    if r.status_code == 200 and b"<ListBucketResult" in r.content[:2000]:
        return ("S3", name, "public")
    if r.status_code in (403, 301, 307) or (r.status_code == 200):
        return ("S3", name, "private")
    return None


def _check_gcs(name):
    r = _get(f"https://storage.googleapis.com/{name}/")
    if r is None:
        return None
    if r.status_code == 200 and b"<ListBucketResult" in r.content[:2000]:
        return ("Google Cloud Storage", name, "public")
    if r.status_code == 403:
        return ("Google Cloud Storage", name, "private")
    return None


@register_check("cloud", "Cloud storage", 70)
def run(ctx: dict) -> list[dict]:
    if ctx["is_ip"]:
        return []
    names = candidates(ctx["host"])
    if not names:
        return []
    jobs = [(_check_s3, n) for n in names] + [(_check_gcs, n) for n in names]
    with ThreadPoolExecutor(max_workers=16) as pool:
        hits = [h for h in pool.map(lambda j: j[0](j[1]), jobs) if h]

    results = []
    for provider, name, state in hits:
        if state == "public":
            results.append(finding(
                "Cloud", "Critical", f"Public {provider} bucket: {name}", f"cloud-public:{provider}:{name}",
                f"Anyone on the internet can list the files in '{name}'. {NOTE}",
                "A public bucket lets strangers browse (and often download) everything stored in it. "
                "This is one of the most common causes of big data leaks.",
                "Turn on 'Block all public access' for the bucket, then review what was exposed.",
            ))
    private = [f"{p}: {n}" for p, n, s in hits if s == "private"]
    if private:
        results.append(finding(
            "Cloud", "Info", f"{len(private)} cloud bucket(s) exist with matching names", "cloud-private",
            "\n".join(private) + f"\n{NOTE}",
            "These buckets exist but refused anonymous listing. That is the right setting.",
            "Double-check bucket policies and object-level permissions.",
        ))
    if not hits:
        results.append(finding(
            "Cloud", "Info", "No matching public cloud buckets found", "cloud-none",
            f"Tried {len(names)} guessed names on AWS S3 and Google Cloud Storage.",
            "None of the common bucket names tied to this domain are open to the public.",
        ))
    return results
