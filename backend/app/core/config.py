"""Settings, read from environment variables (and the .env file)."""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")


def _bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).strip().lower() in ("1", "true", "yes", "on")


class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", f"sqlite:///{(BASE_DIR / 'vulnsight.db').as_posix()}"
    )

    FRONTEND_URLS: list[str] = [
        u.strip()
        for u in os.getenv("FRONTEND_URLS", "http://localhost:5173").split(",")
        if u.strip()
    ]

    # Scope guard
    ALLOW_PRIVATE_TARGETS: bool = _bool("ALLOW_PRIVATE_TARGETS", False)
    MAX_CONCURRENT_SCANS: int = int(os.getenv("MAX_CONCURRENT_SCANS", "2"))
    MAX_CUSTOM_PORTS: int = 2000

    # Login protection
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_MINUTES: int = 15


settings = Settings()
