import re

# Keyword screen for crisis language. This is a coarse safety net, not a
# clinical risk assessment: it errs toward flagging (negations still match).
CRISIS_PATTERNS = [
    r"\bkill(?:ing)? myself\b",
    r"\bsuicid(?:e|al)\b",
    r"\bend(?:ing)? (?:it all|my life)\b",
    r"\b(?:want|wanted|going) to die\b",
    r"\bself[- ]?harm",
    r"\b(?:hurt|hurting|cut|cutting) myself\b",
    r"\bno reason to (?:live|go on)\b",
    r"\bbetter off dead\b",
]

_CRISIS_RE = re.compile("|".join(CRISIS_PATTERNS), re.IGNORECASE)


def detect_crisis_language(text: str) -> bool:
    return _CRISIS_RE.search(text) is not None
