from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
DEFAULT_DURATION_SECONDS = 20


def safe_filename(value: str) -> str:
    """Convert topic/title text to a safe filename."""
    value = (value or "video").strip().lower()
    value = value.replace(" ", "_")
    value = re.sub(r'[<>:"/\\|?*]+', "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "video"


def get_duration(script_data: dict[str, Any]) -> int:
    """Return video duration from scenario JSON."""
    raw_duration = script_data.get("duration_seconds", DEFAULT_DURATION_SECONDS)

    try:
        duration = int(raw_duration)
    except (TypeError, ValueError):
        duration = DEFAULT_DURATION_SECONDS

    return max(5, min(duration, 60))


def _find_font(bold: bool = False, size: int = 64) -> ImageFont.ImageFont:
    """Find a font with Cyrillic support. Windows Arial is preferred."""
    candidates = []

    if os.name == "nt":
        candidates.extend(
            [
                r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
                r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
            ]
        )

    candidates.extend(
        [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            if bold
            else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/Library/Fonts/Arial Unicode.ttf",
        ]
    )

    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size=size)

    return ImageFont.load_default()


def _text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> int:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def _wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.ImageFont,
    max_width: int,
) -> list[str]:
    words = str(text or "").split()
    if not words:
        return []

    lines: list[str] = []
    current = words[0]

    for word in words[1:]:
        candidate = f"{current} {word}"
        if _text_width(draw, candidate, font) <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word

    lines.append(current)
    return lines


def _draw_wrapped_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.ImageFont,
    xy: tuple[int, int],
    max_width: int,
    fill: tuple[int, int, int],
    line_spacing: int = 18,
) -> int:
    x, y = xy
    lines = _wrap_text(draw, text, font, max_width)

    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        bbox = draw.textbbox((x, y), line, font=font)
        y += bbox[3] - bbox[1] + line_spacing

    return y


def render_title_card(script_data: dict[str, Any], output_path: str | Path) -> Path:
    """Render a vertical 1080x1920 PNG title card with Russian text."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    title = str(script_data.get("title") or script_data.get("topic") or "MM VPN")
    hook = str(script_data.get("hook") or "")
    cta = str(script_data.get("cta") or "MM VPN ? ??????? ? ??????????? ?????????.")

    image = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), color=(12, 18, 32))
    draw = ImageDraw.Draw(image)

    # Simple dark gradient.
    for y in range(VIDEO_HEIGHT):
        shade = int(12 + (y / VIDEO_HEIGHT) * 28)
        draw.line((0, y, VIDEO_WIDTH, y), fill=(12, 18, 32 + shade // 2))

    # Brand blocks.
    margin = 86
    card_x1 = margin
    card_y1 = 230
    card_x2 = VIDEO_WIDTH - margin
    card_y2 = 1360

    draw.rounded_rectangle(
        (card_x1, card_y1, card_x2, card_y2),
        radius=52,
        fill=(245, 248, 255),
    )

    draw.rounded_rectangle(
        (margin, 1480, VIDEO_WIDTH - margin, 1700),
        radius=42,
        fill=(40, 96, 255),
    )

    brand_font = _find_font(bold=True, size=54)
    title_font = _find_font(bold=True, size=76)
    hook_font = _find_font(bold=False, size=52)
    cta_font = _find_font(bold=True, size=46)
    small_font = _find_font(bold=False, size=34)

    draw.text((margin, 105), "MM VPN", font=brand_font, fill=(245, 248, 255))
    draw.text((margin, 178), "???????? ?????", font=small_font, fill=(176, 190, 220))

    y = card_y1 + 80
    y = _draw_wrapped_text(
        draw,
        title,
        title_font,
        (card_x1 + 58, y),
        card_x2 - card_x1 - 116,
        fill=(12, 18, 32),
        line_spacing=22,
    )

    y += 70
    _draw_wrapped_text(
        draw,
        hook,
        hook_font,
        (card_x1 + 58, y),
        card_x2 - card_x1 - 116,
        fill=(46, 59, 82),
        line_spacing=20,
    )

    draw.text((margin + 52, 1538), cta, font=cta_font, fill=(255, 255, 255))

    draw.text(
        (margin, 1788),
        "?? ???????? 100% ???????????. ????? ?????????????? ???? ??????.",
        font=small_font,
        fill=(176, 190, 220),
    )

    image.save(output_path, format="PNG")
    return output_path


def build_ffmpeg_command(
    image_path: str | Path,
    output_path: str | Path,
    duration_seconds: int,
) -> list[str]:
    """Build FFmpeg command that turns PNG card into vertical MP4."""
    ffmpeg_bin = os.getenv("FFMPEG_PATH", "ffmpeg")

    return [
        ffmpeg_bin,
        "-y",
        "-loop",
        "1",
        "-i",
        str(image_path),
        "-t",
        str(duration_seconds),
        "-r",
        "30",
        "-pix_fmt",
        "yuv420p",
        "-vf",
        f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}",
        str(output_path),
    ]


def save_video_stub(
    script_data: dict[str, Any],
    topic: str | None = None,
    output_dir: str | Path = "output/videos",
) -> Path:
    """
    Create a simple vertical MP4 from a generated PNG card.

    The name stays save_video_stub for compatibility with app/main.py.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    base_name = safe_filename(topic or script_data.get("topic") or script_data.get("title") or "video")
    card_path = output_dir / f"{base_name}_card.png"
    video_path = output_dir / f"{base_name}.mp4"

    render_title_card(script_data, card_path)

    command = build_ffmpeg_command(
        image_path=card_path,
        output_path=video_path,
        duration_seconds=get_duration(script_data),
    )

    try:
        subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(
            "FFmpeg ?? ??????. ??????? FFmpeg ??? ????? ???? ? ?????????? FFMPEG_PATH."
        ) from exc
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.decode("utf-8", errors="replace") if exc.stderr else ""
        raise RuntimeError(f"FFmpeg failed:\n{stderr}") from exc

    return video_path


# Compatibility aliases for future imports.
save_video = save_video_stub
build_video = save_video_stub
