"""Subtitle generation module.

Creates simple SRT subtitles from script_data["subtitles"].
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


def safe_filename(name: str) -> str:
    value = name.lower().strip()
    value = value.replace("wi-fi", "wi_fi")
    value = re.sub(r'[\\/:*?"<>|]+', "_", value)
    value = re.sub(r"\s+", "_", value)
    value = re.sub(r"_+", "_", value)
    value = value.strip("._")
    return value or "subtitles"


def format_srt_time(seconds: float) -> str:
    if seconds < 0:
        seconds = 0

    milliseconds = int(round((seconds - int(seconds)) * 1000))
    total_seconds = int(seconds)

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60

    return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"


def extract_subtitle_lines(script_data: dict[str, Any]) -> list[str]:
    raw = script_data.get("subtitles", [])

    if not isinstance(raw, list):
        raise ValueError("subtitles must be a list.")

    lines: list[str] = []

    for item in raw:
        if not isinstance(item, str):
            continue

        text = item.strip()
        if text:
            lines.append(text)

    if not lines:
        raise ValueError("No valid subtitle lines found.")

    return lines


def build_srt(
    lines: list[str],
    duration_seconds: int | float = 20,
) -> str:
    if not lines:
        raise ValueError("Subtitle lines cannot be empty.")

    duration = float(duration_seconds)

    if duration <= 0:
        duration = 20.0

    step = duration / len(lines)
    chunks: list[str] = []

    for index, line in enumerate(lines, start=1):
        start = (index - 1) * step
        end = index * step

        chunks.append(
            f"{index}\n"
            f"{format_srt_time(start)} --> {format_srt_time(end)}\n"
            f"{line}\n"
        )

    return "\n".join(chunks).strip() + "\n"


def save_subtitles_srt(
    script_data: dict[str, Any],
    topic: str,
    output_dir: str = "output/subtitles",
) -> Path:
    folder = Path(output_dir)
    folder.mkdir(parents=True, exist_ok=True)

    lines = extract_subtitle_lines(script_data)
    duration = script_data.get("duration_seconds", 20)
    srt = build_srt(lines, duration)

    path = folder / f"{safe_filename(topic)}.srt"
    path.write_text(srt, encoding="utf-8", newline="\n")

    return path
