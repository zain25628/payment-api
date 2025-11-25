# Refactored by Copilot
# Refactored by Copilot – Health Feature
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config import settings
from app.db.session import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    """Return a small health payload for monitoring and uptime checks.

    The response includes the service name and version from application settings.
    """
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
    }



@router.get("/health/db")
def health_check_db(db: Session = Depends(get_db)):
    """
    Basic database connectivity check.
    Attempts a trivial query to ensure the DB connection is alive.
    """
    try:
        db.execute("SELECT 1")
    except Exception:
        return {"status": "error", "database": "unreachable"}
    return {"status": "ok", "database": "reachable"}
