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

def answer(q: str) -> tuple[str, list]:
    hits = client.query_points(
        collection_name=COLLECTION_NAME,
        query=models.Document(text=q, model=EMBEDDING_MODEL),
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
    question = "What blood pressure reading defines Stage 2 hypertension?"

    reply, hits = answer(question)
    print(f"Q: {question}\n")
    print(reply)
    print("---")
    for i, h in enumerate(hits):
        print(f"[{i+1}] {h.payload['source']} #{h.payload['chunk']}")
        print(h.payload['text'][:200], "...")
        print()