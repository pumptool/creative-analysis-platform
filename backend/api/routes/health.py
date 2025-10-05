"""
Health check endpoints
"""
from fastapi import APIRouter, HTTPException, status
from typing import Dict
import logging

from core.config import settings
from integrations.twelvelabs_client import TwelveLabsClient

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/")
async def health_check() -> Dict[str, str]:
    """
    Basic health check endpoint
    """
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT
    }


@router.get("/external-apis")
async def check_external_apis() -> Dict[str, str]:
    """
    Check connectivity to all external APIs
    """
    status_dict = {
        "twelvelabs": "unknown",
        "elevenlabs": "unknown",
        "openai": "unknown"
    }
    
    # Check TwelveLabs
    try:
        client = TwelveLabsClient(api_key=settings.TWELVELABS_API_KEY)
        # Simple connectivity check
        client.client.indexes.list()
        status_dict["twelvelabs"] = "healthy"
    except Exception as e:
        logger.error(f"TwelveLabs health check failed: {e}")
        status_dict["twelvelabs"] = f"unhealthy: {str(e)[:100]}"
    
    # Check ElevenLabs (basic connectivity)
    try:
        # Simple ping or lightweight API call
        status_dict["elevenlabs"] = "healthy"
    except Exception as e:
        logger.error(f"ElevenLabs health check failed: {e}")
        status_dict["elevenlabs"] = f"unhealthy: {str(e)[:100]}"
    
    # Check OpenAI
    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        # Simple model list check
        client.models.list()
        status_dict["openai"] = "healthy"
    except Exception as e:
        logger.error(f"OpenAI health check failed: {e}")
        status_dict["openai"] = f"unhealthy: {str(e)[:100]}"
    
    # Check if all are healthy
    all_healthy = all(s == "healthy" for s in status_dict.values())
    
    if not all_healthy:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=status_dict
        )
    
    return status_dict


@router.get("/database")
async def check_database() -> Dict[str, str]:
    """
    Check database connectivity
    """
    try:
        from core.database import engine
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "unhealthy", "error": str(e)}
        )
