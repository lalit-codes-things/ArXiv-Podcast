from __future__ import annotations

from importlib import import_module
from typing import Any

from src import config


def _load_prompt() -> str:
    return (config.PROMPTS_DIR / "script_generator_prompt.txt").read_text(encoding="utf-8")


def generate_script(metadata: dict[str, Any], summary: str, model: str = "gpt-3.5-turbo") -> str:
    """Generate a long Host/Expert dialogue script."""
    if not config.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is required for script generation.")
    prompt = _load_prompt().format(metadata=metadata, summary=summary)
    client = OpenAI(api_key=config.OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=3000,
    )
    return response.choices[0].message.content.strip()


def OpenAI(api_key: str):
    """Construct an OpenAI client lazily so tests can monkeypatch this symbol."""
    return import_module("openai").OpenAI(api_key=api_key)
