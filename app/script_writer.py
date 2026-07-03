"""Script generator with mock mode and optional OpenAI API mode."""

from __future__ import annotations

import json
import re
from typing import Any


REQUIRED_KEYS = [
    "title",
    "topic",
    "format",
    "duration_seconds",
    "hook",
    "script",
    "voiceover_text",
    "subtitles",
    "cta",
    "visual_ideas",
    "hashtags",
    "status",
]


def generate_video_script(
    topic: str,
    brand_name: str = "MM VPN",
    cta_text: str | None = None,
    ai_provider: str = "mock",
    ai_model: str = "gpt-5.5",
    openai_api_key: str = "",
) -> dict[str, Any]:
    topic = topic.strip()
    if not topic:
        raise ValueError("Topic cannot be empty.")

    provider = (ai_provider or "mock").strip().lower()
    cta = cta_text or f"{brand_name} — включил и пользуешься спокойнее."

    if provider in {"openai", "real"} and openai_api_key:
        try:
            return _generate_with_openai(topic, brand_name, cta, ai_model, openai_api_key)
        except Exception as exc:
            data = _generate_mock_script(topic, brand_name, cta)
            data["ai_provider"] = "mock_fallback"
            data["ai_error"] = f"{type(exc).__name__}: {exc}"
            return data

    data = _generate_mock_script(topic, brand_name, cta)
    data["ai_provider"] = "mock"
    data["ai_model"] = "local_template"
    return data


def _generate_with_openai(
    topic: str,
    brand_name: str,
    cta_text: str,
    ai_model: str,
    openai_api_key: str,
) -> dict[str, Any]:
    from openai import OpenAI

    client = OpenAI(api_key=openai_api_key)

    prompt = {
        "task": "generate_safe_vpn_short_video_script",
        "topic": topic,
        "brand_name": brand_name,
        "cta_text": cta_text,
        "language": "ru",
        "required_keys": REQUIRED_KEYS,
    }

    response = client.responses.create(
        model=ai_model,
        instructions=(
            "ерни только JSON без markdown. "
            "иши безопасный рекламный сценарий для VPN. "
            "е обещай 100% анонимность, невозможность отслеживания, обход любых блокировок, "
            "взлом ограничений, бесплатный доступ к платным сервисам или защиту от всего."
        ),
        input=json.dumps(prompt, ensure_ascii=False),
        max_output_tokens=1000,
    )

    data = _parse_json_object(response.output_text)
    data = _normalize_script(data, topic, brand_name, cta_text)
    data["ai_provider"] = "openai"
    data["ai_model"] = ai_model
    return data


def _parse_json_object(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.S)
        if not match:
            raise
        data = json.loads(match.group(0))

    if not isinstance(data, dict):
        raise ValueError("AI output must be a JSON object.")

    return data


def _normalize_script(
    data: dict[str, Any],
    topic: str,
    brand_name: str,
    cta_text: str,
) -> dict[str, Any]:
    fallback = _generate_mock_script(topic, brand_name, cta_text)

    for key in REQUIRED_KEYS:
        if key not in data or data[key] in {None, ""}:
            data[key] = fallback[key]

    for key in ("subtitles", "visual_ideas", "hashtags"):
        if not isinstance(data.get(key), list):
            data[key] = fallback[key]

    data["topic"] = str(data.get("topic") or topic).strip()
    data["cta"] = str(data.get("cta") or cta_text).strip()
    data["status"] = str(data.get("status") or "draft").strip()

    try:
        data["duration_seconds"] = int(data.get("duration_seconds", 25))
    except (TypeError, ValueError):
        data["duration_seconds"] = 25

    return data


def _generate_mock_script(
    topic: str,
    brand_name: str = "MM VPN",
    cta_text: str | None = None,
) -> dict[str, Any]:
    cta = cta_text or f"{brand_name} — включил и пользуешься спокойнее."
    title_topic = topic[:1].upper() + topic[1:]
    hook = _build_hook(topic)
    voiceover = _build_voiceover(topic, cta)

    return {
        "title": f"{title_topic}: что важно знать",
        "topic": topic,
        "format": "mini_guide",
        "duration_seconds": 25,
        "hook": hook,
        "script": voiceover,
        "voiceover_text": voiceover,
        "subtitles": [
            "Подключился к публичному Wi-Fi?",
            "Не спеши вводить пароли.",
            "VPN помогает защитить трафик.",
            "Это полезный слой защиты.",
            f"{brand_name} — включил и пользуешься спокойнее.",
        ],
        "cta": cta,
        "visual_ideas": [
            "человек с телефоном в общественном месте",
            "иконка открытого Wi-Fi",
            "анимация защищённого туннеля",
            "экран с кнопкой подключения VPN",
        ],
        "hashtags": ["#vpn", "#безопасность", "#wifi", "#приватность", "#mmvpn"],
        "status": "draft",
    }


def _build_hook(topic: str) -> str:
    low = topic.lower()
    if "wi-fi" in low or "wifi" in low:
        return "Подключился к бесплатному Wi-Fi? Подожди 10 секунд."
    if "аэропорт" in low:
        return "Wi-Fi в аэропорту удобный, но не всегда безопасный."
    return f"{topic[:1].upper() + topic[1:]} — коротко и без сложных слов."


def _build_voiceover(topic: str, cta: str) -> str:
    return (
        f"{_build_hook(topic)}\n"
        "В публичных сетях не всегда понятно, кто ещё находится рядом и как настроена сеть. "
        "VPN создаёт защищённый туннель между устройством и сервером, поэтому пользоваться "
        "интернетом в общественных местах спокойнее. "
        "Это не магия, но это полезный слой защиты для обычных ситуаций. "
        f"{cta}"
    )