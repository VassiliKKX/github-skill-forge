"""Arsenal Forge core package.

This package is intentionally dependency-light.  v0.1 focuses on repository
intelligence, security gating, evaluation primitives, and skill compilation.
"""

from .models import Finding, GateDecision, RepoProfile, RiskLevel
from .security import SecurityScanner
from .scanner import rank_repository_paths
from .compiler import render_skill_manifest

__all__ = [
    "Finding",
    "GateDecision",
    "RepoProfile",
    "RiskLevel",
    "SecurityScanner",
    "rank_repository_paths",
    "render_skill_manifest",
]

__version__ = "0.1.0"
