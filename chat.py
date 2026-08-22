from rag import answer

last_hits = []
while True:
    q = input("you> ").strip()
    if q == "/quit": break
    if q == "/sources":
        for i, h in enumerate(last_hits):
            print(f"[{i+1}] {h.metadata['source']} "
                  f"#{h.metadata['chunk']} score={h.score:.3f}")
            print("     ", h.document[:120], "\n")
            continue
    reply, last_hits=answer(q)
    print("bot> ", reply)