# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-03-15

### Added

- `lgb version` command: shows version, Python version, and platform info.
- `lgb history` command: lists saved benchmark runs in a formatted table.
- `lgb history --compare <id1> <id2>`: side-by-side comparison of two runs.
- `lgb warmup` command: sends one request per provider to verify reachability before benchmarking.
- `lgb run --warmup` flag: integrates warmup check into the run workflow.
- `formatters.py`: ASCII horizontal latency distribution histogram per provider.
- `formatters.py`: best value highlighted green, worst value highlighted red in result tables.
- `formatters.py`: improved progress bar using `MofNCompleteColumn` and `TimeRemainingColumn`.
- `warmup.py`: new module with `WarmupChecker` class for async concurrent provider health checks.

### Changed

- `lgb providers`: upgraded to a rich rounded table with index column and provider count footer.
- `lgb run`: now prints latency histogram after the results table in table output mode.
- All CLI commands now include complete `--help` descriptions with usage examples.
- Project version bumped to `0.2.0`.

### Fixed

- Lint issues fixed via `ruff check . --fix`.

## [0.1.0] - 2026-03-15

### Added

- Initial release.
- CLI commands: `run`, `compare`, `providers`.
- YAML configuration loader with environment variable expansion.
- Report generator (Markdown/JSON/CSV).
- CI workflow with `ruff` linting and `pytest`.

### Changed

- Internal models migrated to Pydantic for validation and typing.

[0.2.0]: https://github.com/mnbplus/llm-gateway-bench/releases/tag/v0.2.0
[0.1.0]: https://github.com/mnbplus/llm-gateway-bench/releases/tag/v0.1.0
