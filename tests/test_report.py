"""Tests for report generation."""

import json

from llm_gateway_bench.report import generate_report


def test_generate_report_json(tmp_path, sample_result):
    path = tmp_path / "report.json"
    generate_report([sample_result], str(path))
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data[0]["provider"] == "openai"


def test_generate_report_markdown(tmp_path, sample_result):
    path = tmp_path / "report.md"
    generate_report([sample_result], str(path))
    content = path.read_text(encoding="utf-8")
    assert "openai" in content
    assert "gpt-4o-mini" in content
