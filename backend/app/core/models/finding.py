"""Table: findings (ER entity Finding)."""
from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class Finding(Base):
    __tablename__ = "findings"

    id = Column(Integer, primary_key=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), index=True, nullable=False)
    category = Column(String(40), nullable=False)
    severity = Column(String(10), nullable=False)  # Critical/High/Medium/Low/Info
    title = Column(String(255), nullable=False)
    key = Column(String(120), nullable=False)  # stable id, used to compare scans
    details = Column(Text, default="")
    explanation = Column(Text, default="")  # plain-English (beginner mode)
    fix = Column(Text, default="")

    scan = relationship("Scan", back_populates="findings")
