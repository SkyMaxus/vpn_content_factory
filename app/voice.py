"""Temporary voiceover module.

For now this does not call paid TTS APIs.
It saves voiceover text to output/audio as a .txt file.
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
    return value or "voiceover"


def extract_voiceover_text(script_data: dict[str, Any]) -> str:
    text = script_data.get("voiceover_text") or script_data.get("script") or ""

    if not isinstance(text, str):
        raise ValueError("voiceover_text/script must be a string.")

    text = text.strip()

    if not text:
        raise ValueError("No voiceover text found in script data.")

    return text


def save_voiceover_stub(
    script_data: dict[str, Any],
    topic: str,
    output_dir: str = "output/audio",
) -> Path:
    folder = Path(output_dir)
    folder.mkdir(parents=True, exist_ok=True)

    path = folder / f"{safe_filename(topic)}.txt"
    text = extract_voiceover_text(script_data)
    path.write_text(text, encoding="utf-8", newline="\n")

    return path
