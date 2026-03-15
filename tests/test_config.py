"""Tests for configuration loading."""

from llm_gateway_bench.config import load_config


def test_load_config_expands_env(sample_config_dict):
    cfg = load_config(sample_config_dict["path"])
    assert cfg["providers"][0]["api_key"] == "abc123"
    assert cfg["settings"]["requests"] == 2
