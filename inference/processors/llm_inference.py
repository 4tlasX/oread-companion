"""
LLM Inference Engine
Handles model loading and raw token generation
"""
from llama_cpp import Llama
from pathlib import Path
import logging
from typing import Optional, List

logger = logging.getLogger(__name__)


class LLMInference:
    """Core LLM model operations - loading and generation only"""

    def __init__(self, model_path: str, n_ctx: int = 4096,
                 n_threads: int = 4, n_gpu_layers: int = -1,
                 n_batch: int = 512):
        """
        Initialize LLM inference engine

        Args:
            model_path: Path to GGUF model file
            n_ctx: Context window size
            n_threads: CPU threads
            n_gpu_layers: GPU layers (-1 = all)
            n_batch: Batch size for prompt processing
        """
        self.model_path = Path(model_path)
        self.n_ctx = n_ctx
        self.n_threads = n_threads
        self.n_gpu_layers = n_gpu_layers
        self.n_batch = n_batch
        self.llm = None
        self.initialized = False

    async def initialize(self):
        """Load LLM model into memory"""
        try:
            logger.info("Loading LLM model...")

            if not self.model_path.exists():
                raise FileNotFoundError("Model file not found")

            # Optimized for Apple Silicon Metal GPU
            self.llm = Llama(
                model_path=str(self.model_path),
                n_ctx=self.n_ctx,
                n_threads=self.n_threads,
                n_gpu_layers=self.n_gpu_layers,
                n_batch=self.n_batch,
                use_mmap=True,
                use_mlock=False,  # Don't lock in RAM on macOS
                f16_kv=True,  # Use float16 for key/value cache (faster on Metal)
                logits_all=False,  # Only compute logits for last token
                vocab_only=False,
                verbose=False,
                flash_attn=True,  # Enable flash attention for 2-3x speedup on Metal
                offload_kqv=True  # Offload K/Q/V matrices to GPU for faster attention
            )

            self.initialized = True
            logger.info("✅ LLM model loaded successfully")

        except Exception as e:
            logger.error(f"❌ Failed to load LLM model: {e}", exc_info=True)
            self.initialized = False
            raise

    async def generate(self, prompt: str, max_tokens: int = 200,
                      temperature: float = 1.0, stop: Optional[List[str]] = None,
                      stream: bool = False):
        """
        Generate text from prompt (raw output, no cleaning)

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            stop: Stop sequences
            stream: Enable streaming

        Returns:
            Tuple of (generated_text, tokens_generated) or async generator if streaming
        """
        if not self.initialized:
            raise RuntimeError("LLM not initialized")

        try:
            result = self.llm(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.85,  # Reduced from 0.95 to prevent confabulation/hallucination
                top_k=40,  # Limit sampling candidates for faster generation
                repeat_penalty=1.15,  # Increased from 1.1 to reduce repetition
                stop=stop or [],
                stream=stream,
                echo=False,
                # Performance optimizations for speed
                min_p=0.05,  # Filter low-probability tokens early (faster sampling)
                tfs_z=1.0,  # Tail-free sampling
                mirostat_mode=0,  # Disable mirostat for maximum speed
                # Metal-specific optimizations
            )

            if stream:
                async def stream_generator():
                    for chunk in result:
                        text = chunk['choices'][0]['text']
                        yield text
                return stream_generator()
            else:
                generated_text = result['choices'][0]['text']
                # Extract token count from usage stats if available
                tokens_generated = len(generated_text.split())  # Approximate word count fallback
                if 'usage' in result and 'completion_tokens' in result['usage']:
                    tokens_generated = result['usage']['completion_tokens']

                return generated_text, tokens_generated

        except Exception as e:
            logger.error(f"Generation failed: {e}", exc_info=True)
            raise
