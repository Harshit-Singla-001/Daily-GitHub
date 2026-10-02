import re


INJECTION_PATTERNS = [
    r"ignore\s+(all|any|the|previous|prior|above)\s+instructions",
    r"disregard\s+(all|any|the|previous|prior|above)\s+instructions",
    r"forget\s+(all|any|the|previous|prior|above)\s+instructions",
    r"override\s+(all|any|the|previous|prior|above)\s+instructions",
    r"reveal\s+(your|the)\s+(system|hidden)\s+prompt",
    r"show\s+(me\s+)?(your|the)\s+(system|hidden)\s+prompt",
    r"print\s+(your|the)\s+(system|hidden)\s+prompt",
    r"what\s+are\s+your\s+system\s+instructions",
    r"developer\s+message",
    r"system\s+prompt",
    r"jailbreak",
    r"bypass\s+(your|the)\s+safety",
    r"ignore\s+safety",
    r"act\s+as\s+if\s+you\s+have\s+no\s+rules",
    r"pretend\s+you\s+are\s+not\s+an\s+ai",
]


def detect_prompt_injection(text):
    if not text:
        return {
            "blocked": False,
            "matches": []
        }

    normalized_text = " ".join(text.lower().split())

    matches = []

    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, normalized_text, re.IGNORECASE):
            matches.append(pattern)

    return {
        "blocked": len(matches) > 0,
        "matches": matches
    }


def sanitize_for_prompt(text):
    text = text.replace("\x00", "")
    text = text.strip()

    return text