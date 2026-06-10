from __future__ import annotations

import pytest

from src.job_manager import create_job, get_job, update_job
from src.utils import check_license_allowed, get_paper_hash, sanitize_arxiv_id


def test_utils_license_and_hash():
    assert sanitize_arxiv_id("arXiv:2401.00001") == "2401.00001"
    assert len(get_paper_hash("2401.00001")) == 12
    assert check_license_allowed("https://creativecommons.org/licenses/by/4.0/")
    assert not check_license_allowed("https://creativecommons.org/licenses/by-nd/4.0/")


def test_job_manager_lifecycle():
    job = create_job("2401.00001")
    updated = update_job(job["job_id"], status="running", message="working")

    assert updated["status"] == "running"
    assert get_job(job["job_id"])["message"] == "working"


def test_split_script_lines_handles_continuations():
    pytest.importorskip("fastapi")
    from src import main

    script = "Host: Welcome\nThis continues.\nExpert: Thanks\nMore expert detail."

    lines = main.split_script_lines(script)

    assert lines == [("Host", "Welcome This continues."), ("Expert", "Thanks More expert detail.")]
