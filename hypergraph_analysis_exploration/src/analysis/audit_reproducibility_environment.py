"""Write a repeatable, read-only snapshot of the maintained Python environment."""
from __future__ import annotations

import argparse
import ast
from datetime import date
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any

from src.analysis.project_paths import PROJECT_ROOT, configured_bundle_root


DEFAULT_OUTPUT = PROJECT_ROOT / "sources" / "reproducibility_environment_audit_current.json"
DEPENDENCY_MANIFEST_NAMES = (
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "requirements.txt",
    "Pipfile",
    "Pipfile.lock",
    "poetry.lock",
    "uv.lock",
    "environment.yml",
    "environment.yaml",
)
PYTHON_VERSION_RE = re.compile(r"^\s*python-version:\s*[\"']?(\d+\.\d+(?:\.\d+)?)[\"']?\s*$")
OS_RE = re.compile(r"^\s*-\s*os:\s*([^\s#]+)")


def sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_local_import(name: str, project_root: Path, local_modules: set[str]) -> bool:
    top_level = name.split(".", 1)[0]
    return top_level in local_modules or (project_root / top_level).exists()


def scan_python_sources(project_root: Path) -> dict[str, Any]:
    python_files = sorted(
        path
        for source_root in (project_root / "src", project_root / "tests")
        if source_root.is_dir()
        for path in source_root.rglob("*.py")
        if "__pycache__" not in path.parts
    )
    parse_errors: list[dict[str, str]] = []
    imports: set[str] = set()
    source_tree_digest = hashlib.sha256()
    local_modules = {"src", "tests"}
    local_modules.update(path.stem for path in python_files)
    local_modules.update(
        path.name
        for name in ("src", "tests")
        if (project_root / name).is_dir()
        for path in (project_root / name).iterdir()
        if path.is_dir() and (path / "__init__.py").is_file()
    )
    for path in python_files:
        try:
            source_bytes = path.read_bytes()
            relative_path = path.relative_to(project_root).as_posix()
            source_tree_digest.update(relative_path.encode("utf-8"))
            source_tree_digest.update(b"\0")
            source_tree_digest.update(source_bytes)
            tree = ast.parse(source_bytes.decode("utf-8"), filename=relative_path)
        except (OSError, SyntaxError, UnicodeError) as exc:
            parse_errors.append({"path": path.relative_to(project_root).as_posix(), "error": str(exc)})
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
                imports.add(node.module.split(".", 1)[0])

    stdlib = getattr(sys, "stdlib_module_names", frozenset())
    external_top_level_imports = sorted(
        name for name in imports if name not in stdlib and not _is_local_import(name, project_root, local_modules)
    )
    return {
        "directories_scanned": [
            name for name in ("src", "tests") if (project_root / name).is_dir()
        ],
        "python_file_count": len(python_files),
        "maintained_source_tree_sha256": source_tree_digest.hexdigest(),
        "ast_parse_error_count": len(parse_errors),
        "ast_parse_errors": parse_errors,
        "non_stdlib_non_local_top_level_imports": external_top_level_imports,
        "limitations": [
            "AST scanning does not detect dynamic imports, subprocess-only dependencies, or runtime-only optional modules.",
            "Historical archive directories are outside the maintained-code scan.",
        ],
    }


def parse_ci_matrix(workflow_path: Path) -> list[dict[str, str]]:
    if not workflow_path.is_file():
        return []
    matrix: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for line in workflow_path.read_text(encoding="utf-8").splitlines():
        os_match = OS_RE.match(line)
        if os_match:
            if current:
                matrix.append(current)
            current = {"os": os_match.group(1)}
            continue
        version_match = PYTHON_VERSION_RE.match(line)
        if version_match and current is not None:
            current["python_version"] = version_match.group(1)
    if current:
        matrix.append(current)
    return matrix


