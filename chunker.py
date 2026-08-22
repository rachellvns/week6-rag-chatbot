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

from pathlib import Path

corpus = Path("corpus")

documents = list(corpus.glob("*.md"))

longest = max(
    documents,
    key=lambda p: len(p.read_text(encoding="utf-8"))
)

text = longest.read_text(encoding="utf-8")
chunks = chunk(text)

print(f"Longest document: {longest.name}")
print(f"Chunk count: {len(chunks)}")
print()

# for i, c in enumerate(chunks, 1):
#     tokens = tok_len(c)
#     first_line = c.splitlines()[0]

#     print(f"Chunk {i}: {tokens} tokens | {first_line}")

#     assert tokens >= 50, f"Chunk {i} is too small: {tokens} tokens"
#     assert tokens <= 500, f"Chunk {i} is too large: {tokens} tokens"

# print("\nAll chunks passed the sanity check.")