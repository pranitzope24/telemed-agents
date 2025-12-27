"""Embeddings config placeholder."""
from langchain_openai import OpenAIEmbeddings

from ..constants.openai_constants import EmbeddingModels


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
        return OpenAIEmbeddings(model=self.model_name)
    
