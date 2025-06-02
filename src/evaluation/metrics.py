"""Quality metrics for GenAI outputs."""

from typing import List, Optional


def answer_relevance(question: str, answer: str) -> float:
    """Simple keyword overlap relevance score."""
    q_words = set(question.lower().split()) - {"what", "how", "why", "is", "the", "a"}
    a_words = set(answer.lower().split())
    if not q_words:
        return 0.0
    return len(q_words & a_words) / len(q_words)


def output_length_check(output: str, min_tokens: int = 10, max_tokens: int = 2000) -> bool:
    tokens = len(output.split())
    return min_tokens <= tokens <= max_tokens


def format_compliance(output: str, required_sections: Optional[List[str]] = None) -> float:
    if not required_sections:
        return 1.0
    found = sum(1 for s in required_sections if s.lower() in output.lower())
    return found / len(required_sections)
