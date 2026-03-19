"""CLI tests for llm_gateway_bench."""

from click.testing import CliRunner

from llm_gateway_bench.cli import cli
from llm_gateway_bench.models import BenchResult


def make_result(provider: str = "openai", model: str = "gpt-4o-mini") -> BenchResult:
    return BenchResult(
        provider=provider,
        model=model,
        ttft_ms=312.0,
        total_ms=1840.0,
        tokens_per_sec=68.2,
        success_rate=1.0,
        p95_ms=2100.0,
        p50_ms=1800.0,
        errors=0,
        total_tokens=150,
    )


def test_providers_command_lists_builtin_targets():
    runner = CliRunner()
    result = runner.invoke(cli, ["providers"])

    assert result.exit_code == 0
    assert "openai" in result.output
    assert "custom" in result.output


def test_run_command_writes_report(monkeypatch, tmp_path):
    runner = CliRunner()
    output = tmp_path / "single.md"

    monkeypatch.setattr(
        "llm_gateway_bench.cli.run_benchmark",
        lambda **kwargs: make_result(provider=kwargs["provider"], model=kwargs["model"]),
    )

    result = runner.invoke(
        cli,
        [
            "run",
            "--provider",
            "openai",
            "--model",
            "gpt-4o-mini",
            "--output",
            str(output),
        ],
    )

    assert result.exit_code == 0
    assert output.exists()
    assert "gpt-4o-mini" in output.read_text(encoding="utf-8")


def test_compare_command_writes_report(monkeypatch, tmp_path):
    runner = CliRunner()
    config = tmp_path / "bench.yaml"
    output = tmp_path / "report.md"
    config.write_text(
        """
prompts:
  - "Say hello"
providers:
  - name: openai
    model: gpt-4o-mini
    api_key: ${OPENAI_API_KEY}
settings:
  requests: 2
  concurrency: 1
  timeout: 5
""".lstrip(),
        encoding="utf-8",
    )

    monkeypatch.setenv("OPENAI_API_KEY", "abc123")
    monkeypatch.setattr(
        "llm_gateway_bench.cli.compare_providers",
        lambda cfg: [make_result()],
    )

    result = runner.invoke(cli, ["compare", str(config), "--output", str(output)])

    assert result.exit_code == 0
    assert output.exists()
    assert "openai" in output.read_text(encoding="utf-8")
