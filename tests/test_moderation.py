"""Tests for moderation module."""

import unittest

from app.moderation import ModerationError, assert_safe_script, check_script_data, check_text


class TestModeration(unittest.TestCase):
    def test_blocks_100_percent_anonymity(self):
        result = check_text("\u041d\u0430\u0448 VPN \u0434\u0430\u0435\u0442 100% \u0430\u043d\u043e\u043d\u0438\u043c\u043d\u043e\u0441\u0442\u044c \u0432 \u0438\u043d\u0442\u0435\u0440\u043d\u0435\u0442\u0435.")
        self.assertFalse(result["is_safe"])

    def test_blocks_impossible_to_track(self):
        result = check_text("\u0421 \u044d\u0442\u0438\u043c VPN \u0442\u0435\u0431\u044f \u043d\u0435\u0432\u043e\u0437\u043c\u043e\u0436\u043d\u043e \u043e\u0442\u0441\u043b\u0435\u0434\u0438\u0442\u044c.")
        self.assertFalse(result["is_safe"])

    def test_blocks_hack_restrictions(self):
        result = check_text("VPN \u043f\u043e\u043c\u043e\u0436\u0435\u0442 \u0441\u0434\u0435\u043b\u0430\u0442\u044c \u0432\u0437\u043b\u043e\u043c \u043e\u0433\u0440\u0430\u043d\u0438\u0447\u0435\u043d\u0438\u0439.")
        self.assertFalse(result["is_safe"])

    def test_allows_safe_wifi_wording(self):
        result = check_text("VPN \u043f\u043e\u043c\u043e\u0433\u0430\u0435\u0442 \u0437\u0430\u0449\u0438\u0442\u0438\u0442\u044c \u0442\u0440\u0430\u0444\u0438\u043a \u0432 \u043f\u0443\u0431\u043b\u0438\u0447\u043d\u044b\u0445 \u0441\u0435\u0442\u044f\u0445.")
        self.assertTrue(result["is_safe"])

    def test_script_data_raises_error(self):
        script = {
            "title": "Bad offer",
            "script": "\u0413\u0430\u0440\u0430\u043d\u0442\u0438\u0440\u043e\u0432\u0430\u043d\u043d\u0430\u044f \u0437\u0430\u0449\u0438\u0442\u0430 \u043e\u0442 \u0432\u0441\u0435\u0433\u043e.",
            "subtitles": ["Bad promise"],
        }

        with self.assertRaises(ModerationError):
            assert_safe_script(script)

    def test_safe_script_data_passes(self):
        script = {
            "title": "Public Wi-Fi",
            "script": "VPN \u0441\u043e\u0437\u0434\u0430\u0435\u0442 \u0437\u0430\u0449\u0438\u0449\u0435\u043d\u043d\u044b\u0439 \u0442\u0443\u043d\u043d\u0435\u043b\u044c \u043c\u0435\u0436\u0434\u0443 \u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u043e\u043c \u0438 \u0441\u0435\u0440\u0432\u0435\u0440\u043e\u043c.",
            "subtitles": ["Safe wording"],
        }

        result = check_script_data(script)
        self.assertTrue(result["is_safe"])


if __name__ == "__main__":
    unittest.main()
