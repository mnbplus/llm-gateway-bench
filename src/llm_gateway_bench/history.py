"""History storage and comparison for llm-gateway-bench.

We store each run as a JSONL line in ``~/.lgb/history.jsonl``.
Each record is a lightweight dictionary including:
- run_id (auto)
- timestamp
- results[]
- meta (optional)

The CLI offers:
- `lgb history` to list runs
- `lgb history --compare RUN1 RUN2` to compare two stored runs
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Sequence, Tuple

from .models import BenchResult


def history_dir() -> Path:
    return Path(os.path.expanduser("~")) / ".lgb"


def history_path() -> Path:
    return history_dir() / "history.jsonl"


def ensure_history_parent() -> None:
    history_dir().mkdir(parents=True, exist_ok=True)


def _now_iso() -> str:
    # Keep it simple and stable without tz deps.
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())


def _default_run_id(ts: Optional[str] = None) -> str:
    # Lexicographically sortable
    return (ts or _now_iso()).replace(":", "").replace("-", "")


def serialize_results(results: Sequence[BenchResult]) -> List[Dict[str, Any]]:
    return [r.model_dump() for r in results]


def append_run(
    results: Sequence[BenchResult],
    *,
    run_id: Optional[str] = None,
    meta: Optional[Dict[str, Any]] = None,
) -> str:
    ensure_history_parent()
    ts = _now_iso()
    rid = run_id or _default_run_id(ts)

    record = {
        "run_id": rid,
        "ts": ts,
        "meta": meta or {},
        "results": serialize_results(results),
    }

    with history_path().open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return rid


@dataclass(frozen=True)
class HistoryRun:
    run_id: str
    ts: str
    meta: Dict[str, Any]
    results: List[BenchResult]


def iter_runs() -> Iterator[HistoryRun]:
    p = history_path()
    if not p.exists():
        return
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            results = [BenchResult.model_validate(r) for r in obj.get("results", [])]
            yield HistoryRun(
                run_id=obj.get("run_id", ""),
                ts=obj.get("ts", ""),
                meta=obj.get("meta", {}) or {},
                results=results,
            )


def list_runs(limit: int = 20) -> List[HistoryRun]:
    runs = list(iter_runs())
    runs.sort(key=lambda r: r.ts)
    if limit > 0:
        runs = runs[-limit:]
    return runs


def get_run(run_id: str) -> HistoryRun:
    for r in iter_runs():
        if r.run_id == run_id:
            return r
    raise KeyError(f"run not found: {run_id}")


def compare_runs(a_id: str, b_id: str) -> Tuple[HistoryRun, HistoryRun]:
    return get_run(a_id), get_run(b_id)
