"""CLI entry point for VPN content factory MVP."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from config import load_settings
from ideas import choose_random_topic, load_topics
from moderation import assert_safe_script
from script_writer import generate_video_script
from subtitles import save_subtitles_srt
from voice import save_voiceover_stub
from video_builder import save_video_stub
from visual_prompts import save_visual_prompts


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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate local VPN video script JSON.")

    topic_group = parser.add_mutually_exclusive_group(required=True)
    topic_group.add_argument("--topic", help="Video topic")
    topic_group.add_argument("--random-topic", action="store_true", help="Pick random topic from topics file")
    topic_group.add_argument("--list-topics", action="store_true", help="Show available topics and exit")

    parser.add_argument("--topics-file", default="data/content_topics.json", help="Path to topics JSON file")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for stable tests/debug")
    parser.add_argument("--print-json", action="store_true", help="Print JSON to console")

    parser.add_argument(
        "--make-voice",
        action="store_true",
        help="Save voiceover text to output/audio as a temporary TTS stub",
    )

    parser.add_argument(
        "--make-subtitles",
        action="store_true",
        help="Save subtitles to output/subtitles as an SRT file",
    )

    parser.add_argument(
        "--make-video",
        action="store_true",
        help="Save simple vertical MP4 video to output/videos",
    )

    parser.add_argument(
        "--make-visual-prompts",
        action="store_true",
        help="Save AI-video prompts to output/prompts",
    )

    return parser


def resolve_topic(args: argparse.Namespace) -> str | None:
    if args.list_topics:
        topics = load_topics(args.topics_file)
        for index, topic in enumerate(topics, start=1):
            print(f"{index}. {topic}")
        return None

    if args.random_topic:
        topic = choose_random_topic(args.topics_file, seed=args.seed)
        print(f"Selected random topic: {topic}")
        return topic

    return args.topic


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    topic = resolve_topic(args)
    if topic is None:
        return

    settings = load_settings()

    script_data = generate_video_script(
        topic=topic,
        brand_name=settings.brand_name,
        cta_text=settings.cta_text,
        ai_provider=settings.ai_provider,
        ai_model=settings.ai_model,
        openai_api_key=settings.openai_api_key,
    )

    if settings.safe_mode:
        assert_safe_script(script_data)

    path = save_script(script_data, topic, settings.output_dir)

    subtitles_path = None
    if args.make_subtitles:
        subtitles_path = save_subtitles_srt(script_data, topic)

    voice_path = None
    if args.make_voice:
        voice_path = save_voiceover_stub(script_data, topic)

    video_path = None
    if args.make_video:
        video_path = save_video_stub(script_data, topic)

    visual_prompts_path = None
    if args.make_visual_prompts:
        visual_prompts_path = save_visual_prompts(script_data, topic)

    if args.print_json:
        print(json.dumps(script_data, ensure_ascii=False, indent=2))

    print(f"Done. Script saved: {path}")
    if subtitles_path is not None:
        print(f"Subtitles saved: {subtitles_path}")
    if voice_path is not None:
        print(f"Voiceover saved: {voice_path}")
    if video_path is not None:
        print(f"Video saved: {video_path}")
    if visual_prompts_path is not None:
        print(f"Visual prompts saved: {visual_prompts_path}")


if __name__ == "__main__":
    main()
