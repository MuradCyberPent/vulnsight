"""Input for starting a scan. (Member 1)"""
from typing import Literal, Optional

from pydantic import BaseModel, Field


class ScanCreate(BaseModel):
    target: str = Field(min_length=1, max_length=255)
    profile: Literal["quick", "full", "web-only"] = "quick"
    ports: Optional[str] = Field(default=None, max_length=200)  # e.g. "22,80,443" or "1-1024"
    authorized: bool = False  # scope guard: "I own this target or have permission"
