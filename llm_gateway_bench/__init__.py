"""Development-time shim for the ``src`` layout.

This repository uses a ``src/`` layout for packaging. Some workflows (including
simple ``python -c ...`` invocations from the repository root) expect imports to
work without an editable install.

This module adds ``src`` to ``sys.path`` at runtime so that
``import llm_gateway_bench`` resolves to the real package.

It is **not** included in built distributions.
"""

from __future__ import annotations

import sys
from pathlib import Path
from pkgutil import extend_path

_src = Path(__file__).resolve().parent.parent / "src"
if _src.exists():
    sys.path.insert(0, str(_src))

__path__ = extend_path(__path__, __name__)
