import asyncio
from functools import cache

from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """Build embeddings with a process-cached model."""

    def __init__(self, model_name: str) -> None:
        """Configure the embedding model."""
        self.model_name = model_name

    @staticmethod
    @cache
    def _load_model(model_name: str) -> SentenceTransformer:
        """Load and cache the embedding model."""
        model: SentenceTransformer = SentenceTransformer(
            model_name_or_path=model_name,
        )
        return model

    def initialize(self) -> None:
        """Load the model once for the current process."""
        self._load_model(self.model_name)

    async def embed_query(self, text: str) -> list[float]:
        """Build a normalized vector for a user query."""
        model = self._load_model(self.model_name)
        vector = await asyncio.to_thread(
            model.encode,
            f"query: {text}",
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        return [float(value) for value in vector]

    async def embed_passages(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """Build normalized vectors for indexed questions."""
        model = self._load_model(self.model_name)
        vectors = await asyncio.to_thread(
            model.encode,
            [f"passage: {text}" for text in texts],
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        return [[float(value) for value in vector] for vector in vectors]
