# ingest_hybrid.py
import hashlib
from pathlib import Path
from qdrant_client import models
from chunker import chunk
from config import EMBEDDING_MODEL, DOC_TYPE_BY_FILE
from store import client, ensure_hybrid, HYBRID_COLLECTION_NAME, BM25_MODEL


def stable_id(path: str, i: int) -> int:
    h = hashlib.md5(f"{path}:{i}".encode()).hexdigest()
    return int(h[:12], 16)


ensure_hybrid()

points = []
for p in sorted(Path("corpus").glob("*.*")):
    text = p.read_text(errors="ignore")
    for i, ch in enumerate(chunk(text)):
        points.append(models.PointStruct(
            id=stable_id(p.name, i),
            vector={
                "dense": models.Document(text=ch, model=EMBEDDING_MODEL),
                "bm25": models.Document(text=ch, model=BM25_MODEL),
            },
            payload={
                "source": p.name,
                "chunk": i,
                "text": ch,
                "doc_type": DOC_TYPE_BY_FILE.get(p.name, "unknown"),
            },
        ))

client.upsert(collection_name=HYBRID_COLLECTION_NAME, points=points)
print(f"ingested {len(points)} chunks into {HYBRID_COLLECTION_NAME}")