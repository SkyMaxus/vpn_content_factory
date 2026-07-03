"""Project settings loader."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*args, **kwargs) -> bool:
        return False


@dataclass(frozen=True)
class Settings:
    brand_name: str
    cta_text: str
    output_dir: str
    safe_mode: bool
    ai_provider: str
    ai_mode: str
    ai_model: str
    ai_api_key: str
    openai_api_key: str


def _as_bool(value: str | None, default: bool = True) -> bool:
    if value is None:
        return default
    return value.strip().lower() not in {"0", "false", "no", "off", "нет"}


def load_settings(env_path: str | Path = ".env") -> Settings:
    load_dotenv(env_path)

    brand_name = os.getenv("BRAND_NAME", "MM VPN").strip() or "MM VPN"
    ai_provider = os.getenv("AI_PROVIDER", "mock").strip().lower() or "mock"
    ai_mode = os.getenv("AI_MODE", "mock").strip().lower() or "mock"
    ai_model = os.getenv("AI_MODEL", "gpt-5.5").strip() or "gpt-5.5"
    ai_api_key = os.getenv("AI_API_KEY", "").strip()
    openai_api_key = os.getenv("OPENAI_API_KEY", ai_api_key).strip()

    return Settings(
        brand_name=brand_name,
        cta_text=os.getenv(
            "CTA_TEXT",
            f"{brand_name} — включил и пользуешься спокойнее.",
        ).strip(),
        output_dir=os.getenv("OUTPUT_DIR", "output/scripts").strip() or "output/scripts",
        safe_mode=_as_bool(os.getenv("SAFE_MODE"), default=True),
        ai_provider=ai_provider,
        ai_mode=ai_mode,
        ai_model=ai_model,
        ai_api_key=ai_api_key,
        openai_api_key=openai_api_key,
    )
