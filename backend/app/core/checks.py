"""Registry of scan checks.

Every check file in modules/scanning/checks/ registers itself with @register_check,
so the scan runner finds it automatically (nobody has to edit a shared list).
"""
CHECKS: dict[str, dict] = {}


def register_check(name: str, label: str, order: int):
    def decorator(func):
        CHECKS[name] = {"label": label, "order": order, "run": func}
        return func
    return decorator


def ordered_checks() -> list[str]:
    """Names of all registered checks, in the order they run."""
    return [name for name, _ in sorted(CHECKS.items(), key=lambda item: item[1]["order"])]
