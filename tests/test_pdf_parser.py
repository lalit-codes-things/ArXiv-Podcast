from __future__ import annotations

from src import pdf_parser


def test_extract_sections_from_mocked_text(monkeypatch):
    text = "Abstract\nA short abstract.\nIntroduction\nImportant context.\nConclusion\nFinal notes.\nReferences\n[1]"
    monkeypatch.setattr(pdf_parser, "extract_text", lambda path: text)

    sections = pdf_parser.extract_sections("dummy.pdf")

    assert "short abstract" in sections["abstract"]
    assert "Important context" in sections["introduction"]
    assert "Final notes" in sections["conclusion"]
