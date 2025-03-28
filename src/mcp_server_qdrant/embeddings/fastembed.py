import asyncio
from typing import List

from fastembed import TextEmbedding

from mcp_server_qdrant.embeddings.base import EmbeddingProvider


class FastEmbedProvider(EmbeddingProvider):
    """
    FastEmbed implementation of the embedding provider.
    :param model_name: The name of the FastEmbed model to use.
    """

    def __init__(self, model_name: str):
        self.model_name = model_name
        self.embedding_model = None

    async def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """Embed a list of documents into vectors."""
        self.embedding_model = self.embedding_model or TextEmbedding(self.model_name)

        # Run in a thread pool since FastEmbed is synchronous
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            None, lambda: list(self.embedding_model.passage_embed(documents))
        )
        return [embedding.tolist() for embedding in embeddings]

    async def embed_query(self, query: str) -> List[float]:
        """Embed a query into a vector."""
        self.embedding_model = self.embedding_model or TextEmbedding(self.model_name)
        # Run in a thread pool since FastEmbed is synchronous
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            None, lambda: list(self.embedding_model.query_embed([query]))
        )
        return embeddings[0].tolist()

    def get_vector_name(self) -> str:
        """
        Return the name of the vector for the Qdrant collection.
        Important: This is compatible with the FastEmbed logic used before 0.6.0.
        """
        self.embedding_model = self.embedding_model or TextEmbedding(self.model_name)
        model_name = self.embedding_model.model_name.split("/")[-1].lower()
        return f"fast-{model_name}"
