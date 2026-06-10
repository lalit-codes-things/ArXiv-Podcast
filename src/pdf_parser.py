from __future__ import annotations

import re
from importlib import import_module
from pathlib import Path
from typing import Any


def extract_text(pdf_path: str | Path) -> str:
    """Extract all text from a PDF using PyMuPDF."""
    fitz = import_module("fitz")
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(path)
    chunks: list[str] = []
    with fitz.open(path) as doc:
        for page in doc:
            chunks.append(page.get_text("text"))
    return "\n".join(chunks).strip()


def _extract_section(text: str, names: tuple[str, ...], stop_names: tuple[str, ...]) -> str:
    name_pattern = "|".join(re.escape(name) for name in names)
    stop_pattern = "|".join(re.escape(name) for name in stop_names)
    pattern = re.compile(
        rf"(?ims)^\s*(?:\d+\.?\s*)?(?:{name_pattern})\s*$\n(?P<body>.*?)(?=^\s*(?:\d+\.?\s*)?(?:{stop_pattern})\s*$|\Z)"
    )
    match = pattern.search(text)
    return re.sub(r"\s+", " ", match.group("body")).strip() if match else ""


def extract_sections(pdf_path: str | Path) -> dict[str, Any]:
    """Extract full text plus common high-value paper sections."""
    text = extract_text(pdf_path)
    sections = {
        "abstract": _extract_section(text, ("abstract",), ("introduction", "1 introduction")),
        "introduction": _extract_section(
            text,
            ("introduction", "1 introduction"),
            ("related work", "background", "methods", "method", "approach", "conclusion", "conclusions"),
        ),
        "conclusion": _extract_section(
            text,
            ("conclusion", "conclusions", "discussion and conclusion"),
            ("references", "bibliography", "appendix", "acknowledgements", "acknowledgments"),
        ),
        "full_text": text,
    }
    return sections
