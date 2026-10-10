"""Repository-intelligence helpers.

v0.1 keeps ranking deterministic and transparent.  The next phase can replace
or augment this with AST/import/call-graph analysis while preserving the same
output contract.
"""

from pathlib import PurePosixPath
from typing import Iterable, List, Sequence, Tuple


ENTRY_NAMES = {
    "__main__.py", "main.py", "app.py", "cli.py", "core.py",
    "index.js", "main.js", "app.js", "server.js",
    "index.ts", "main.ts", "app.ts",
    "main.go", "lib.rs", "main.rs", "mod.rs",
    "Main.java", "App.java",
}

DEPENDENCY_NAMES = {
    "requirements.txt", "pyproject.toml", "setup.py", "Pipfile",
    "package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock",
    "go.mod", "Cargo.toml", "pom.xml", "build.gradle", "Gemfile",
}

DOC_NAMES = {
    "readme.md", "readme.rst", "readme.txt", "contributing.md",
    "architecture.md", "docs.md", "changelog.md",
}

CORE_DIRS = {
    "src", "lib", "app", "core", "pkg", "internal", "cmd",
    "services", "service", "api", "server", "client", "agents", "agent",
}

EXCLUDED_DIRS = {
    "node_modules", "dist", "build", "vendor", ".venv", "venv",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".tox",
}


def score_path(path: str) -> int:
    p = PurePosixPath(path)
    name = p.name
    lower_name = name.lower()
    parts = {part.lower() for part in p.parts}

    # Generated/vendor trees are never repository-intelligence candidates.
    if parts & EXCLUDED_DIRS:
        return -1000

    score = 0

    if name in ENTRY_NAMES:
        score += 100
    if name in DEPENDENCY_NAMES:
        score += 80
    if lower_name in DOC_NAMES:
        score += 60
    if parts & CORE_DIRS:
        score += 35

    suffix = p.suffix.lower()
    if suffix in {".py", ".js", ".ts", ".tsx", ".go", ".rs", ".java", ".rb"}:
        score += 20

    depth = max(0, len(p.parts) - 1)
    score -= min(depth * 2, 20)

    if any(part.startswith(".") for part in p.parts):
        score -= 30

    return score


def rank_repository_paths(paths: Iterable[str], limit: int = 80) -> List[str]:
    ranked: List[Tuple[int, str]] = []
    for path in paths:
        score = score_path(path)
        if score > 0:
            ranked.append((score, path))

    ranked.sort(key=lambda item: (-item[0], item[1]))
    return [path for _, path in ranked[:limit]]


def classify_special_files(paths: Sequence[str]):
    entries = [p for p in paths if PurePosixPath(p).name in ENTRY_NAMES]
    dependencies = [p for p in paths if PurePosixPath(p).name in DEPENDENCY_NAMES]
    return entries, dependencies
