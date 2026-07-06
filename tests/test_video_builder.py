from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app"

if str(APP) not in sys.path:
    sys.path.insert(0, str(APP))

from video_builder import (
    build_ffmpeg_command,
    get_duration,
    safe_filename,
    save_video_stub,
)


class TestVideoBuilder(unittest.TestCase):
    def test_safe_filename(self):
        self.assertEqual(safe_filename("VPN в аэропорту"), "vpn_в_аэропорту")
        self.assertEqual(safe_filename("Wi-Fi / test"), "wi_fi_test")

    def test_get_duration(self):
        self.assertEqual(get_duration({"duration_seconds": 7}), 7.0)
        self.assertEqual(get_duration({"duration_seconds": "bad"}), 20.0)
        self.assertEqual(get_duration({"duration_seconds": -1}), 20.0)

    @unittest.skipIf(shutil.which("ffmpeg") is None, "FFmpeg is not installed")
    def test_build_ffmpeg_command(self):
        command = build_ffmpeg_command(
            {"duration_seconds": 2},
            Path("output/videos/test.mp4"),
        )

        self.assertIn("-f", command)
        self.assertIn("lavfi", command)
        self.assertIn("libx264", command)

    @unittest.skipIf(shutil.which("ffmpeg") is None, "FFmpeg is not installed")
    def test_save_video_stub(self):
        data = {"duration_seconds": 1}

        with tempfile.TemporaryDirectory() as tmp:
            path = save_video_stub(data, "VPN test", tmp)

            self.assertTrue(path.exists())
            self.assertEqual(path.suffix, ".mp4")
            self.assertGreater(path.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
