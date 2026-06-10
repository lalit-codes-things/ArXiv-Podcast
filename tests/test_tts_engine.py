from __future__ import annotations

import pytest

from src import tts_engine


def test_text_to_speech_edge_mock(monkeypatch, tmp_path):
    async def fake_edge(text, output_path, voice):
        output_path.write_bytes(b"audio")

    monkeypatch.setattr(tts_engine.config, "TTS_ENGINE", "edge")
    monkeypatch.setattr(tts_engine, "_edge_tts", fake_edge)

    output = tts_engine.text_to_speech("hello", tmp_path / "out.mp3", voice="en-GB-RyanNeural")

    assert (tmp_path / "out.mp3").read_bytes() == b"audio"
    assert output.endswith("out.mp3")


def test_text_to_speech_rejects_empty(tmp_path):
    with pytest.raises(ValueError):
        tts_engine.text_to_speech("   ", tmp_path / "out.mp3")
