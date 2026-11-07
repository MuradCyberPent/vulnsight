"""Import every table here so SQLAlchemy knows about all of them (and their relationships)."""
from .user import User
from .scan import Scan
from .finding import Finding

__all__ = ["User", "Scan", "Finding"]
