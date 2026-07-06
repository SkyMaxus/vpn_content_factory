from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping


DEFAULT_ASPECT_RATIO = "9:16"
DEFAULT_RESOLUTION = "1080x1920"
DEFAULT_VIDEO_MODE = "ai-prompts"
NEGATIVE_PROMPT = (
    "no readable text, no subtitles, no captions, no logos, no brand marks, "
    "no distorted hands, no extra fingers, no glitch artifacts, no scary hacker visuals, "
    "no illegal activity, no dark cybercrime mood"
)

_BAD_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]+')
_SPACE_RE = re.compile(r"\s+")
_CYRILLIC_RE = re.compile(r"[\u0400-\u04FF]")
_UNICODE_ESCAPE_RE = re.compile(r"\\u[0-9a-fA-F]{4}")
_SCENE_PREFIX_RE = re.compile(
    r"^\s*(?:\d+\s*[\).:-]\s*)?"
    r"(?:\u041a\u0430\u0434\u0440|\u0421\u0446\u0435\u043d\u0430|scene|shot)"
    r"\s*\d*\s*[:.-]?\s*",
    re.IGNORECASE,
)


def normalize_text(value: Any) -> str:
    if value is None:
        return ""

    text = str(value)

    if _UNICODE_ESCAPE_RE.search(text):
        text = text.encode("utf-8").decode("unicode_escape")

    replacements = {
        "\u2011": "-",
        "\u2010": "-",
        "\u2012": "-",
        "\u2013": "-",
        "\u2014": "-",
        "\u00a0": " ",
    }

    for source, target in replacements.items():
        text = text.replace(source, target)

    return _SPACE_RE.sub(" ", text).strip()


def contains_cyrillic(text: str) -> bool:
    return bool(_CYRILLIC_RE.search(text or ""))


def safe_filename(value: Any, fallback: str = "visual_prompts") -> str:
    name = normalize_text(value).lower()
    name = _BAD_FILENAME_CHARS.sub("_", name)
    name = re.sub(r"[\s_]+", "_", name)
    name = name.strip("._-")
    return name or fallback


def _as_clean_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [item for item in (normalize_text(item) for item in value) if item]

    if isinstance(value, tuple):
        return [item for item in (normalize_text(item) for item in value) if item]

    text = normalize_text(value)
    return [text] if text else []


def _strip_scene_prefix(line: str) -> str:
    text = normalize_text(line)
    text = _SCENE_PREFIX_RE.sub("", text)
    text = re.sub(r"^\d+\s*[\).:-]\s*", "", text).strip()
    return text


def extract_scene_sources(script_data: Mapping[str, Any], max_scenes: int = 5) -> list[str]:
    visual_ideas = _as_clean_list(script_data.get("visual_ideas"))
    if visual_ideas:
        return visual_ideas[:max_scenes]

    raw_script = str(script_data.get("script") or "")
    script_sources: list[str] = []

    for line in raw_script.splitlines():
        source = _strip_scene_prefix(line)
        if source:
            script_sources.append(source)

    if script_sources:
        return script_sources[:max_scenes]

    fallback_sources = [
        normalize_text(script_data.get("hook")),
        normalize_text(script_data.get("title")),
        normalize_text(script_data.get("topic")),
    ]

    return [source for source in fallback_sources if source][:max_scenes] or [
        "Generic mobile internet privacy scene"
    ]


def _source_has(source: str, keywords: tuple[str, ...]) -> bool:
    source_lower = normalize_text(source).lower()

    for keyword in keywords:
        normalized_keyword = normalize_text(keyword).lower()
        if normalized_keyword and normalized_keyword in source_lower:
            return True

    return False


