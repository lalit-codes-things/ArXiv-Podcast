from __future__ import annotations

import os
from importlib import import_module, util
from pathlib import Path

if util.find_spec("dotenv"):
    import_module("dotenv").load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
PROMPTS_DIR = BASE_DIR / "prompts"
FRONTEND_DIR = BASE_DIR / "frontend"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
TTS_ENGINE = os.getenv("TTS_ENGINE", "edge").strip().lower()
TTS_VOICE = os.getenv("TTS_VOICE", "en-GB-RyanNeural")
MAX_SCRIPT_DURATION_SECONDS = int(os.getenv("MAX_SCRIPT_DURATION_SECONDS", "1200"))
TARGET_DURATION_SECONDS = int(os.getenv("TARGET_DURATION_SECONDS", "600"))
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", str(BASE_DIR / "output")))
TEMP_DIR = OUTPUT_DIR / "tmp"


def ensure_directories() -> None:
    """Create runtime output directories if they do not already exist."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)


ensure_directories()
