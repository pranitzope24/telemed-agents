from enum import Enum


class OpenaiModels(Enum):
    """Enum for OpenAI models."""

    GPT_4O = "gpt-4o"
    GPT_4_1 = "gpt-4.1"
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_5 = "gpt-5"

class EmbeddingModels(Enum):
    """Enum for Embedding models."""

    TEXT_EMBEDDING_3_SMALL = "text-embedding-3-small"
    TEXT_EMBEDDING_3_LARGE = "text-embedding-3-large"