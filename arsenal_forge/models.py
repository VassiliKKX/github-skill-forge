from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class RiskLevel(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Finding:
    rule_id: str
    level: RiskLevel
    message: str
    path: str = ""
    line: Optional[int] = None
    evidence: str = ""


@dataclass
class GateDecision:
    passed: bool
    score: int
    findings: List[Finding] = field(default_factory=list)
    reasons: List[str] = field(default_factory=list)


@dataclass
class RepoProfile:
    owner: str
    name: str
    url: str
    description: str = ""
    language: str = "Unknown"
    default_branch: str = "main"
    stars: int = 0
    license_id: str = "UNKNOWN"
    entry_points: List[str] = field(default_factory=list)
    dependency_files: List[str] = field(default_factory=list)
    ranked_paths: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)
