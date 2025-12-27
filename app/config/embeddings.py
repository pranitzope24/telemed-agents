"""Embeddings config placeholder."""
import logging

from langchain_openai import OpenAIEmbeddings

from ..constants.openai_constants import EmbeddingModels
from ..utils.logger import get_logger

logger = get_logger() or logging.getLogger(__name__)

class EmbeddingsConfig:
    """Embeddings configuration class.
    Usage: 
        embeddings_config = EmbeddingsConfig()
        model = embeddings_config.get_model()
    """

    def __init__(self, model_name: str = EmbeddingModels.TEXT_EMBEDDING_3_SMALL.value):
        self.model_name = model_name

    def get_model(self) -> str:
        """Returns the embedding model name."""
        logger.info("OpenAIEmbeddings client initialised with model '%s'", self.model_name)
        return OpenAIEmbeddings(model=self.model_name)
    
