"""HTTP API routes."""

import logging

from fastapi import APIRouter

from config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
def read_root():
    """Root endpoint."""
    logger.debug("Root endpoint called")
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "healthy",
        "environment": settings.environment,
    }

@router.get("/health")
def health():
    return {
        "status": "okay"
    }