def _guess_visual_en(source_ru: str) -> str:
    source = normalize_text(source_ru)

    if _source_has(source, ("\u0430\u044d\u0440\u043e\u043f", "airport")):
        return (
            "busy airport terminal, travelers with suitcases, a calm person using a smartphone "
            "while waiting near the gate"
        )

    if _source_has(source, ("\u0444\u0438\u043d\u0430\u043b", "\u043b\u043e\u0433\u043e", "cta", "brand")):
        return (
            "clean modern closing shot with abstract privacy visuals, soft gradient background, "
            "empty space for a logo and call to action added later"
        )

    if _source_has(source, ("\u043a\u0430\u0444\u0435", "cafe", "coffee")):
        return (
            "cozy cafe interior, public wifi atmosphere, person using a smartphone near a laptop "
            "and a cup of coffee"
        )

    if _source_has(source, ("\u043e\u0442\u0435\u043b", "hotel")):
        return (
            "hotel lobby or hotel room workspace, traveler checking messages on a smartphone, "
            "calm business trip mood"
        )

    if _source_has(source, ("wi-fi", "wifi", "\u043f\u0443\u0431\u043b\u0438\u0447")):
        return (
            "public wifi situation, smartphone connection screen without readable text, "
            "subtle privacy shield animation style"
        )

    if _source_has(source, ("vpn", "mm vpn", "\u043f\u0440\u0438\u043b\u043e\u0436", "\u0438\u043d\u0442\u0435\u0440\u0444\u0435\u0439\u0441")):
        return (
            "smartphone with a generic privacy app interface, simple connection animation, "
            "clean technology look, no readable UI text"
        )

    if _source_has(source, ("\u043f\u043e\u0447\u0442", "\u0431\u0438\u043b\u0435\u0442", "email", "ticket", "\u043d\u043e\u0443\u0442")):
        return (
            "calm user checking email, travel tickets and messages on a smartphone and laptop, "
            "safe everyday internet use mood"
        )

    if _source_has(source, ("\u0441\u043c\u0430\u0440\u0442\u0444\u043e\u043d", "\u0442\u0435\u043b\u0435\u0444\u043e\u043d", "phone")):
        return (
            "close-up of a smartphone in hand, modern mobile internet use, clean neutral background"
        )

    return (
        "person using a smartphone in a modern public place, calm privacy focused atmosphere, "
        "natural everyday technology scene"
    )


def build_video_prompt(source_ru: str, scene_index: int = 1, duration_seconds: int = 4) -> str:
    visual_en = _guess_visual_en(source_ru)

    return (
        f"Vertical 9:16 realistic short video, scene {scene_index}, about "
        f"{duration_seconds} seconds. {visual_en}. Smooth camera movement, "
        "natural lighting, modern commercial b-roll style. Leave clean empty space "
        "for later Russian subtitles and CTA overlays. No readable text on screen."
    )


def _scene_duration(script_data: Mapping[str, Any], scenes_count: int) -> int:
    try:
        total_duration = int(script_data.get("duration_seconds") or 20)
    except (TypeError, ValueError):
        total_duration = 20

    if scenes_count <= 0:
        return 4

    return max(3, round(total_duration / scenes_count))


def generate_visual_prompts(script_data: Mapping[str, Any]) -> dict[str, Any]:
    sources = extract_scene_sources(script_data)
    subtitles = _as_clean_list(script_data.get("subtitles"))
    scenes_count = len(sources)
    duration = _scene_duration(script_data, scenes_count)
    cta_ru = normalize_text(script_data.get("cta"))

    scenes = []
    for index, source_ru in enumerate(sources, start=1):
        subtitle_ru = subtitles[index - 1] if index - 1 < len(subtitles) else ""

        scenes.append(
            {
                "scene": index,
                "duration_seconds": duration,
                "source_ru": source_ru,
                "prompt_en": build_video_prompt(source_ru, index, duration),
                "subtitle_ru": subtitle_ru,
                "cta_ru": cta_ru if index == scenes_count else "",
                "negative_prompt": NEGATIVE_PROMPT,
            }
        )

    return {
        "title": normalize_text(script_data.get("title")),
        "topic": normalize_text(script_data.get("topic")),
        "format": "ai_video_prompts",
        "video_mode": DEFAULT_VIDEO_MODE,
        "aspect_ratio": DEFAULT_ASPECT_RATIO,
        "resolution": DEFAULT_RESOLUTION,
        "scenes_count": scenes_count,
        "scenes": scenes,
    }


def save_visual_prompts(
    script_data: Mapping[str, Any],
    topic: str | Path | None = None,
    output_dir: str | Path = "output/prompts",
) -> Path:
    prompts_data = generate_visual_prompts(script_data)

    if topic is not None:
        possible_path = Path(topic)
        if possible_path.suffix.lower() == ".json":
            path = possible_path
        else:
            filename_base = safe_filename(topic)
            path = Path(output_dir) / f"{filename_base}_visual_prompts.json"
    else:
        filename_base = safe_filename(
            script_data.get("topic") or script_data.get("title") or "visual_prompts"
        )
        path = Path(output_dir) / f"{filename_base}_visual_prompts.json"

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="\n") as file:
        json.dump(prompts_data, file, ensure_ascii=False, indent=2)

    return path
