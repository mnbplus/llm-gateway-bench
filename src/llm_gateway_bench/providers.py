"""Provider defaults used by llm-gateway-bench.

Kept in a standalone module to avoid circular imports between validation and bench logic.
"""

from __future__ import annotations

from typing import Dict

PROVIDER_DEFAULTS: Dict[str, Dict[str, str]] = {
    # ── Frontier providers ───────────────────────────────────────────────────
    "openai": {"base_url": "https://api.openai.com/v1", "env_key": "OPENAI_API_KEY"},
    "anthropic": {"base_url": "https://api.anthropic.com/v1", "env_key": "ANTHROPIC_API_KEY"},
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "env_key": "GEMINI_API_KEY",
    },
    # ── Chinese providers ────────────────────────────────────────────────────
    "deepseek": {"base_url": "https://api.deepseek.com/v1", "env_key": "DEEPSEEK_API_KEY"},
    "dashscope": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "env_key": "DASHSCOPE_API_KEY",
    },
    "siliconflow": {"base_url": "https://api.siliconflow.cn/v1", "env_key": "SILICONFLOW_API_KEY"},
    "zhipu": {"base_url": "https://open.bigmodel.cn/api/paas/v4", "env_key": "ZHIPU_API_KEY"},
    "moonshot": {"base_url": "https://api.moonshot.cn/v1", "env_key": "MOONSHOT_API_KEY"},
    "baidu": {"base_url": "https://qianfan.baidubce.com/v2", "env_key": "BAIDU_API_KEY"},
    "01ai": {"base_url": "https://api.lingyiwanwu.com/v1", "env_key": "YI_API_KEY"},
    "minimax": {"base_url": "https://api.minimax.chat/v1", "env_key": "MINIMAX_API_KEY"},
    # ── Fast inference / aggregators ─────────────────────────────────────────
    "groq": {"base_url": "https://api.groq.com/openai/v1", "env_key": "GROQ_API_KEY"},
    "together": {"base_url": "https://api.together.xyz/v1", "env_key": "TOGETHER_API_KEY"},
    "fireworks": {"base_url": "https://api.fireworks.ai/inference/v1", "env_key": "FIREWORKS_API_KEY"},
    "openrouter": {"base_url": "https://openrouter.ai/api/v1", "env_key": "OPENROUTER_API_KEY"},
    "mistral": {"base_url": "https://api.mistral.ai/v1", "env_key": "MISTRAL_API_KEY"},
    "cohere": {"base_url": "https://api.cohere.com/compatibility/v1", "env_key": "COHERE_API_KEY"},
    "perplexity": {"base_url": "https://api.perplexity.ai", "env_key": "PERPLEXITY_API_KEY"},
    # ── Self-hosted / local ──────────────────────────────────────────────────
    "ollama": {"base_url": "http://localhost:11434/v1", "env_key": ""},
    "vllm": {"base_url": "http://localhost:8000/v1", "env_key": ""},
    "lmstudio": {"base_url": "http://localhost:1234/v1", "env_key": ""},
}
