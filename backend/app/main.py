"""VulnSight API: run with  uvicorn app.main:app --reload

This file only wires things together. The real features live in app/modules/:
  users     Module 1  User Management and Security
  scanning  Module 2  Vulnerability Scanning Engine
  analysis  Module 3  Analysis, Reporting and Dashboard
Every module is found automatically (see core/discovery.py).
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, SessionLocal, engine, utcnow
from app.core.discovery import load_modules
from app.core.models import Scan


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)  # create tables if they don't exist yet
    if settings.SECRET_KEY == "change-me":
        print("WARNING: SECRET_KEY is the default. Set a real one in backend/.env before deploying!")
    # Scans that were running when the server stopped can never finish: mark them failed.
    db = SessionLocal()
    try:
        for s in db.query(Scan).filter(Scan.status.in_(["queued", "running"])).all():
            s.status, s.error, s.finished_at = "failed", "Server restarted during the scan.", utcnow()
        db.commit()
    finally:
        db.close()
    yield


app = FastAPI(title="VulnSight API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.FRONTEND_URLS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)


@app.get("/api/health", tags=["system"])
def health():
    return {"status": "ok"}


load_modules(app)
