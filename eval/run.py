# eval/run.py — python eval/run.py --config baseline
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
import argparse
from rag import client, COLLECTION_NAME, EMBEDDING_MODEL, answer, retrieve
from metrics import hit_at_k, mean_reciprocal_rank
from judge import judge

REFUSAL = "I don't have that in the knowledge base."


def load_jsonl(path):
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def ctx_of(hits):
    return "\n\n".join(
        f"[{i+1}] ({h.payload['source']} #{h.payload['chunk']})\n{h.payload['text']}"
        for i, h in enumerate(hits)
    )

def print_scorecard(rows):
    n = len(rows)
    answerable_rows = [r for r in rows if not r["is_refusal_case"]]

    hit3 = sum(r["hit3"] for r in answerable_rows) / len(answerable_rows)
    mrr = sum(r["rr"] for r in answerable_rows) / len(answerable_rows)
    faithful = sum(r["faithful"] for r in rows) / n  # faithfulness still applies to all rows, including refusals

    print(f"hit@3: {hit3:.2f}  MRR: {mrr:.2f}  faithful: {faithful:.2f}  (n={n}, answerable={len(answerable_rows)})")
    print("\nFailures:")
    for r in rows:
        if (not r["is_refusal_case"] and not r["hit3"]) or not r["faithful"] or not r["refusal_ok"]:
            print(f"  - {r['q']}  (hit3={r['hit3']} faithful={r['faithful']} refusal_ok={r['refusal_ok']} refusal_case={r['is_refusal_case']})")

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="baseline")
    args = parser.parse_args()
    config = args.config

    rows = []
    for case in load_jsonl("eval/golden.jsonl"):
        hits = retrieve(case["q"])
        got = [f"{h.payload['source']}:{h.payload['chunk']}" for h in hits]
        ans, _ = answer(case["q"])
        is_refusal_case = case["reference"] == "REFUSE"
        rows.append({
            "q": case["q"],
            "hit3": hit_at_k(got, case["relevant"]),
            "rr": mean_reciprocal_rank(got, case["relevant"]),
            "faithful": judge(ans, ctx_of(hits)).faithful,
            "refusal_ok": (REFUSAL in ans) == is_refusal_case,
            "is_refusal_case": is_refusal_case,
        })

    print_scorecard(rows)
    save_json(f"eval/results-{config}.json", rows)