"""Pydantic models used across llm-gateway-bench."""

from __future__ import annotations

from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DictLikeModel(BaseModel):
    """Pydantic model with light dict-style access for backward compatibility."""

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)


class ProviderConfig(DictLikeModel):
    """Configuration for a single provider."""

    name: str = Field(..., min_length=1)
    model: str = Field(..., min_length=1)
    base_url: Optional[str] = None
    api_key: Optional[str] = None

    model_config = ConfigDict(extra="allow")

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("base_url", "api_key")
    @classmethod
    def normalize_optional(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        value = value.strip()
        return value or None


class SettingsConfig(DictLikeModel):
    """Global benchmark settings."""

    requests: int = Field(20, gt=0)
    concurrency: int = Field(3, gt=0)
    timeout: int = Field(30, gt=0)

    model_config = ConfigDict(extra="forbid")


class BenchConfig(DictLikeModel):
    """Top-level benchmark configuration."""

    prompts: List[str] = Field(default_factory=lambda: ["Say hello."])
    providers: List[ProviderConfig] = Field(default_factory=list)
    settings: SettingsConfig = Field(
        default_factory=lambda: SettingsConfig(
            requests=20,
            concurrency=3,
            timeout=30,
        )
    )

    model_config = ConfigDict(extra="forbid")

    def first_prompt(self) -> str:
        """Return the first prompt or a safe default."""
        return self.prompts[0] if self.prompts else "Say hello."


class BenchResult(DictLikeModel):
    """Summary statistics for a benchmark run."""

    provider: str
    model: str
    ttft_ms: float = 0.0
    total_ms: float = 0.0
    tokens_per_sec: float = 0.0
    success_rate: float = Field(0.0, ge=0.0, le=1.0)
    p95_ms: float = 0.0
    p50_ms: float = 0.0
    errors: int = 0
    total_tokens: int = 0
    raw_latencies: List[float] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")
