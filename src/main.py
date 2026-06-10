from __future__ import annotations

import re
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src import config
from src.arxiv_fetcher import fetch_paper
from src.audio_mixer import concatenate_audio, generate_waveform
from src.job_manager import create_job, get_job, update_job
from src.pdf_parser import extract_sections
from src.script_generator import generate_script
from src.summarizer import summarize
from src.tts_engine import text_to_speech
from src.utils import LicenseNotAllowedException, get_paper_hash, safe_unlink, sanitize_arxiv_id

app = FastAPI(title="ArXiv Podcast")
config.ensure_directories()
app.mount("/output", StaticFiles(directory=str(config.OUTPUT_DIR)), name="output")
if (config.FRONTEND_DIST_DIR / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(config.FRONTEND_DIST_DIR / "assets")), name="assets")
app = FastAPI(title="Paper to Podcast")
config.ensure_directories()
app.mount("/output", StaticFiles(directory=str(config.OUTPUT_DIR)), name="output")


class GenerateRequest(BaseModel):
    arxiv_id: str


def _combine_sections(sections: dict) -> str:
    preferred = "\n\n".join(
        value for key, value in sections.items() if key in {"abstract", "introduction", "conclusion"} and value
    )
    return preferred or sections.get("full_text", "")[:50000]


def split_script_lines(script: str) -> list[tuple[str, str]]:
    """Split script into ordered (speaker, text) lines for synthesis."""
    lines: list[tuple[str, str]] = []
    current_speaker: str | None = None
    current_text: list[str] = []
    for raw_line in script.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        match = re.match(r"^(Host|Expert):\s*(.*)$", line, flags=re.IGNORECASE)
        if match:
            if current_speaker and current_text:
                lines.append((current_speaker, " ".join(current_text).strip()))
            current_speaker = match.group(1).title()
            current_text = [match.group(2).strip()]
        elif current_speaker:
            current_text.append(line)
    if current_speaker and current_text:
        lines.append((current_speaker, " ".join(current_text).strip()))
    return [(speaker, text) for speaker, text in lines if text]


def _public_output_url(path: str | Path) -> str:
    return f"/output/{Path(path).name}"


def run_pipeline(job_id: str, arxiv_id: str) -> None:
    """Run the complete ArXiv Podcast workflow for a background job."""
    """Run the complete paper-to-podcast workflow for a background job."""
    temp_files: list[str] = []
    try:
        clean_id = sanitize_arxiv_id(arxiv_id)
        paper_hash = get_paper_hash(clean_id)
        update_job(job_id, status="running", message="Fetching arXiv paper")
        metadata = fetch_paper(clean_id)

        update_job(job_id, message="Parsing PDF")
        sections = extract_sections(metadata["pdf_path"])

        update_job(job_id, message="Summarizing paper")
        summary = summarize(_combine_sections(sections))

        update_job(job_id, message="Generating 10+ minute podcast script")
        script = generate_script(metadata, summary)
        dialogue_lines = split_script_lines(script)
        if not dialogue_lines:
            raise RuntimeError("Generated script did not contain Host:/Expert: lines.")

        update_job(job_id, message="Synthesizing speech")
        audio_segments: list[str] = []
        for index, (speaker, text) in enumerate(dialogue_lines, start=1):
            segment_path = config.TEMP_DIR / f"{paper_hash}_{index:03d}_{speaker.lower()}.mp3"
            audio_segments.append(text_to_speech(text, segment_path))
            temp_files.append(str(segment_path))

        update_job(job_id, message="Combining dialogue audio")
        podcast_path = config.OUTPUT_DIR / f"{paper_hash}.mp3"
        waveform_path = config.OUTPUT_DIR / f"{paper_hash}.png"
        concatenate_audio(audio_segments, podcast_path)
        generate_waveform(podcast_path, waveform_path)

        update_job(
            job_id,
            status="completed",
            message="Podcast generated",
            result={
                "audio_url": _public_output_url(podcast_path),
                "waveform_url": _public_output_url(waveform_path),
                "metadata": metadata,
                "summary": summary,
            },
        )
    except LicenseNotAllowedException as exc:
        update_job(job_id, status="failed", message="License rejected", error=str(exc))
    except Exception as exc:
        update_job(job_id, status="failed", message="Pipeline failed", error=str(exc))
    finally:
        for path in temp_files:
            safe_unlink(path)


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    index_path = config.FRONTEND_DIST_DIR / "index.html"
    if not index_path.exists():
        index_path = config.FRONTEND_DIR / "index.html"
    return HTMLResponse(index_path.read_text(encoding="utf-8"))
    return HTMLResponse((config.FRONTEND_DIR / "index.html").read_text(encoding="utf-8"))


@app.post("/api/generate")
def generate(request: GenerateRequest, background_tasks: BackgroundTasks) -> dict:
    try:
        clean_id = sanitize_arxiv_id(request.arxiv_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    job = create_job(clean_id)
    background_tasks.add_task(run_pipeline, job["job_id"], clean_id)
    return {"job_id": job["job_id"], "status": job["status"]}


@app.get("/api/status/{job_id}")
def status(job_id: str) -> dict:
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.get("/api/download/{filename}")
def download(filename: str) -> FileResponse:
    path = config.OUTPUT_DIR / Path(filename).name
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path)