def audit_environment(project_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    root = project_root.resolve()
    config_path = root / "config" / "project_config.json"
    lock_path = root / "config" / "frozen_bundle_integrity_lock.json"
    workflow_path = root / ".github" / "workflows" / "tests.yml"
    config: dict[str, Any] = {}
    config_error = None
    try:
        loaded = json.loads(config_path.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            config = loaded
        else:
            config_error = "project_config.json must contain a JSON object"
    except (OSError, json.JSONDecodeError) as exc:
        config_error = str(exc)

    bundle_config = config.get("data_source", {})
    configured_relative_root = bundle_config.get("root") if isinstance(bundle_config, dict) else None
    bundle_root = None
    bundle_error = config_error
    if config and config_error is None:
        try:
            bundle_root = configured_bundle_root(root)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            bundle_error = str(exc)

    dependency_manifests = [
        name for name in DEPENDENCY_MANIFEST_NAMES if (root / name).is_file()
    ]
    source_scan = scan_python_sources(root)
    license_files = [
        name for name in ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING", "COPYING.md", "COPYING.txt")
        if (root / name).is_file()
    ]
    bundle_manifest = bundle_root / "manifest.json" if bundle_root else None

    return {
        "audit_id": "reproducibility-environment-audit/2",
        "date": date.today().isoformat(),
        "scope": "Read-only snapshot of maintained Python imports, declared dependency manifests, CI matrix, repository license markers, and configured external bundle path; not CI, a test run, or a full data integrity replay.",
        "audit_script_sha256": sha256_file(Path(__file__)),
        "runtime_observed": {
            "python_version": sys.version.split()[0],
            "python_major_minor": f"{sys.version_info.major}.{sys.version_info.minor}",
            "runtime_patch_is_pinned": False,
        },
        "maintained_python_import_scan": source_scan,
        "dependency_configuration": {
            "dependency_manifest_files_found": dependency_manifests,
            "ci_matrix": parse_ci_matrix(workflow_path),
            "ci_workflow_sha256": sha256_file(workflow_path),
            "third_party_imports_detected": source_scan["non_stdlib_non_local_top_level_imports"],
        },
        "repository_release_markers": {
            "license_files_found": license_files,
            "release_status_declared_in_inventory": _declared_release_status(root),
        },
        "frozen_bundle_configuration": {
            "configured_relative_root": configured_relative_root,
            "path_resolution_error": bundle_error,
            "bundle_root_exists": bool(bundle_root and bundle_root.is_dir()),
            "manifest_exists": bool(bundle_manifest and bundle_manifest.is_file()),
            "bundle_integrity_replayed": False,
            "bundle_integrity_lock_sha256": sha256_file(lock_path),
            "project_config_sha256": sha256_file(config_path),
            "limitation": "A sibling bundle is not included by cloning this project alone; path/manifest existence does not establish byte-level integrity or public-release rights.",
        },
    }


def _declared_release_status(project_root: Path) -> str | None:
    inventory = project_root / "sources" / "data_release_inventory.json"
    try:
        data = json.loads(inventory.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    status = data.get("project_release_status") if isinstance(data, dict) else None
    return status if isinstance(status, str) else None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)

    root = args.project_root.resolve()
    output = args.output.resolve()
    if not output.is_relative_to(root):
        parser.error("output must remain inside the project directory")
    if output.exists() and not args.force:
        parser.error(f"output exists; pass --force to replace: {output}")

    result = audit_environment(root)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = {
        "output": output.relative_to(root).as_posix(),
        "python_version": result["runtime_observed"]["python_version"],
        "maintained_python_file_count": result["maintained_python_import_scan"]["python_file_count"],
        "ast_parse_error_count": result["maintained_python_import_scan"]["ast_parse_error_count"],
        "third_party_imports_detected": result["dependency_configuration"]["third_party_imports_detected"],
        "bundle_manifest_exists": result["frozen_bundle_configuration"]["manifest_exists"],
        "release_status_declared": result["repository_release_markers"]["release_status_declared_in_inventory"],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 1 if result["maintained_python_import_scan"]["ast_parse_error_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
