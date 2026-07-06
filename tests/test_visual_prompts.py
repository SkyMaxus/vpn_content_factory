import json
import tempfile
import unittest
from pathlib import Path

from app.visual_prompts import (
    DEFAULT_MAX_SCENES,
    build_video_prompt,
    extract_scene_sources,
    generate_visual_prompts,
    normalize_text,
    safe_filename,
    save_visual_prompts,
)


class TestVisualPrompts(unittest.TestCase):
    def test_normalize_text(self):
        self.assertEqual(normalize_text("Wi\u2011Fi  test"), "Wi-Fi test")
        self.assertEqual(normalize_text("  hello   world  "), "hello world")

    def test_safe_filename(self):
        topic = "VPN \u0432 \u0430\u044d\u0440\u043e\u043f\u043e\u0440\u0442\u0443"
        expected = "vpn_\u0432_\u0430\u044d\u0440\u043e\u043f\u043e\u0440\u0442\u0443"
        self.assertEqual(safe_filename(topic), expected)
        self.assertEqual(safe_filename("bad/name:*?"), "bad_name")

    def test_extract_scene_sources_prefers_visual_ideas(self):
        script_data = {
            "visual_ideas": [
                "\u0427\u0435\u043b\u043e\u0432\u0435\u043a \u0432 \u0430\u044d\u0440\u043e\u043f\u043e\u0440\u0442\u0443",
                "\u042d\u043a\u0440\u0430\u043d \u0441 Wi\u2011Fi",
            ],
            "subtitles": ["subtitle should be lower priority"],
        }

        sources = extract_scene_sources(script_data)

        self.assertEqual(sources[0], "\u0427\u0435\u043b\u043e\u0432\u0435\u043a \u0432 \u0430\u044d\u0440\u043e\u043f\u043e\u0440\u0442\u0443")
        self.assertIn("Wi-Fi", sources[1])

    def test_extract_scene_sources_fallback_to_hook(self):
        script_data = {
            "hook": "Public Wi-Fi in airport",
        }

        sources = extract_scene_sources(script_data)

        self.assertEqual(sources, ["Public Wi-Fi in airport"])

    def test_build_video_prompt(self):
        prompt = build_video_prompt("Traveler uses phone in airport", topic="VPN in airport")

        self.assertIn("Vertical 9:16", prompt)
        self.assertIn("Traveler uses phone in airport", prompt)
        self.assertIn("No text overlays", prompt)

    def test_generate_visual_prompts(self):
        script_data = {
            "title": "VPN test",
            "topic": "VPN topic",
            "visual_ideas": [
                "Scene one",
                "Scene two",
                "Scene three",
                "Scene four",
                "Scene five",
                "Scene six",
            ],
        }

        result = generate_visual_prompts(script_data)

        self.assertEqual(result["format"], "ai_video_prompts")
        self.assertEqual(result["video_mode"], "ai-prompts")
        self.assertEqual(result["scenes_count"], DEFAULT_MAX_SCENES)
        self.assertEqual(len(result["scenes"]), DEFAULT_MAX_SCENES)
        self.assertEqual(result["scenes"][0]["duration_seconds"], 4)
        self.assertIn("negative_prompt", result["scenes"][0])

    def test_save_visual_prompts(self):
        script_data = {
            "title": "VPN test",
            "topic": "VPN test",
            "visual_ideas": ["Scene one"],
        }

        with tempfile.TemporaryDirectory() as tmp:
            output_path = save_visual_prompts(script_data, output_dir=tmp)

            self.assertTrue(output_path.exists())

            data = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(data["format"], "ai_video_prompts")
            self.assertEqual(data["scenes_count"], 1)


if __name__ == "__main__":
    unittest.main()
