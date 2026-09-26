from functools import lru_cache
from pathlib import Path
from typing import Any

from app.config.settings import settings


@lru_cache(maxsize=1)
def get_embedding_model():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(settings.embedding_model)


@lru_cache(maxsize=1)
def get_qdrant_client():
    from qdrant_client import QdrantClient

    path = Path(settings.qdrant_path)
    if not path.is_absolute():
        path = Path(__file__).resolve().parents[2] / path
    path.mkdir(parents=True, exist_ok=True)
    return QdrantClient(path=str(path))


def ensure_collection() -> None:
    from qdrant_client.models import Distance, VectorParams

    client = get_qdrant_client()
    if not client.collection_exists(settings.qdrant_collection):
        dimension = get_embedding_model().get_sentence_embedding_dimension()
        client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=VectorParams(size=dimension, distance=Distance.COSINE),
        )


def index_chunks(chunks: list[dict[str, Any]]) -> int:
    from qdrant_client.models import PointStruct

    if not chunks:
        return 0
    ensure_collection()
    vectors = get_embedding_model().encode(
        [chunk["content"] for chunk in chunks],
        normalize_embeddings=True,
    )
    points = [
        PointStruct(
            id=chunk["id"],
            vector=vector.tolist(),
            payload={
                "document_id": chunk["document_id"],
                "chunk_id": chunk["id"],
                "chunk_index": chunk["chunk_index"],
                "content": chunk["content"],
                "title": chunk.get("title"),
                "law_type": chunk.get("law_type"),
            },
        )
        for chunk, vector in zip(chunks, vectors)
    ]
    get_qdrant_client().upsert(collection_name=settings.qdrant_collection, points=points)
    return len(points)


def search_chunks(query: str, limit: int = 5) -> list[dict[str, Any]]:
    ensure_collection()
    vector = get_embedding_model().encode(query, normalize_embeddings=True).tolist()
    result = get_qdrant_client().query_points(
        collection_name=settings.qdrant_collection,
        query=vector,
        limit=limit,
        with_payload=True,
    )
    return [
        {"score": point.score, **(point.payload or {})}
        for point in result.points
    ]
