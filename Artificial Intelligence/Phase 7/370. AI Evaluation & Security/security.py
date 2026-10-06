import re
import json
from datetime import datetime

from config import AUDIT_LOG_FILE


PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"ignore\s+(all\s+)?prior\s+instructions",
    r"disregard\s+(all\s+)?previous\s+instructions",
    r"forget\s+(all\s+)?previous\s+instructions",
    r"override\s+(the\s+)?system",
    r"reveal\s+(the\s+)?system\s+prompt",
    r"show\s+(me\s+)?your\s+system\s+prompt",
    r"developer\s+message",
    r"jailbreak",
    r"you\s+are\s+now\s+an?\s+unrestricted",
]


SENSITIVE_PATTERNS = {
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",

    "api_key": (
        r"\b(?:sk-[A-Za-z0-9_-]{10,}|"
        r"AIza[A-Za-z0-9_-]{20,})\b"
    ),

    "password_assignment": (
        r"(?i)\bpassword\s*[:=]\s*\S+"
    ),

    "token": (
        r"(?i)\b(?:access[_-]?token|auth[_-]?token|"
        r"bearer)\s*[:=]\s*\S+"
    ),

    "credit_card": (
        r"\b(?:\d[ -]*?){13,19}\b"
    ),
}


UNSAFE_TOOL_PATTERNS = [
    r"\bdelete\s+(all|the|every)\b",
    r"\bdrop\s+(database|table)\b",
    r"\bexecute\s+(shell|command|code)\b",
    r"\brm\s+-rf\b",
    r"\bformat\s+(the\s+)?drive\b",
    r"\bsend\s+money\b",
    r"\btransfer\s+funds\b",
    r"\bdisable\s+security\b",
    r"\bgrant\s+admin\b",
    r"\bchange\s+permissions?\b",
]


def detect_prompt_injection(text):
    findings = []

    lowered = text.lower()

    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, lowered):
            findings.append({
                "type": "prompt_injection",
                "pattern": pattern,
                "severity": "HIGH",
            })

    return findings


def detect_sensitive_data(text):
    findings = []

    for data_type, pattern in SENSITIVE_PATTERNS.items():
        matches = re.findall(pattern, text)

        if matches:
            findings.append({
                "type": "sensitive_data",
                "data_type": data_type,
                "count": len(matches),
                "severity": "HIGH",
            })

    return findings


def detect_unsafe_tools(text):
    findings = []

    lowered = text.lower()

    for pattern in UNSAFE_TOOL_PATTERNS:
        if re.search(pattern, lowered):
            findings.append({
                "type": "unsafe_tool_usage",
                "pattern": pattern,
                "severity": "CRITICAL",
            })

    return findings


def calculate_security_risk(
    injection_findings,
    sensitive_findings,
    tool_findings,
):
    score = 0

    score += min(len(injection_findings) * 30, 60)
    score += min(len(sensitive_findings) * 25, 50)
    score += min(len(tool_findings) * 40, 80)

    score = min(score, 100)

    if score <= 24:
        level = "LOW"
    elif score <= 49:
        level = "MEDIUM"
    elif score <= 74:
        level = "HIGH"
    else:
        level = "CRITICAL"

    return score, level


def create_security_report(user_input):
    injection_findings = detect_prompt_injection(user_input)
    sensitive_findings = detect_sensitive_data(user_input)
    tool_findings = detect_unsafe_tools(user_input)

    score, level = calculate_security_risk(
        injection_findings,
        sensitive_findings,
        tool_findings,
    )

    return {
        "risk_score": score,
        "risk_level": level,
        "prompt_injection": injection_findings,
        "sensitive_data": sensitive_findings,
        "unsafe_tools": tool_findings,
    }


def save_audit_log(report):
    existing_logs = []

    if AUDIT_LOG_FILE.exists():
        try:
            with open(
                AUDIT_LOG_FILE,
                "r",
                encoding="utf-8",
            ) as file:
                existing_logs = json.load(file)

                if not isinstance(existing_logs, list):
                    existing_logs = []

        except (json.JSONDecodeError, OSError):
            existing_logs = []

    report["timestamp"] = datetime.now().isoformat()

    existing_logs.append(report)

    existing_logs = existing_logs[-100:]

    with open(
        AUDIT_LOG_FILE,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            existing_logs,
            file,
            indent=4,
        )