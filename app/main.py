"""CLI entry point for VPN content factory MVP."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from config import load_settings
from moderation import assert_safe_script
from script_writer import generate_video_script


def safe_filename(topic: str) -> str:
    name = topic.lower().strip()
    name = name.replace("wi-fi", "wi_fi")
    name = re.sub(r'[\\/:*?"<>|]+', "_", name)
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"_+", "_", name)
    name = name.strip("._")
    return name or "script"


def save_script(data: dict, topic: str, output_dir: str) -> Path:
    folder = Path(output_dir)
    folder.mkdir(parents=True, exist_ok=True)

    path = folder / f"{safe_filename(topic)}.json"

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate local VPN video script JSON.")
    parser.add_argument("--topic", required=True, help="Video topic")
    parser.add_argument("--print-json", action="store_true", help="Print JSON to console")
    args = parser.parse_args()

    settings = load_settings()

    script_data = generate_video_script(
        topic=args.topic,
        brand_name=settings.brand_name,
        cta_text=settings.cta_text,
    )

    if settings.safe_mode:
        assert_safe_script(script_data)

    path = save_script(script_data, args.topic, settings.output_dir)

    if args.print_json:
        print(json.dumps(script_data, ensure_ascii=False, indent=2))

    print(f"\u0413\u043e\u0442\u043e\u0432\u043e. \u0421\u0446\u0435\u043d\u0430\u0440\u0438\u0439 \u0441\u043e\u0445\u0440\u0430\u043d\u0451\u043d: {path}")


if __name__ == "__main__":
    main()
