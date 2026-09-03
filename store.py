# store.py
from qdrant_client import models
from config import EMBEDDING_MODEL
from rag import client  # ← reuse the single client instance, don't create a new one

HYBRID_COLLECTION_NAME = "corpus_hybrid"
BM25_MODEL = "Qdrant/bm25"


def ensure_hybrid(name: str = HYBRID_COLLECTION_NAME) -> None:
    if client.collection_exists(name):
        return
    client.create_collection(
        name,
        vectors_config={
            "dense": models.VectorParams(
                size=client.get_embedding_size(EMBEDDING_MODEL),
                distance=models.Distance.COSINE,
            )
        },
        sparse_vectors_config={
            "bm25": models.SparseVectorParams(modifier=models.Modifier.IDF)
        },
    )


def retrieve_hybrid(q: str, doc_type: str | None = None, limit: int = 5):
    query_filter = None
    if doc_type:
        query_filter = models.Filter(
            must=[models.FieldCondition(key="doc_type", match=models.MatchValue(value=doc_type))]
        )
    return client.query_points(
        HYBRID_COLLECTION_NAME,
        prefetch=[
            models.Prefetch(
                query=models.Document(text=q, model=EMBEDDING_MODEL),
                using="dense",
                limit=20,
            ),
            models.Prefetch(
                query=models.Document(text=q, model=BM25_MODEL),
                using="bm25",
                limit=20,
            ),
        ],
        query=models.FusionQuery(fusion=models.Fusion.RRF),
        query_filter=query_filter,
        limit=limit,
    ).points