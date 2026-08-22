import hashlib
from pathlib import Path
from qdrant_client import QdrantClient, models
from chunker import chunk
from config import EMBEDDING_MODEL, QDRANT_PATH, COLLECTION_NAME

DOC_TYPE_BY_FILE = {
    "type2-diabetes-overview.md": "condition_overview",
    "asthma-overview.md": "condition_overview",
    "ckd-overview.md": "condition_overview",
    "hypertension-guideline.md": "treatment_guideline",
    "migraine-guideline.md": "treatment_guideline",
    "depression-anxiety-screening-guideline.md": "treatment_guideline",
    "knee-replacement-patient-education.md": "patient_education",
    "cardiovascular-nutrition.md": "patient_education",
    "adult-vaccination-patient-education.md": "patient_education",
    "antibiotic-resistance-summary.md": "clinical_summary",
}

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

# for chunk-size shootout task
# if client.collection_exists(COLLECTION_NAME):
#     client.delete_collection(COLLECTION_NAME)
# client.create_collection(
#     COLLECTION_NAME,
#     vectors_config=models.VectorParams(
#         size=client.get_embedding_size(EMBEDDING_MODEL),
#         distance=models.Distance.COSINE,
#     ),
# )

docs, meta, ids = [], [], []
for p in sorted(Path("corpus").glob("*.*")):
    text = p.read_text(errors="ignore")
    for i, ch in enumerate(chunk(text)):
        docs.append(ch)
        meta.append({"source": p.name, "chunk": i, "text": ch, "doc_type": DOC_TYPE_BY_FILE.get(p.name, "unknown"),
                     })
        ids.append(stable_id(p.name,i))

points = [
    models.PointStruct(
        id=ids[i], vector=models.Document(text=docs[i], model=EMBEDDING_MODEL),payload=meta[i],
    )
    for i in range(len(docs))
]
client.upsert(collection_name=COLLECTION_NAME, points=points)
print(f"ingested {len(docs)} chunks")