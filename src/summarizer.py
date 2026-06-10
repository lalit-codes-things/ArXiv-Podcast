from __future__ import annotations

from importlib import import_module

from src import config


def _load_prompt() -> str:
    return (config.PROMPTS_DIR / "summarizer_prompt.txt").read_text(encoding="utf-8")


def summarize(content: str, model: str = "gpt-3.5-turbo") -> str:
    """Summarize extracted paper content with OpenAI chat completions."""
    if not config.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is required for summarization.")
    prompt = _load_prompt().format(content=content[:50000])
    client = OpenAI(api_key=config.OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()


def OpenAI(api_key: str):
    """Construct an OpenAI client lazily so tests can monkeypatch this symbol."""
    return import_module("openai").OpenAI(api_key=api_key)
