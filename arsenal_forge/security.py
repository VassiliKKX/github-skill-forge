"""Static security gate for forged skills.

The scanner is deliberately conservative: it flags behavior for review and
does not claim that a repository is safe merely because no rule matched.
"""

import re
from typing import Dict, List, Tuple

from .models import Finding, GateDecision, RiskLevel


Rule = Tuple[str, RiskLevel, re.Pattern, str]


RULES: List[Rule] = [
    (
        "AF001",
        RiskLevel.CRITICAL,
        re.compile(r"\bcurl\b[^\n|]{0,200}\|\s*(?:ba)?sh\b", re.I),
        "Remote content is piped directly into a shell.",
    ),
    (
        "AF002",
        RiskLevel.HIGH,
        re.compile(r"\b(?:os\.system|subprocess\.[A-Za-z_]+)\s*\([^\n]{0,300}shell\s*=\s*True", re.I),
        "Shell execution with shell=True requires manual review.",
    ),
    (
        "AF003",
        RiskLevel.HIGH,
        re.compile(r"\b(?:eval|exec)\s*\(", re.I),
        "Dynamic code execution detected.",
    ),
    (
        "AF004",
        RiskLevel.HIGH,
        re.compile(r"(?:\.ssh|id_rsa|credentials|aws_access_key|github_token|api[_-]?key)", re.I),  # nosec AF004
        "Potential credential or secret access detected.",
    ),
    (
        "AF005",
        RiskLevel.MEDIUM,
        re.compile(r"\b(?:requests\.(?:get|post|put|delete)|urllib\.request|fetch\s*\()", re.I),
        "Outbound network access detected.",
    ),
    (
        "AF006",
        RiskLevel.MEDIUM,
        re.compile(r"\b(?:rm\s+-rf|shutil\.rmtree|os\.remove|os\.unlink)\b", re.I),
        "Destructive filesystem operation detected.",
    ),
]


def _line_for_offset(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _line_text(text: str, line_number: int) -> str:
    lines = text.splitlines()
    if 1 <= line_number <= len(lines):
        return lines[line_number - 1]
    return ""


def _is_suppressed(line_text: str, rule_id: str) -> bool:
    """Allow explicit, rule-scoped suppression such as '# nosec AF003'."""
    match = re.search(r"(?:#|//)\s*nosec\s+([A-Z0-9_, -]+)", line_text, re.I)
    if not match:
        return False

    ids = {
        item.strip().upper()
        for item in re.split(r"[,\s]+", match.group(1))
        if item.strip()
    }
    return rule_id.upper() in ids


class SecurityScanner:
    def scan_text(self, path: str, text: str) -> List[Finding]:
        findings: List[Finding] = []
        for rule_id, level, pattern, message in RULES:
            for match in pattern.finditer(text):
                line_number = _line_for_offset(text, match.start())
                if _is_suppressed(_line_text(text, line_number), rule_id):
                    continue

                evidence = match.group(0).replace("\n", " ")[:180]
                findings.append(
                    Finding(
                        rule_id=rule_id,
                        level=level,
                        message=message,
                        path=path,
                        line=line_number,
                        evidence=evidence,
                    )
                )
        return findings

    def scan_files(self, files: Dict[str, str]) -> List[Finding]:
        findings: List[Finding] = []
        for path, text in files.items():
            findings.extend(self.scan_text(path, text))
        return findings

    def gate(self, files: Dict[str, str]) -> GateDecision:
        findings = self.scan_files(files)
        penalty = {
            RiskLevel.INFO: 0,
            RiskLevel.LOW: 2,
            RiskLevel.MEDIUM: 8,
            RiskLevel.HIGH: 20,
            RiskLevel.CRITICAL: 45,
        }
        score = max(0, 100 - sum(penalty[f.level] for f in findings))
        blocker = any(f.level in {RiskLevel.HIGH, RiskLevel.CRITICAL} for f in findings)

        reasons = []
        if blocker:
            reasons.append("High or critical findings require manual review.")
        if not findings:
            reasons.append("No static rule matched; this is not a safety guarantee.")

        return GateDecision(
            passed=not blocker,
            score=score,
            findings=findings,
            reasons=reasons,
        )
