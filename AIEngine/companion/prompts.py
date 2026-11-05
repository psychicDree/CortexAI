import re
from typing import Dict, List, Sequence

from question_bank import Entry

CRISIS_MESSAGE = (
    "It sounds like you're going through something really painful. If you are thinking about "
    "harming yourself, please contact local emergency services or a crisis line now, or reach "
    "out to someone you trust. You don't have to handle this alone."
)

NO_ANSWER_MESSAGE = (
    "I don't have a reviewed answer for that yet. I can help with questions about stress, "
    "sleep, mood, and the exercises in this app."
)

_GUARDRAILS = (
    "You are not a therapist or doctor. Never diagnose, never suggest medication, and never "
    "claim to treat anything. Never include phone numbers, websites, or names of hotlines or "
    "organizations. If the user mentions self-harm or danger, tell them to contact local "
    "emergency services or a crisis line."
)

# Hard filter on model output: contact details vary by country and models invent them.
_CONTACT_RE = re.compile(r"\d[\d\-\s().]{5,}\d|\b(?:988|911|999|112|116 ?123)\b|\b1-800\b|https?://|www\.|\b[\w.-]+\.(?:com|org|net|gov)\b", re.IGNORECASE)


def has_contact_details(text: str) -> bool:
    return _CONTACT_RE.search(text) is not None


def fallback_reply(module_title: str, module_description: str) -> str:
    suggestion = f"{module_title}: {module_description}" if module_description else f"{module_title}."
    return f"Thanks for sharing how you're feeling. When you're ready, try {suggestion}"

REPLY_SYSTEM = (
    "You are a warm, supportive wellbeing companion in a self-care app. "
    "In 2-3 short sentences: acknowledge how the user feels in plain words, then gently "
    "invite them to try the suggested exercise. Do not ask more than one question. "
    + _GUARDRAILS
)

ASK_SYSTEM = (
    "You answer questions for a self-care app using only the reference entries provided. "
    "If the entries do not answer the question, say you don't have an answer for that. "
    "Do not add facts that are not in the entries. Keep the answer under 120 words. "
    + _GUARDRAILS
)


def reply_messages(text: str, emotion: str, module_title: str, module_description: str) -> List[Dict[str, str]]:
    return [
        {"role": "system", "content": REPLY_SYSTEM},
        {
            "role": "user",
            "content": (
                f"Detected feeling: {emotion}\n"
                f"Suggested exercise: {module_title} - {module_description}\n"
                f"User's check-in:\n{text}"
            ),
        },
    ]


def ask_messages(question: str, entries: Sequence[Entry]) -> List[Dict[str, str]]:
    references = "\n\n".join(f"[{e.id}] Q: {e.question}\nA: {e.answer}" for e in entries)
    return [
        {"role": "system", "content": ASK_SYSTEM},
        {"role": "user", "content": f"Reference entries:\n{references}\n\nQuestion: {question}"},
    ]
