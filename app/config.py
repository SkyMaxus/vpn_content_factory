"""Config for local MVP."""

import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv() -> None:
        return None


@dataclass(frozen=True)
class Settings:
    brand_name: str
    cta_text: str
    output_dir: str
    safe_mode: bool


def load_settings() -> Settings:
    load_dotenv()

    brand_name = os.getenv("BRAND_NAME", "MM VPN")
    cta_text = os.getenv("CTA_TEXT", f"{brand_name} — включил и пользуешься спокойнее.")
    output_dir = os.getenv("OUTPUT_DIR", "output/scripts")
    safe_mode = os.getenv("SAFE_MODE", "true").lower() in {"1", "true", "yes", "on"}

    return Settings(
        brand_name=brand_name,
        cta_text=cta_text,
        output_dir=output_dir,
        safe_mode=safe_mode,
    )
