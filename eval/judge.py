from pydantic import BaseModel
from rag import call_llm

class Verdict(BaseModel):
    faithful: bool
    unsupported: list[str] = []
    
JUDGE = ("You are a strict grader. Given SOURCES and an"
 " ANSWER, list every claim in the answer NOT supported"
 " by the sources. Respond ONLY with JSON matching:"
 ' {"faithful": bool, "unsupported": [string]}')

def judge(answer: str, ctx: str) -> Verdict:
    raw = call_llm(system="".join(JUDGE), temperature=0,
                   user=f"SOURCES:\n{ctx}\n\nANSWER:\n{answer}",
                   max_tokens=2000)
    return Verdict.model_validate_json(raw)