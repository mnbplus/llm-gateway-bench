"""Custom exceptions for llm-gateway-bench."""


class LlmGatewayBenchError(Exception):
    """Base exception for all benchmark errors."""


class ConfigError(LlmGatewayBenchError):
    """Raised when configuration files are invalid or missing required values."""


class ProviderError(LlmGatewayBenchError):
    """Raised when provider configuration is invalid or unsupported."""


class ReportError(LlmGatewayBenchError):
    """Raised when report generation fails."""
