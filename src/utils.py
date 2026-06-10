from __future__ import annotations

import hashlib
import re
from pathlib import Path


class LicenseNotAllowedException(Exception):
    """Raised when a paper license forbids derivative works."""


def sanitize_arxiv_id(arxiv_id: str) -> str:
    """Normalize and validate an arXiv identifier."""
    cleaned = arxiv_id.strip().replace("arXiv:", "").replace("https://arxiv.org/abs/", "")
    cleaned = cleaned.replace("https://arxiv.org/pdf/", "").removesuffix(".pdf")
    if not re.fullmatch(r"(?:\d{4}\.\d{4,5})(?:v\d+)?|(?:[\w.-]+/\d{7})(?:v\d+)?", cleaned):
        raise ValueError(f"Invalid arXiv ID: {arxiv_id}")
    return cleaned


def get_paper_hash(arxiv_id: str) -> str:
    """Return a stable short hash for file naming."""
    return hashlib.sha256(sanitize_arxiv_id(arxiv_id).encode("utf-8")).hexdigest()[:12]


def check_license_allowed(license_url: str | None) -> bool:
    """Return False for Creative Commons NoDerivatives licenses."""
    if not license_url:
        return True
    normalized = license_url.lower()
    forbidden_terms = ("by-nc-nd", "by-nd")
    return not any(term in normalized for term in forbidden_terms)


def safe_unlink(path: str | Path) -> None:
    """Best-effort deletion for generated temporary files."""
    try:
        Path(path).unlink(missing_ok=True)
    except OSError:
        pass
