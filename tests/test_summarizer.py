from __future__ import annotations

from types import SimpleNamespace

from src import summarizer


class DummyCompletions:
    def create(self, **kwargs):
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="- summary"))])


class DummyClient:
    def __init__(self, api_key: str) -> None:
        self.chat = SimpleNamespace(completions=DummyCompletions())


def test_summarize_uses_openai(monkeypatch):
    monkeypatch.setattr(summarizer.config, "OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(summarizer, "OpenAI", DummyClient)

    assert summarizer.summarize("paper text") == "- summary"
