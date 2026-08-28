# calculate hit@k
# formula sum of (0 || 1) / number of questions
# the purpose of calculating hit@k is to know whether the answer is hitting the corresponding chunk or not
def hit_at_k(got: list[str], relevant: list[str],
             k: int = 3) -> bool:
    return any(r in got[:k] for r in relevant)

# calculate MRR
# formula sum of (1/rank) / number of questions
# the purpose of calculating MRR is to know how deep does the program needs to "surf" through the incorrect chunk to finally found one (if there is any)
def mean_reciprocal_rank(got: list[str], relevant: list[str]) -> float:
    for i, g in enumerate(got):
        if g in relevant:
            return 1 / (i+1)
        return 0.0