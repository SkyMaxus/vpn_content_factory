"""Simple vertical video builder using FFmpeg.

MVP version: creates a plain vertical MP4 background.
Text overlays will be added later after the base video pipeline is stable.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path
from typing import Any


WIDTH = 1080
HEIGHT = 1920
FPS = 30


def safe_filename(name: str) -> str:
    value = name.lower().strip()
    value = value.replace("wi-fi", "wi_fi")
    value = re.sub(r'[\\/:*?"<>|]+', "_", value)
    value = re.sub(r"\s+", "_", value)
    value = re.sub(r"_+", "_", value)
    value = value.strip("._")
    return value or "video"


def get_duration(script_data: dict[str, Any]) -> float:
    duration = script_data.get("duration_seconds", 20)

    try:
        value = float(duration)
    except (TypeError, ValueError):
        value = 20.0

    if value <= 0:
        value = 20.0

    return value


def build_ffmpeg_command(
    script_data: dict[str, Any],
    output_path: Path,
) -> list[str]:
    ffmpeg = shutil.which("ffmpeg")

    if not ffmpeg:
        raise RuntimeError("FFmpeg not found. Install FFmpeg and restart terminal.")

    duration = get_duration(script_data)

    return [
        ffmpeg,
        "-y",
        "-f",
        "lavfi",
        "-i",
        f"color=c=0x101827:s={WIDTH}x{HEIGHT}:r={FPS}",
        "-t",
        str(duration),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(output_path),
    ]


def save_video_stub(
    script_data: dict[str, Any],
    topic: str,
    output_dir: str = "output/videos",
) -> Path:
    folder = Path(output_dir)
    folder.mkdir(parents=True, exist_ok=True)

    path = folder / f"{safe_filename(topic)}.mp4"
    command = build_ffmpeg_command(script_data, path)

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    if result.returncode != 0:
        raise RuntimeError("FFmpeg failed:\n" + result.stderr[-3000:])

    if not path.exists() or path.stat().st_size == 0:
        raise RuntimeError(f"Video was not created: {path}")

    return path
