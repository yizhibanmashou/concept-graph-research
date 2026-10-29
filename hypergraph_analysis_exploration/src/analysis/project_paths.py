"""Resolve project-level data paths from the versioned configuration file."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROJECT_CONFIG = PROJECT_ROOT / "config" / "project_config.json"


def configured_bundle_root(project_root: Path = PROJECT_ROOT) -> Path:
    """Return the configured frozen-bundle root, resolving relative paths at project root."""
    config_path = project_root / "config" / "project_config.json"
    try:
        config: Any = json.loads(config_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Project configuration is missing: {config_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Project configuration is invalid JSON: {config_path}") from exc
    if not isinstance(config, dict):
        raise ValueError("Project configuration must be a JSON object")
    data_source = config.get("data_source")
    if not isinstance(data_source, dict):
        raise ValueError("Project configuration must define an object at data_source")
    raw_root = data_source.get("root")
    if not isinstance(raw_root, str) or not raw_root.strip():
        raise ValueError("Project configuration data_source.root must be a non-empty path")
    path = Path(raw_root)
    if not path.is_absolute():
        path = project_root / path
    return path.resolve()
