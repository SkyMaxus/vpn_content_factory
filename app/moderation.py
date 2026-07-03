"""Simple moderation for VPN marketing texts."""

from __future__ import annotations

from typing import Any


class ModerationError(ValueError):
    """Raised when generated content has risky VPN promises."""


def normalize_text(text: str) -> str:
    return (
        text.lower()
        .replace("\u0451", "\u0435")
        .replace("\u2011", "-")
        .replace("\u2013", "-")
        .replace("\u2014", "-")
        .strip()
    )


def find_risky_phrases(text: str) -> list[str]:
    t = normalize_text(text)
    issues: list[str] = []

    if "100%" in t and "\u0430\u043d\u043e\u043d\u0438\u043c" in t:
        issues.append("100% anonymity")

    if "\u043d\u0435\u0432\u043e\u0437\u043c\u043e\u0436" in t and "\u043e\u0442\u0441\u043b\u0435\u0434" in t:
        issues.append("impossible to track")

    if "\u043f\u043e\u043b\u043d" in t and "\u043d\u0435\u0432\u0438\u0434\u0438\u043c" in t:
        issues.append("full invisibility")

    if "\u043e\u0431\u0445\u043e\u0434" in t and "\u043b\u044e\u0431" in t and "\u0431\u043b\u043e\u043a\u0438\u0440\u043e\u0432" in t:
        issues.append("bypass any blocks")

    if "\u043f\u043b\u0430\u0442\u043d" in t and "\u0441\u0435\u0440\u0432\u0438\u0441" in t and "\u0431\u0435\u0441\u043f\u043b\u0430\u0442" in t:
        issues.append("free access to paid services")

    if "\u0432\u0437\u043b\u043e\u043c" in t and "\u043e\u0433\u0440\u0430\u043d\u0438\u0447" in t:
        issues.append("hack restrictions")

    if "\u0437\u0430\u0449\u0438\u0442" in t and "\u043e\u0442 \u0432\u0441" in t:
        issues.append("protection from everything")

    if "\u0430\u0431\u0441\u043e\u043b\u044e\u0442" in t and "\u0431\u0435\u0437\u043e\u043f\u0430\u0441" in t:
        issues.append("absolute safety")

    return issues


def check_text(text: str) -> dict[str, Any]:
    issues = find_risky_phrases(text)
    return {
        "is_safe": len(issues) == 0,
        "issues": issues,
    }


def extract_text(data: Any) -> str:
    if isinstance(data, str):
        return data

    if isinstance(data, dict):
        return " ".join(extract_text(value) for value in data.values())

    if isinstance(data, list):
        return " ".join(extract_text(item) for item in data)

    return ""


def check_script_data(script_data: dict[str, Any]) -> dict[str, Any]:
    return check_text(extract_text(script_data))


def assert_safe_script(script_data: dict[str, Any]) -> None:
    result = check_script_data(script_data)

    if not result["is_safe"]:
        issues = ", ".join(result["issues"])
        raise ModerationError(f"Script failed moderation. Risks: {issues}")
