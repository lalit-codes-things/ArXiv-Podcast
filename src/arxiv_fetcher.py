from __future__ import annotations

from importlib import import_module
from pathlib import Path
from typing import Any

from src import config
from src.utils import LicenseNotAllowedException, check_license_allowed, get_paper_hash, sanitize_arxiv_id

arxiv = None


def fetch_paper(arxiv_id: str) -> dict[str, Any]:
    """Fetch arXiv metadata and download the PDF into the output temp directory."""
    arxiv_module = arxiv or import_module("arxiv")
    clean_id = sanitize_arxiv_id(arxiv_id)
    client = arxiv_module.Client()
    search = arxiv_module.Search(id_list=[clean_id], max_results=1)
    results = list(client.results(search))
    if not results:
        raise ValueError(f"No arXiv paper found for {clean_id}")

    paper = results[0]
    license_url = getattr(paper, "license", None)
    if not check_license_allowed(license_url):
        raise LicenseNotAllowedException(
            f"Paper {clean_id} uses a NoDerivatives license and cannot be adapted into a podcast."
        )

    config.ensure_directories()
    pdf_path = config.TEMP_DIR / f"{get_paper_hash(clean_id)}.pdf"
    downloaded = paper.download_pdf(dirpath=str(config.TEMP_DIR), filename=pdf_path.name)

    return {
        "arxiv_id": clean_id,
        "title": paper.title,
        "authors": [author.name for author in paper.authors],
        "summary": paper.summary,
        "published": paper.published.isoformat() if getattr(paper, "published", None) else None,
        "updated": paper.updated.isoformat() if getattr(paper, "updated", None) else None,
        "license": license_url,
        "pdf_url": getattr(paper, "pdf_url", None),
        "pdf_path": str(Path(downloaded)),
    }
