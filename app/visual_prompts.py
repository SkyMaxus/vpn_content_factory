from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


DEFAULT_SCENE_DURATION_SECONDS = 4
DEFAULT_MAX_SCENES = 5
DEFAULT_NEGATIVE_PROMPT = (
    "no readable text, no subtitles, no logos, no fake app interface, "
    "no distorted hands, no distorted faces, no glitches, no watermark"
)
SCENE_MARKER_PATTERN = "(?:\u0421\u0446\u0435\u043d\u0430|\u041a\u0430\u0434\u0440)\\s*\\d+\\s*[:.-]?"


def normalize_text(value: Any) -> str:
    """Normalize text for prompt generation."""
    text = str(value or "")
    replacements = {
        "\u2011": "-",
        "\u2010": "-",
        "\u2012": "-",
        "\u2013": "-",
        "\u2014": "-",
        "\xa0": " ",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"\s+", " ", text).strip()
    return text


def safe_filename(value: str) -> str:
    """Convert topic/title text to a safe filename."""
    value = normalize_text(value or "visual_prompts").lower()
    value = value.replace(" ", "_")
    value = re.sub(r'[<>:"/\\|?*]+', "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "visual_prompts"


def extract_scene_sources(script_data: dict[str, Any], max_scenes: int = DEFAULT_MAX_SCENES) -> list[str]:
    """
    Extract short source ideas from scenario JSON.

    Priority:
    1. visual_ideas
    2. subtitles
    3. script lines
    4. hook/title fallback
    """
    sources: list[str] = []

    for key in ("visual_ideas", "subtitles"):
        values = script_data.get(key)

        if isinstance(values, list):
            for item in values:
                text = normalize_text(item)
                if text:
                    sources.append(text)

    if not sources:
        script_text = normalize_text(script_data.get("script"))

        if script_text:
            parts = re.split(SCENE_MARKER_PATTERN, script_text, flags=re.IGNORECASE)

            for part in parts:
                text = normalize_text(part)
                if text:
                    sources.append(text)

    if not sources:
        fallback = normalize_text(script_data.get("hook") or script_data.get("title") or script_data.get("topic"))
        if fallback:
            sources.append(fallback)

    unique_sources: list[str] = []
    seen: set[str] = set()

    for source in sources:
        key = source.lower()

        if key not in seen:
            unique_sources.append(source)
            seen.add(key)

        if len(unique_sources) >= max_scenes:
            break

    return unique_sources


def build_video_prompt(scene_source: str, topic: str | None = None) -> str:
    """Build an English prompt for AI video generation."""
    scene_source = normalize_text(scene_source)
    topic = normalize_text(topic)

    topic_part = f" Topic: {topic}." if topic else ""

    return (
        "Vertical 9:16 realistic short video for a privacy and VPN social media ad. "
        "Clean modern cinematic look, natural lighting, smartphone lifestyle scene, "
        "subtle cybersecurity atmosphere, calm trustworthy mood. "
        f"Scene idea: {scene_source}.{topic_part} "
        "No text overlays, no subtitles, no brand logos, because text and branding "
        "will be added later in post-production."
    )


def generate_visual_prompts(
    script_data: dict[str, Any],
    max_scenes: int = DEFAULT_MAX_SCENES,
) -> dict[str, Any]:
    """Generate structured AI-video prompts from scenario JSON."""
    topic = normalize_text(script_data.get("topic") or script_data.get("title") or "VPN video")
    title = normalize_text(script_data.get("title") or topic)
    sources = extract_scene_sources(script_data, max_scenes=max_scenes)

    scenes = []

    for index, source in enumerate(sources, start=1):
        scenes.append(
            {
                "scene": index,
                "duration_seconds": DEFAULT_SCENE_DURATION_SECONDS,
                "source": source,
                "prompt": build_video_prompt(source, topic=topic),
                "negative_prompt": DEFAULT_NEGATIVE_PROMPT,
            }
        )

    return {
        "title": title,
        "topic": topic,
        "format": "ai_video_prompts",
        "video_mode": "ai-prompts",
        "aspect_ratio": "9:16",
        "resolution": "1080x1920",
        "scenes_count": len(scenes),
        "scenes": scenes,
        "final_assembly_note": (
            "Generate clips from these prompts, then assemble them with local Python/FFmpeg: "
            "voiceover, subtitles, logo, CTA and final safety disclaimer."
        ),
    }


def save_visual_prompts(
    script_data: dict[str, Any],
    topic: str | None = None,
    output_dir: str | Path = "output/prompts",
) -> Path:
    """Save generated AI-video prompts as JSON."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    base_name = safe_filename(topic or script_data.get("topic") or script_data.get("title") or "visual_prompts")
    output_path = output_dir / f"{base_name}_visual_prompts.json"

    data = generate_visual_prompts(script_data)

    with output_path.open("w", encoding="utf-8", newline="\n") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

    return output_path


def load_script_json(path: str | Path) -> dict[str, Any]:
    """Load scenario JSON from disk."""
    path = Path(path)

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError("Script JSON must be an object.")

    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="Export AI-video prompts from generated script JSON.")
    parser.add_argument("--script", required=True, help="Path to generated scenario JSON.")
    parser.add_argument("--output-dir", default="output/prompts", help="Directory for visual prompt JSON.")
    args = parser.parse_args()

    script_data = load_script_json(args.script)
    output_path = save_visual_prompts(script_data, output_dir=args.output_dir)
    print(f"Visual prompts saved: {output_path}")


if __name__ == "__main__":
    main()
