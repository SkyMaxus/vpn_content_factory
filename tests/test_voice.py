from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app"

if str(APP) not in sys.path:
    sys.path.insert(0, str(APP))

from voice import extract_voiceover_text, save_voiceover_stub


class TestVoice(unittest.TestCase):
    def test_extract_voiceover_text(self):
        data = {"voiceover_text": "Текст озвучки"}
        self.assertEqual(extract_voiceover_text(data), "Текст озвучки")

    def test_save_voiceover_stub(self):
        data = {"voiceover_text": "MM VPN — включил и пользуешься спокойнее."}

        with tempfile.TemporaryDirectory() as tmp:
            path = save_voiceover_stub(data, "VPN в аэропорту", tmp)

            self.assertTrue(path.exists())
            self.assertEqual(path.suffix, ".txt")
            self.assertIn("MM VPN", path.read_text(encoding="utf-8"))

    def test_empty_voiceover_raises_error(self):
        with self.assertRaises(ValueError):
            extract_voiceover_text({"voiceover_text": "   "})


if __name__ == "__main__":
    unittest.main()
