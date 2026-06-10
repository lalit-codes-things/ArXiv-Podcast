from __future__ import annotations

from importlib import import_module
from pathlib import Path


def _audio_segment():
    return import_module("pydub").AudioSegment


def concatenate_audio(audio_paths: list[str | Path], output_path: str | Path) -> str:
    """Concatenate spoken dialogue clips into one MP3 without extra audio assets."""
    if not audio_paths:
        raise ValueError("At least one audio path is required.")
    AudioSegment = _audio_segment()
    combined = AudioSegment.empty()
    for audio_path in audio_paths:
        combined += AudioSegment.from_file(audio_path)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    combined.export(output, format="mp3")
    return str(output)


def generate_waveform(audio_path: str | Path, output_path: str | Path) -> str:
    """Generate a PNG waveform image for an audio file."""
    plt = import_module("matplotlib.pyplot")
    audio = _audio_segment().from_file(audio_path)
    samples = audio.get_array_of_samples()
    if audio.channels > 1:
        samples = samples[:: audio.channels]
    duration = len(samples) / float(audio.frame_rate or 1)
    times = [index * duration / max(len(samples), 1) for index in range(len(samples))]

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(12, 3))
    plt.plot(times, samples, linewidth=0.4, color="#2563eb")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Amplitude")
    plt.tight_layout()
    plt.savefig(output)
    plt.close()
    return str(output)
