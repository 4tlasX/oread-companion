"""
Self-contained configuration for the inference service.
No dependencies on backend code.
"""
import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

# Load .env file from the inference directory
ENV_FILE = Path(__file__).parent / ".env"
load_dotenv(ENV_FILE)


class InferenceConfig:
    """Configuration for the inference service with proper path resolution."""

    def __init__(self):
        # Project root is parent of inference directory
        self.project_root = Path(__file__).resolve().parent.parent

        # Server settings
        self.host = os.getenv("INFERENCE_HOST", "127.0.0.1")
        self.port = int(os.getenv("INFERENCE_PORT", "9001"))
        self.reload = os.getenv("RELOAD", "false").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", "INFO").lower()

        # Model paths - resolve relative to project root
        llm_path_str = os.getenv("LLM_MODEL_PATH", "models/MN-Violet-Lotus-12B-Q4_K_M.gguf")
        emotion_path_str = os.getenv("EMOTION_MODEL_PATH", "models/roberta_emotions_onnx")
        memory_path_str = os.getenv("MEMORY_PERSIST_DIR", "data/memory")

        self.llm_model_path = self._resolve_path(llm_path_str)
        self.emotion_model_path = self._resolve_path(emotion_path_str)
        self.memory_persist_dir = self._resolve_path(memory_path_str)

        # LLM settings
        self.llm_n_gpu_layers = int(os.getenv("LLM_N_GPU_LAYERS", "-1"))
        self.llm_n_ctx = int(os.getenv("LLM_N_CTX", "10000"))
        self.llm_n_batch = int(os.getenv("LLM_N_BATCH", "1024"))
        self.llm_n_threads = int(os.getenv("LLM_N_THREADS", "8"))

        # Memory management settings
        self.llm_use_mmap = os.getenv("LLM_USE_MMAP", "true").lower() == "true"
        self.llm_use_mlock = os.getenv("LLM_USE_MLOCK", "false").lower() == "true"

        # Response cleaning settings
        self.min_response_length = int(os.getenv("MIN_RESPONSE_LENGTH", "3"))
        self.enable_fallback_cleaning = os.getenv("ENABLE_FALLBACK_CLEANING", "true").lower() == "true"

        # CORS settings
        allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:9000,http://localhost:3000")
        self.allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]

        # Inference port for backend-node to connect
        self.inference_port = self.port

    def _resolve_path(self, path_str: str) -> str:
        """
        Resolve model path relative to project root.
        Handles both absolute and relative paths.
        """
        path = Path(path_str)

        # If already absolute, use as-is
        if path.is_absolute():
            return str(path)

        # Otherwise, resolve relative to project root
        resolved = (self.project_root / path).resolve()
        return str(resolved)

    def validate(self) -> bool:
        """Validate configuration and check if model files exist."""
        issues = []

        # Check LLM model
        llm_path = Path(self.llm_model_path)
        if not llm_path.exists():
            issues.append("LLM model not found")
            logger.warning("LLM model file does not exist")
        elif not llm_path.is_file():
            issues.append("LLM model path is not a file")

        # Check emotion model
        emotion_path = Path(self.emotion_model_path)
        if not emotion_path.exists():
            issues.append("Emotion model not found")
            logger.warning("Emotion model directory does not exist")
            logger.warning("Will fall back to online model download (requires internet)")
        elif not emotion_path.is_dir():
            issues.append("Emotion model path is not a directory")

        # Check port range
        if not (1024 <= self.port <= 65535):
            issues.append(f"Invalid port number: {self.port}")

        # Check GPU layers
        if self.llm_n_gpu_layers < -1:
            issues.append(f"Invalid GPU layers value: {self.llm_n_gpu_layers}")

        # Log validation results
        if issues:
            logger.error("Configuration validation issues:")
            for issue in issues:
                logger.error(f"  - {issue}")
            # Don't fail on missing models, just warn
            # This allows the service to start with fallback models
            return True

        logger.info("Configuration validation passed")
        return True

    def print_config(self):
        """Print configuration for debugging."""
        logger.info("=" * 60)
        logger.info("Inference Service Configuration")
        logger.info("=" * 60)
        logger.info(f"Host: {self.host}")
        logger.info(f"Port: {self.port}")
        logger.info(f"LLM Model: {'Loaded' if Path(self.llm_model_path).exists() else 'Not found'}")
        logger.info(f"Emotion Model: {'Loaded' if Path(self.emotion_model_path).exists() else 'Not found'}")
        logger.info(f"GPU Layers: {self.llm_n_gpu_layers}")
        logger.info(f"Context Size: {self.llm_n_ctx}")
        logger.info(f"Batch Size: {self.llm_n_batch}")
        logger.info(f"Threads: {self.llm_n_threads}")
        logger.info(f"CORS Origins: {self.allowed_origins}")
        logger.info("=" * 60)


# Singleton instance
config = InferenceConfig()