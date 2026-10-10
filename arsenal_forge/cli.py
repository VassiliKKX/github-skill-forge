import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Dict, Iterable, List

from .compiler import render_skill_manifest
from .models import RepoProfile
from .scanner import classify_special_files, rank_repository_paths
from .security import SecurityScanner


SKIP_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "dist", "build", "vendor",
    ".venv", "venv", "__pycache__", ".pytest_cache", ".mypy_cache",
}

TEXT_SUFFIXES = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java", ".rb",
    ".php", ".sh", ".bash", ".zsh", ".ps1", ".yml", ".yaml", ".json",
    ".toml", ".ini", ".cfg", ".md", ".rst", ".txt",
}


def iter_paths(root: Path, max_files: int = 5000) -> List[str]:
    result: List[str] = []
    for path in root.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if not path.is_file():
            continue
        result.append(path.relative_to(root).as_posix())
        if len(result) >= max_files:
            break
    return result


def read_candidate_files(
    root: Path,
    paths: Iterable[str],
    max_bytes_per_file: int = 250_000,
) -> Dict[str, str]:
    files: Dict[str, str] = {}
    for relative in paths:
        path = root / relative
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {
            "Dockerfile", "Makefile", "Procfile"
        }:
            continue
        try:
            if path.stat().st_size > max_bytes_per_file:
                continue
            files[relative] = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
    return files


def inspect_local(
    root: Path,
    source_url: str,
    name: str,
    output_dir: Path,
    language: str = "Unknown",
):
    paths = iter_paths(root)
    ranked = rank_repository_paths(paths, limit=120)
    entries, dependency_files = classify_special_files(paths)

    scan_targets = list(dict.fromkeys(ranked + dependency_files + entries))
    file_contents = read_candidate_files(root, scan_targets)
    gate = SecurityScanner().gate(file_contents)

    profile = RepoProfile(
        owner="local",
        name=name,
        url=source_url,
        language=language,
        entry_points=entries[:20],
        dependency_files=dependency_files[:20],
        ranked_paths=ranked,
        metadata={"local_root": str(root.resolve())},
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "SKILL.md").write_text(
        render_skill_manifest(profile),
        encoding="utf-8",
    )
    (output_dir / "repo_profile.json").write_text(
        json.dumps(asdict(profile), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    security_payload = {
        "passed": gate.passed,
        "score": gate.score,
        "reasons": gate.reasons,
        "findings": [
            {
                **asdict(item),
                "level": item.level.value,
            }
            for item in gate.findings
        ],
    }
    (output_dir / "security_report.json").write_text(
        json.dumps(security_payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return profile, gate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="arsenal-forge",
        description="Forge a reviewable Agent skill from repository evidence.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    local = sub.add_parser(
        "inspect-local",
        help="Inspect a local repository and generate an unverified skill draft.",
    )
    local.add_argument("path")
    local.add_argument("--source-url", default="local://repository")
    local.add_argument("--name")
    local.add_argument("--language", default="Unknown")
    local.add_argument("--output-dir", default=".arsenal-forge/out")

    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "inspect-local":
        root = Path(args.path).resolve()
        if not root.is_dir():
            raise SystemExit(f"Repository path does not exist: {root}")

        name = args.name or root.name
        profile, gate = inspect_local(
            root=root,
            source_url=args.source_url,
            name=name,
            output_dir=Path(args.output_dir),
            language=args.language,
        )

        print(f"Repository: {profile.name}")
        print(f"Security score: {gate.score}/100")
        print(f"Security gate: {'PASS' if gate.passed else 'REVIEW REQUIRED'}")
        print(f"Output: {Path(args.output_dir).resolve()}")
        return 0 if gate.passed else 2

    return 1
