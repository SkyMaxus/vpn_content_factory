import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from app.video_builder import (
    VIDEO_HEIGHT,
    VIDEO_WIDTH,
    build_ffmpeg_command,
    get_duration,
    render_title_card,
    safe_filename,
    save_video_stub,
)


class TestVideoBuilder(unittest.TestCase):
    def test_safe_filename(self):
        topic = "VPN \u0432 \u0430\u044d\u0440\u043e\u043f\u043e\u0440\u0442\u0443"
        expected = "vpn_\u0432_\u0430\u044d\u0440\u043e\u043f\u043e\u0440\u0442\u0443"

        self.assertEqual(safe_filename(topic), expected)
        self.assertEqual(safe_filename('bad/name:*?'), "bad_name")
        self.assertEqual(safe_filename(""), "video")

    def test_get_duration(self):
        self.assertEqual(get_duration({"duration_seconds": 20}), 20)
        self.assertEqual(get_duration({"duration_seconds": "15"}), 15)
        self.assertEqual(get_duration({"duration_seconds": 2}), 5)
        self.assertEqual(get_duration({"duration_seconds": 999}), 60)
        self.assertEqual(get_duration({}), 20)

    def test_render_title_card_creates_png(self):
        script_data = {
            "title": "VPN \u0432 \u0430\u044d\u0440\u043e\u043f\u043e\u0440\u0442\u0443",
            "hook": "\u041e\u0442\u043a\u0440\u044b\u0442\u044b\u0439 Wi-Fi \u2014 \u043f\u043e\u0432\u043e\u0434 \u0431\u044b\u0442\u044c \u0432\u043d\u0438\u043c\u0430\u0442\u0435\u043b\u044c\u043d\u0435\u0435.",
            "cta": "MM VPN \u2014 \u0432\u043a\u043b\u044e\u0447\u0438\u043b \u0438 \u043f\u043e\u043b\u044c\u0437\u0443\u0435\u0448\u044c\u0441\u044f \u0441\u043f\u043e\u043a\u043e\u0439\u043d\u0435\u0435.",
        }

        with tempfile.TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "card.png"
            result = render_title_card(script_data, output_path)

            self.assertEqual(result, output_path)
            self.assertTrue(output_path.exists())

            with Image.open(output_path) as image:
                self.assertEqual(image.size, (VIDEO_WIDTH, VIDEO_HEIGHT))
                self.assertEqual(image.format, "PNG")

    def test_build_ffmpeg_command(self):
        command = build_ffmpeg_command(
            image_path="card.png",
            output_path="video.mp4",
            duration_seconds=20,
        )

        self.assertIn("-loop", command)
        self.assertIn("card.png", command)
        self.assertIn("video.mp4", command)
        self.assertIn("20", command)
        self.assertIn(f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}", command)

    def test_save_video_stub(self):
        topic = "VPN \u0432 \u0430\u044d\u0440\u043e\u043f\u043e\u0440\u0442\u0443"
        expected_file = "vpn_\u0432_\u0430\u044d\u0440\u043e\u043f\u043e\u0440\u0442\u0443.mp4"
        expected_card = "vpn_\u0432_\u0430\u044d\u0440\u043e\u043f\u043e\u0440\u0442\u0443_card.png"

        script_data = {
            "topic": topic,
            "title": topic,
            "hook": "\u041e\u0442\u043a\u0440\u044b\u0442\u044b\u0439 Wi-Fi \u2014 \u043f\u043e\u0432\u043e\u0434 \u0431\u044b\u0442\u044c \u0432\u043d\u0438\u043c\u0430\u0442\u0435\u043b\u044c\u043d\u0435\u0435.",
            "cta": "MM VPN \u2014 \u0432\u043a\u043b\u044e\u0447\u0438\u043b \u0438 \u043f\u043e\u043b\u044c\u0437\u0443\u0435\u0448\u044c\u0441\u044f \u0441\u043f\u043e\u043a\u043e\u0439\u043d\u0435\u0435.",
            "duration_seconds": 20,
        }

        with tempfile.TemporaryDirectory() as tmp:
            with patch("app.video_builder.subprocess.run") as mocked_run:
                result = save_video_stub(script_data, output_dir=tmp)

            self.assertEqual(result.name, expected_file)
            self.assertTrue((Path(tmp) / expected_card).exists())
            mocked_run.assert_called_once()


if __name__ == "__main__":
    unittest.main()
