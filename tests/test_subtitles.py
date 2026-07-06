from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app"

if str(APP) not in sys.path:
    sys.path.insert(0, str(APP))

from subtitles import (
    build_srt,
    extract_subtitle_lines,
    format_srt_time,
    save_subtitles_srt,
)


class TestSubtitles(unittest.TestCase):
    def test_format_srt_time(self):
        self.assertEqual(format_srt_time(0), "00:00:00,000")
        self.assertEqual(format_srt_time(1.5), "00:00:01,500")
        self.assertEqual(format_srt_time(65), "00:01:05,000")

    def test_extract_subtitle_lines(self):
        data = {
            "subtitles": [
                "ервая строка",
                "   ",
                123,
                "торая строка",
            ]
        }

        self.assertEqual(
            extract_subtitle_lines(data),
            ["ервая строка", "торая строка"],
        )

    def test_build_srt(self):
        srt = build_srt(["ервая", "торая"], duration_seconds=4)

        self.assertIn("1", srt)
        self.assertIn("00:00:00,000 --> 00:00:02,000", srt)
        self.assertIn("00:00:02,000 --> 00:00:04,000", srt)
        self.assertIn("ервая", srt)
        self.assertIn("торая", srt)

    def test_save_subtitles_srt(self):
        data = {
            "duration_seconds": 4,
            "subtitles": ["MM VPN", "ользуйся спокойнее"],
        }

        with tempfile.TemporaryDirectory() as tmp:
            path = save_subtitles_srt(data, "VPN в аэропорту", tmp)

            self.assertTrue(path.exists())
            self.assertEqual(path.suffix, ".srt")
            content = path.read_text(encoding="utf-8")
            self.assertIn("MM VPN", content)
            self.assertIn("00:00:00,000", content)

    def test_empty_subtitles_raise_error(self):
        with self.assertRaises(ValueError):
            extract_subtitle_lines({"subtitles": []})


if __name__ == "__main__":
    unittest.main()
