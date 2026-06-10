from __future__ import annotations

from types import SimpleNamespace

from src import script_generator


class DummyCompletions:
    def create(self, **kwargs):
        assert "summary" in kwargs["messages"][0]["content"]
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="Host: Hi\nExpert: Hello"))])


class DummyClient:
    def __init__(self, api_key: str) -> None:
        self.chat = SimpleNamespace(completions=DummyCompletions())


def test_generate_script_uses_prompt(monkeypatch):
    monkeypatch.setattr(script_generator.config, "OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(script_generator, "OpenAI", DummyClient)

    script = script_generator.generate_script({"title": "T"}, "summary")

    assert script.startswith("Host:")
