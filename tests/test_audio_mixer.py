from __future__ import annotations

import pytest

pytest.importorskip("pydub")
from pydub import AudioSegment

from src.audio_mixer import concatenate_audio, generate_waveform


def test_concatenate_audio_and_waveform(tmp_path):
    first = tmp_path / "first.wav"
    second = tmp_path / "second.wav"
    AudioSegment.silent(duration=100).export(first, format="wav")
    AudioSegment.silent(duration=100).export(second, format="wav")

    mp3 = concatenate_audio([first, second], tmp_path / "combined.mp3")
    png = generate_waveform(mp3, tmp_path / "waveform.png")

    assert (tmp_path / "combined.mp3").exists()
    assert (tmp_path / "waveform.png").exists()
    assert mp3.endswith("combined.mp3")
    assert png.endswith("waveform.png")
