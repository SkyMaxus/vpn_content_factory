"""Tests for topic loading and random idea picking."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from app.ideas import choose_random_topic, load_topics


class TestIdeas(unittest.TestCase):
    def test_load_topics_from_json_list(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "topics.json"
            path.write_text(json.dumps(["one", "two"], ensure_ascii=False), encoding="utf-8")

            self.assertEqual(load_topics(str(path)), ["one", "two"])

    def test_load_topics_removes_duplicates_and_empty_values(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "topics.json"
            path.write_text(json.dumps(["one", " ", "one", "Two"], ensure_ascii=False), encoding="utf-8")

            self.assertEqual(load_topics(str(path)), ["one", "Two"])

    def test_choose_random_topic_is_stable_with_seed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "topics.json"
            path.write_text(json.dumps(["a", "b", "c"], ensure_ascii=False), encoding="utf-8")

            first = choose_random_topic(str(path), seed=123)
            second = choose_random_topic(str(path), seed=123)

            self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
