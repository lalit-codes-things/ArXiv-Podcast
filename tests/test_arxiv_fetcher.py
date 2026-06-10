from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from src import arxiv_fetcher
from src.utils import LicenseNotAllowedException


class DummyAuthor:
    def __init__(self, name: str) -> None:
        self.name = name


class DummyPaper:
    title = "A Test Paper"
    authors = [DummyAuthor("Ada Lovelace")]
    summary = "summary"
    published = None
    updated = None
    license = "https://creativecommons.org/licenses/by/4.0/"
    pdf_url = "https://arxiv.org/pdf/2401.00001"

    def download_pdf(self, dirpath: str, filename: str) -> str:
        path = Path(dirpath) / filename
        path.write_bytes(b"%PDF test")
        return str(path)


def test_fetch_paper_downloads_metadata(monkeypatch, tmp_path):
    monkeypatch.setattr(arxiv_fetcher.config, "TEMP_DIR", tmp_path)
    monkeypatch.setattr(arxiv_fetcher.config, "OUTPUT_DIR", tmp_path)
    monkeypatch.setattr(arxiv_fetcher, "arxiv", SimpleNamespace(
        Search=lambda **kwargs: SimpleNamespace(**kwargs),
        Client=lambda: SimpleNamespace(results=lambda search: [DummyPaper()]),
    ))

    result = arxiv_fetcher.fetch_paper("2401.00001")

    assert result["title"] == "A Test Paper"
    assert result["authors"] == ["Ada Lovelace"]
    assert Path(result["pdf_path"]).exists()


def test_fetch_paper_rejects_no_derivatives(monkeypatch, tmp_path):
    class ForbiddenPaper(DummyPaper):
        license = "https://creativecommons.org/licenses/by-nc-nd/4.0/"

    monkeypatch.setattr(arxiv_fetcher.config, "TEMP_DIR", tmp_path)
    monkeypatch.setattr(arxiv_fetcher, "arxiv", SimpleNamespace(
        Search=lambda **kwargs: SimpleNamespace(**kwargs),
        Client=lambda: SimpleNamespace(results=lambda search: [ForbiddenPaper()]),
    ))

    with pytest.raises(LicenseNotAllowedException):
        arxiv_fetcher.fetch_paper("2401.00001")
