from __future__ import annotations

import asyncio
from importlib import import_module, util
from pathlib import Path

from src import config


async def _edge_tts(text: str, output_path: Path, voice: str) -> None:
    edge_tts = import_module("edge_tts")
    communicate = edge_tts.Communicate(text=text, voice=voice)
    await communicate.save(str(output_path))


def _kokoro_tts(text: str, output_path: Path, voice: str) -> None:
    if not util.find_spec("kokoro") or not util.find_spec("soundfile"):
        raise RuntimeError("Kokoro TTS requires optional packages: kokoro and soundfile.")
    sf = import_module("soundfile")
    kokoro = import_module("kokoro")
    np = import_module("numpy")

    pipeline = kokoro.KPipeline(lang_code="a")
    audio_chunks = []
    sample_rate = 24000
    for _, _, audio in pipeline(text, voice=voice):
        audio_chunks.append(audio)
    if not audio_chunks:
        raise RuntimeError("Kokoro produced no audio.")
    sf.write(output_path, np.concatenate(audio_chunks), sample_rate)


def text_to_speech(text: str, output_path: str | Path, voice: str | None = None) -> str:
    """Synthesize text to an audio file using Edge TTS or optional Kokoro."""
    if not text.strip():
        raise ValueError("Cannot synthesize empty text.")
    config.ensure_directories()
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    selected_voice = voice or config.TTS_VOICE

    if config.TTS_ENGINE == "edge":
        try:
            asyncio.run(_edge_tts(text, path, selected_voice))
        except RuntimeError:
            loop = asyncio.new_event_loop()
            try:
                loop.run_until_complete(_edge_tts(text, path, selected_voice))
            finally:
                loop.close()
    elif config.TTS_ENGINE == "kokoro":
        _kokoro_tts(text, path, selected_voice)
    else:
        raise ValueError(f"Unsupported TTS_ENGINE: {config.TTS_ENGINE}")
    return str(path)
