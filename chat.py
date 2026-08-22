from rag import answer

last_hits = []
while True:
    q = input("you> ").strip()
    if q == "/quit":
        break
    if q == "/sources":
        for i, h in enumerate(last_hits):
            print(f"[{i+1}] {h.payload['source']} "
                  f"#{h.payload['chunk']} score={h.score:.3f}")
            print("     ", h.payload['text'][:120], "\n")
        continue
    reply, last_hits = answer(q)
    print("bot>", reply)