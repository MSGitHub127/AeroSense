"""FastAPI application entrypoint for AeroSense Urban Air Quality Assistant."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.db import init_db
from app.exceptions import (
    AeroSenseBaseException,
    AQICalculationError,
    ProfileNotFoundError,
    RecommendationGenerationError,
    SecurityValidationError,
)
from app.routers import (
    advisory_router,
    alternatives_router,
    consultation_router,
    iaq_router,
    impact_router,
    routines_router,
    session_router,
)
from app.security import TokenBucketRateLimiter

logger = logging.getLogger("aerosense")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle hook to initialize database schemas and caches."""
    init_db()
    logger.info("AeroSense application initialized successfully.")
    yield


app = FastAPI(
    title="AeroSense",
    description="GenAI-powered Urban Air Quality Assistant helping families navigate winter smog.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

settings = get_settings()

# GZip Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory Token Bucket Rate Limiter
rate_limiter = TokenBucketRateLimiter(rate=50.0, capacity=100.0)


@app.middleware("http")
async def security_and_rate_limit_middleware(request: Request, call_next):
    """Enforce rate limits and inject strict HTTP security headers."""
    client_ip = request.client.host if request.client else "unknown"

    # Bypass rate limits for static assets and health checks
    path = request.url.path
    if not (path.startswith("/static") or path == "/health" or path == "/"):
        if not rate_limiter.consume(client_ip):
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"error": "RateLimitExceeded", "detail": "Rate limit exceeded. Please try again shortly."},
            )

    response: Response = await call_next(request)

    # Security Headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "script-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "font-src 'self' data:;"
    )

    return response


# --- Global Exception Handlers ---


@app.exception_handler(ProfileNotFoundError)
async def profile_not_found_handler(request: Request, exc: ProfileNotFoundError):
    """Handle missing profile lookups."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": "ProfileNotFound", "detail": str(exc)},
    )


@app.exception_handler(SecurityValidationError)
async def security_validation_handler(request: Request, exc: SecurityValidationError):
    """Handle security red-line infractions."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "SecurityValidationError", "detail": str(exc)},
    )


@app.exception_handler(AQICalculationError)
async def aqi_calculation_handler(request: Request, exc: AQICalculationError):
    """Handle air quality calculation discrepancies."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": "AQICalculationError", "detail": str(exc)},
    )


@app.exception_handler(RecommendationGenerationError)
async def recommendation_error_handler(request: Request, exc: RecommendationGenerationError):
    """Handle recommendation pipeline failures."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "RecommendationGenerationError", "detail": str(exc)},
    )


@app.exception_handler(AeroSenseBaseException)
async def aerosense_base_handler(request: Request, exc: AeroSenseBaseException):
    """Catch-all for domain exceptions."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": exc.__class__.__name__, "detail": str(exc)},
    )


# --- Sub-Routers Mount ---
app.include_router(session_router)
app.include_router(advisory_router)
app.include_router(routines_router)
app.include_router(iaq_router)
app.include_router(alternatives_router)
app.include_router(impact_router)
app.include_router(consultation_router)


# --- Static and Web Views ---

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "app" / "static"
FRONTEND_DIR = BASE_DIR / "frontend"

if STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/health", tags=["Health"], summary="Health check probe")
def health_check() -> dict[str, str]:
    """Liveness probe reporting application status."""
    return {
        "status": "healthy",
        "service": "AeroSense",
        "version": "1.0.0",
        "provider": settings.llm_provider,
    }


@app.get("/", summary="Serve primary AeroSense web application", include_in_schema=False)
def index_page():
    """Serve the single-page accessible web interface."""
    frontend_index = FRONTEND_DIR / "index.html"
    if frontend_index.is_file():
        return FileResponse(str(frontend_index))

    static_index = STATIC_DIR / "index.html"
    if static_index.is_file():
        return FileResponse(str(static_index))

    return JSONResponse(
        content={
            "service": "AeroSense",
            "message": "Welcome to AeroSense Urban Air Quality Assistant API. Visit /docs for OpenAPI documentation.",
        }
    )
