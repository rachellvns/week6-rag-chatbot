import hashlib
from pathlib import Path
from qdrant_client import QdrantClient, models
from chunker import chunk
from config import EMBEDDING_MODEL, QDRANT_PATH, COLLECTION_NAME

def stable_id(path: str, i: int) -> int:
    h = hashlib.md5(f"{path}:{i}".encode()).hexdigest()
    return int(h[:12], 16)

client = QdrantClient(path="./qdrant_data")

if not client.collection_exists(COLLECTION_NAME):
    client.create_collection(
        COLLECTION_NAME,
        vectors_config=models.VectorParams(
            size=client.get_embedding_size(EMBEDDING_MODEL),
            distance=models.Distance.COSINE,
        ),
    )

docs, meta, ids = [], [], []
for p in sorted(Path("corpus").glob("*.*")):
    text = p.read_text(errors="ignore")
    for i, ch in enumerate(chunk(text)):
        docs.append(ch)
        meta.append({"source": p.name, "chunk": i, "text": ch})
        ids.append(stable_id(p.name,i))

points = [
    models.PointStruct(
        id=ids[i], vector=models.Document(text=docs[i], model=EMBEDDING_MODEL),payload=meta[i],
    )
    for i in range(len(docs))
]
client.upsert(collection_name=COLLECTION_NAME, points=points)
print(f"ingested {len(docs)} chunks")