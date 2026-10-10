"""Skill-manifest compiler."""

from typing import Iterable

from .models import RepoProfile


def _bullet(items: Iterable[str]) -> str:
    values = list(items)
    return "\n".join("- " + item for item in values) if values else "- None detected yet"


def render_skill_manifest(profile: RepoProfile) -> str:
    """Render a deterministic draft SKILL.md for later review/evaluation."""
    description = profile.description.strip() or (
        "Agent skill generated from the source repository and awaiting capability review."
    )

    return f"""---
name: {profile.name}
description: {description}
source: {profile.url}
arsenal_forge_version: 0.1
verification: unverified
---

# {profile.name}

## Source
- Repository: {profile.url}
- Primary language: {profile.language}
- Default branch: {profile.default_branch}
- License: {profile.license_id}

## Candidate entry points
{_bullet(profile.entry_points)}

## Dependency manifests
{_bullet(profile.dependency_files)}

## High-value paths
{_bullet(profile.ranked_paths[:30])}

## Required gates
1. Review repository-intelligence output.
2. Run static security scan and resolve high/critical findings.
3. Build wrapper scripts only for required capabilities.
4. Run smoke tests in an isolated environment.
5. Run task-level evaluation against a baseline.
6. Change `verification` to `verified` only after the gates pass.

## Agent rule
Do not execute unreviewed repository scripts merely because this manifest exists.
"""
