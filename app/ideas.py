"""Topic loader and random idea picker for local MVP."""

from __future__ import annotations

import json
import random
from pathlib import Path


DEFAULT_TOPICS = [
    "\u043e\u043f\u0430\u0441\u043d\u043e\u0441\u0442\u044c \u043f\u0443\u0431\u043b\u0438\u0447\u043d\u043e\u0433\u043e Wi-Fi",
    "VPN \u0432 \u043f\u043e\u0435\u0437\u0434\u043a\u0435",
    "\u043a\u0430\u043a \u0432\u043a\u043b\u044e\u0447\u0438\u0442\u044c VPN \u043d\u0430 \u0442\u0435\u043b\u0435\u0444\u043e\u043d\u0435",
]


def load_topics(path: str = "data/content_topics.json") -> list[str]:
    file_path = Path(path)

    if not file_path.exists():
        return DEFAULT_TOPICS.copy()

    raw = json.loads(file_path.read_text(encoding="utf-8"))

    if not isinstance(raw, list):
        raise ValueError("Topics file must contain a JSON list.")

    topics: list[str] = []
    seen: set[str] = set()

    for item in raw:
        if not isinstance(item, str):
            continue

        topic = item.strip()
        key = topic.lower()

        if topic and key not in seen:
            topics.append(topic)
            seen.add(key)

    if not topics:
        raise ValueError("Topics file has no valid topics.")

    return topics


def choose_random_topic(path: str = "data/content_topics.json", seed: int | None = None) -> str:
    topics = load_topics(path)
    rng = random.Random(seed)
    return rng.choice(topics)
