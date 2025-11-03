"""
Health Check Routes
Simple health and readiness endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> Dict[str, str]:
    """Simple health check"""
    return {"status": "healthy"}


@router.get("/ready")
async def ready_check(
    llm_processor=None,
    emotion_detector=None
) -> Dict[str, Any]:
    """
    Readiness check - verifies all components are initialized

    NOTE: Dependencies must be injected by main.py
    """
    status = {
        "llm": llm_processor is not None and llm_processor.initialized,
        "emotion": emotion_detector is not None and emotion_detector.initialized
    }

    if not status["llm"]:
        raise HTTPException(status_code=503, detail="LLM not initialized")
    if not status["emotion"]:
        raise HTTPException(status_code=503, detail="Emotion detector not initialized")

    return {
        "status": "ready",
        "components": status
    }
