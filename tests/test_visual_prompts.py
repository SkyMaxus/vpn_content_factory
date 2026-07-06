import json
import tempfile
import unittest
from pathlib import Path

from app.visual_prompts import (
    build_video_prompt,
    contains_cyrillic,
    extract_scene_sources,
    generate_visual_prompts,
    normalize_text,
    safe_filename,
    save_visual_prompts,
)


class TestVisualPrompts(unittest.TestCase):
    def sample_script_data(self):
        return {
            "title": "VPN \u0432 \u0430\u044d\u0440\u043e\u043f\u043e\u0440\u0442\u0443: \u0441\u043f\u043e\u043a\u043e\u0439\u043d\u0435\u0435 \u0432 Wi-Fi",
            "topic": "VPN \u0432 \u0430\u044d\u0440\u043e\u043f\u043e\u0440\u0442\u0443",
            "duration_seconds": 20,
            "hook": "\u0410\u044d\u0440\u043e\u043f\u043e\u0440\u0442, \u043e\u0442\u043a\u0440\u044b\u0442\u044b\u0439 Wi-Fi \u0438 \u0441\u0440\u043e\u0447\u043d\u044b\u0435 \u0434\u0435\u043b\u0430?",
            "script": "1) \u041a\u0430\u0434\u0440: \u0447\u0435\u043b\u043e\u0432\u0435\u043a \u0432 \u0430\u044d\u0440\u043e\u043f\u043e\u0440\u0442\u0443 \u043f\u043e\u0434\u043a\u043b\u044e\u0447\u0430\u0435\u0442\u0441\u044f \u043a Wi-Fi.",
            "subtitles": [
                "\u0410\u044d\u0440\u043e\u043f\u043e\u0440\u0442, Wi-Fi \u0438 \u0441\u0440\u043e\u0447\u043d\u044b\u0435 \u0434\u0435\u043b\u0430?",
                "MM VPN \u043f\u043e\u043c\u043e\u0433\u0430\u0435\u0442 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u044c\u0441\u044f \u0438\u043d\u0442\u0435\u0440\u043d\u0435\u0442\u043e\u043c \u0441\u043f\u043e\u043a\u043e\u0439\u043d\u0435\u0435.",
            ],
            "cta": "MM VPN — \u0432\u043a\u043b\u044e\u0447\u0438\u043b \u0438 \u043f\u043e\u043b\u044c\u0437\u0443\u0435\u0448\u044c\u0441\u044f \u0441\u043f\u043e\u043a\u043e\u0439\u043d\u0435\u0435.",
            "visual_ideas": [
                "\u0422\u0435\u0440\u043c\u0438\u043d\u0430\u043b \u0430\u044d\u0440\u043e\u043f\u043e\u0440\u0442\u0430, \u043b\u044e\u0434\u0438 \u0441 \u0447\u0435\u043c\u043e\u0434\u0430\u043d\u0430\u043c\u0438",
                "\u0421\u043c\u0430\u0440\u0442\u0444\u043e\u043d \u043f\u043e\u0434\u043a\u043b\u044e\u0447\u0430\u0435\u0442\u0441\u044f \u043a public Wi-Fi",
                "\u0424\u0438\u043d\u0430\u043b\u044c\u043d\u044b\u0439 \u044d\u043a\u0440\u0430\u043d \u0441 \u0431\u0440\u0435\u043d\u0434\u043e\u043c \u0438 CTA",
            ],
        }

    def test_normalize_text(self):
        self.assertEqual(normalize_text("  VPN\u00a0\u2011 Wi\u2011Fi  "), "VPN - Wi-Fi")

    def test_safe_filename(self):
        self.assertEqual(safe_filename("VPN / airport: test?"), "vpn_airport_test")

    def test_build_video_prompt_has_no_cyrillic(self):
        prompt = build_video_prompt("\u0410\u044d\u0440\u043e\u043f\u043e\u0440\u0442, \u043f\u0443\u0431\u043b\u0438\u0447\u043d\u044b\u0439 Wi-Fi", 1, 4)

        self.assertIn("Vertical 9:16", prompt)
        self.assertIn("airport", prompt.lower())
        self.assertFalse(contains_cyrillic(prompt))

    def test_extract_scene_sources_prefers_visual_ideas(self):
        sources = extract_scene_sources(self.sample_script_data())

        self.assertEqual(len(sources), 3)
        self.assertIn("\u0422\u0435\u0440\u043c\u0438\u043d\u0430\u043b", sources[0])

    def test_extract_scene_sources_fallback_to_hook(self):
        data = {
            "hook": "\u041a\u0430\u0444\u0435, Wi-Fi \u0438 \u0440\u0430\u0431\u043e\u0447\u0438\u0435 \u0434\u0435\u043b\u0430?"
        }

        sources = extract_scene_sources(data)

        self.assertEqual(sources, ["\u041a\u0430\u0444\u0435, Wi-Fi \u0438 \u0440\u0430\u0431\u043e\u0447\u0438\u0435 \u0434\u0435\u043b\u0430?"])

    def test_generate_visual_prompts_uses_source_ru_and_prompt_en(self):
        data = generate_visual_prompts(self.sample_script_data())

        self.assertEqual(data["format"], "ai_video_prompts")
        self.assertEqual(data["aspect_ratio"], "9:16")
        self.assertEqual(data["scenes_count"], 3)

        first_scene = data["scenes"][0]

        self.assertIn("source_ru", first_scene)
        self.assertIn("prompt_en", first_scene)
        self.assertIn("subtitle_ru", first_scene)
        self.assertIn("cta_ru", first_scene)
        self.assertNotIn("source", first_scene)
        self.assertNotIn("prompt", first_scene)
        self.assertTrue(contains_cyrillic(first_scene["source_ru"]))
        self.assertFalse(contains_cyrillic(first_scene["prompt_en"]))

    def test_final_scene_has_cta_ru(self):
        data = generate_visual_prompts(self.sample_script_data())

        self.assertEqual(data["scenes"][0]["cta_ru"], "")
        self.assertTrue(contains_cyrillic(data["scenes"][-1]["cta_ru"]))

    def test_save_visual_prompts(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = save_visual_prompts(
                self.sample_script_data(),
                topic="vpn_test",
                output_dir=temp_dir,
            )

            self.assertTrue(path.exists())
            self.assertEqual(path.name, "vpn_test_visual_prompts.json")

            saved = json.loads(Path(path).read_text(encoding="utf-8"))
            self.assertIn("source_ru", saved["scenes"][0])
            self.assertIn("prompt_en", saved["scenes"][0])
            self.assertFalse(contains_cyrillic(saved["scenes"][0]["prompt_en"]))


if __name__ == "__main__":
    unittest.main()
