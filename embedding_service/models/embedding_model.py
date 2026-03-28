import os
import logging
from typing import List, Optional
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

MODEL_NAME = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")


class EmbeddingModel:
    def __init__(self):
        logger.info(f"Loading embedding model: {MODEL_NAME}")
        self.model = SentenceTransformer(MODEL_NAME)
        logger.info("Embedding model loaded successfully.")

    def encode(self, text: str) -> List[float]:
        """
        Encodes a text string into a 384-dimension embedding vector.
        Returns empty list if text is empty — callers must check before using.
        """
        if not text or not text.strip():
            logger.warning("encode() called with empty or whitespace text. Returning [].")
            return []

        encoded = self.model.encode(text.strip())
        return encoded.tolist() if hasattr(encoded, "tolist") else list(encoded)


# Lazy singleton — only instantiated when first accessed
_embedding_model: Optional[EmbeddingModel] = None


def get_embedding_model() -> EmbeddingModel:
    """
    Returns the singleton EmbeddingModel instance.
    Loads the model on first call, reuses it on subsequent calls.
    """
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = EmbeddingModel()
    return _embedding_model