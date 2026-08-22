from anthropic import Anthropic
from qdrant_client import QdrantClient, models
from config import API_KEY, BASE_URL, MODEL, EMBEDDING_MODEL, QDRANT_PATH, COLLECTION_NAME

client = QdrantClient(path=QDRANT_PATH)
llm = Anthropic(api_key=API_KEY, base_url=BASE_URL)

SYSTEM = ("Answer ONLY from the numbered sources provided."
          "Cite like [1] or [2] [3] after each claim."
          "If the sources do not contain the answer, reply exactly: "
          "'I dont have that in the knowledge base.'"
          "Never use outside knowledge.")

def answer(q: str, doc_type: str | None = None) -> tuple[str, list]:
    query_filter = None
    if doc_type:
        query_filter = models.Filter(
            must=[models.FieldCondition(key="doc_type", match=models.MatchValue(value=doc_type))]
        )
        
    hits = client.query_points(
        collection_name=COLLECTION_NAME,
        query=models.Document(text=q, model=EMBEDDING_MODEL),
        query_filter=query_filter,
        limit=5,
    ).points
    
    context = "\n\n".join(
        f"[{i+1}] ({h.payload['source']} #{h.payload['chunk']})"
        f"\n{h.payload['text']}"
        for i, h in enumerate(hits)
    )
    response = llm.messages.create(
        model=MODEL,
        max_tokens=700,
        system=SYSTEM,
        messages=[{"role": "user", "content": f"Sources:\n{context}\n\nQuestion: {q}"}],
    )
    reply = response.content[0].text
    return reply, hits

if __name__ == "__main__":

    reply, hits = answer(q= "What increases a person's risk of developing this condition?",
        doc_type="condition_overview")
    print(reply)
    for i, h in enumerate(hits):
        print(f"[{i+1}] {h.payload['source']} #{h.payload['doc_type']}")