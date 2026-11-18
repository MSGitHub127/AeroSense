"""FastAPI sub-routers for AeroSense."""
from __future__ import annotations

from app.routers.advisory import router as advisory_router
from app.routers.alternatives import router as alternatives_router
from app.routers.consultation import router as consultation_router
from app.routers.iaq import router as iaq_router
from app.routers.impact import router as impact_router
from app.routers.routines import router as routines_router
from app.routers.session import router as session_router

__all__ = [
    "advisory_router",
    "alternatives_router",
    "consultation_router",
    "iaq_router",
    "impact_router",
    "routines_router",
    "session_router",
]
