"""Project evaluation checks for docstrings and TODO markers."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[1] / "app" / "src"
FORBIDDEN_MARKERS = ("TODO", "FIXME")


def _is_public(name: str) -> bool:
    return not name.startswith("_")


def _marker_violations(file_path: Path) -> list[str]:
    text = file_path.read_text(encoding="utf-8")
    violations: list[str] = []
    for marker in FORBIDDEN_MARKERS:
        if marker in text:
            violations.append(f"{file_path}: contains {marker}")
    return violations


def _docstring_violations(file_path: Path) -> list[str]:
    tree = ast.parse(file_path.read_text(encoding="utf-8"), filename=str(file_path))
    violations: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if not _is_public(node.name):
                continue
            if ast.get_docstring(node) is None:
                violations.append(
                    f"{file_path}:{node.lineno} missing docstring for {node.name}"
                )

    return violations


def run_checks() -> list[str]:
    """Run all configured static quality checks and return violations."""
    violations: list[str] = []
    for file_path in sorted(SOURCE_ROOT.rglob("*.py")):
        violations.extend(_marker_violations(file_path))
        violations.extend(_docstring_violations(file_path))
    return violations


def main() -> int:
    """Execute eval checks and return process exit code semantics."""
    violations = run_checks()
    if violations:
        print("Evaluation failed:")
        for violation in violations:
            print(f"- {violation}")
        return 1

    print("Evaluation passed: no TODO/FIXME markers and docstrings are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
