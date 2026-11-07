"""Table: scans (ER entity Scan)."""
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base, utcnow


class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    target = Column(String(255), nullable=False)
    resolved_ip = Column(String(64))
    profile = Column(String(20), nullable=False)
    ports_spec = Column(String(200))
    authorized = Column(Boolean, default=False, nullable=False)  # scope-guard confirmation
    status = Column(String(15), default="queued", nullable=False)  # queued/running/completed/failed
    progress_pct = Column(Integer, default=0, nullable=False)
    progress_text = Column(String(120), default="Queued")
    risk_score = Column(Integer, default=0, nullable=False)
    risk_level = Column(String(10), default="Low", nullable=False)
    error = Column(Text)
    started_at = Column(DateTime, default=utcnow, nullable=False)
    finished_at = Column(DateTime)

    owner = relationship("User", back_populates="scans")
    findings = relationship("Finding", back_populates="scan", cascade="all, delete-orphan")
