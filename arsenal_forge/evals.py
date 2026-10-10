"""Evaluation primitives for forged skills."""

from dataclasses import dataclass
import subprocess
import time
from typing import List, Optional, Sequence


@dataclass
class EvalResult:
    name: str
    passed: bool
    returncode: Optional[int]
    duration_s: float
    stdout: str = ""
    stderr: str = ""
    error: str = ""


def run_smoke_command(
    name: str,
    command: Sequence[str],
    cwd: Optional[str] = None,
    timeout: int = 30,
) -> EvalResult:
    """Run a smoke test without invoking a shell."""
    started = time.monotonic()
    try:
        proc = subprocess.run(
            list(command),
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False,
        )
        return EvalResult(
            name=name,
            passed=proc.returncode == 0,
            returncode=proc.returncode,
            duration_s=time.monotonic() - started,
            stdout=proc.stdout[-4000:],
            stderr=proc.stderr[-4000:],
        )
    except Exception as exc:
        return EvalResult(
            name=name,
            passed=False,
            returncode=None,
            duration_s=time.monotonic() - started,
            error=str(exc),
        )


def summarize(results: List[EvalResult]):
    total = len(results)
    passed = sum(1 for result in results if result.passed)
    return {
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate": (passed / total) if total else 0.0,
    }
