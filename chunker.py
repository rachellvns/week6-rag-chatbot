from pathlib import Path
corpus = Path("corpus")
    
def tok_len(s: str) -> int:
    return max(1, len(s)//4)

def chunk(text: str, max_tokens: int = 350, overlap: int=50) -> list[str]:
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    buf = ""
    for p in paras:
        if buf and tok_len(buf) + tok_len(p) > max_tokens:
            chunks.append(buf.strip())
            buf = buf[-overlap * 4:]
        buf += "\n\n" + p
    if buf.strip():
        chunks.append(buf.strip())
    return chunks


if __name__ == "__main__":
    # change this line to inspect different file
    target = corpus / "hypertension-guideline.md"

    text = target.read_text(encoding="utf-8")
    chunks = chunk(text)

    print(f"Document: {target.name}")
    print(f"Chunk count: {len(chunks)}\n")

    for i, c in enumerate(chunks):
        tokens = tok_len(c)
        print(f"--- {target.name}:{i} ({tokens} tokens) ---")
        print(c)
        print()