"""Audit relative Markdown links and heading fragments in a project tree.

External URLs are intentionally not fetched. The audit checks local file
targets and GitHub-style heading fragments in Markdown files only.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote


LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(<?([^\s)>]+)>?(?:\s+[^)]*)?\)")
HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*#*\s*$", re.MULTILINE)
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "data:", "//")


def _heading_slugs(markdown: str) -> set[str]:
    """Return common GitHub-style heading slugs, including duplicate suffixes."""
    slugs: set[str] = set()
    counts: dict[str, int] = {}
    for heading in HEADING_RE.findall(markdown):
        slug = heading.lower().strip()
        slug = re.sub(r"[^\w\- ]", "", slug, flags=re.UNICODE)
        slug = re.sub(r" +", "-", slug)
        slug = re.sub(r"-+", "-", slug).strip("-")
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        slugs.add(slug if count == 0 else f"{slug}-{count}")
    return slugs


def audit(root: Path) -> list[dict[str, str]]:
    root = root.resolve()
    markdown_files = sorted(root.rglob("*.md")) + sorted(root.rglob("*.markdown"))
    issues: list[dict[str, str]] = []

    for source in markdown_files:
        try:
            text = source.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            issues.append({"source": str(source.relative_to(root)), "target": "", "issue": f"unreadable: {exc}"})
            continue

        for raw_target in LINK_RE.findall(text):
            target = unquote(raw_target.strip())
            if not target or target.startswith(EXTERNAL_PREFIXES) or target.startswith("#"):
                continue

            local_path, separator, fragment = target.partition("#")
            resolved = (source.parent / local_path).resolve() if local_path else source
            try:
                resolved.relative_to(root)
            except ValueError:
                issues.append({
                    "source": str(source.relative_to(root)),
                    "target": raw_target,
                    "issue": "target escapes project root",
                })
                continue

            if not resolved.exists():
                issues.append({
                    "source": str(source.relative_to(root)),
                    "target": raw_target,
                    "issue": "missing local file",
                })
                continue

            if separator and fragment and resolved.suffix.casefold() in {".md", ".markdown"}:
                try:
                    target_text = resolved.read_text(encoding="utf-8")
                except (OSError, UnicodeError) as exc:
                    issues.append({
                        "source": str(source.relative_to(root)),
                        "target": raw_target,
                        "issue": f"unreadable anchor target: {exc}",
                    })
                    continue
                if fragment.casefold() not in _heading_slugs(target_text):
                    issues.append({
                        "source": str(source.relative_to(root)),
                        "target": raw_target,
                        "issue": "missing Markdown heading fragment",
                    })

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="project root (default: current directory)")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args()

    root = args.root.resolve()
    if not root.is_dir():
        parser.error(f"project root is not a directory: {root}")
    issues = audit(root)
    if args.json:
        print(json.dumps({"root": str(root), "issue_count": len(issues), "issues": issues}, ensure_ascii=False, indent=2))
    else:
        print(f"Checked Markdown links under {root}; issues: {len(issues)}")
        for issue in issues:
            print(f"{issue['source']}: {issue['target']} ({issue['issue']})")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
