from __future__ import annotations
from dataclasses import dataclass
import re
from typing import Any
from .validate import load_rubric

VAGUE = re.compile(r"\b(good|bad|clear|appropriate|reasonable|useful|nice)\b", re.I)
COMPOUND = re.compile(r"\b(and|also|as well as|both)\b", re.I)

@dataclass(frozen=True)
class LintFinding:
    path: str
    severity: str
    rule: str
    message: str
    suggested_fix: str

def lint(rubric_path: str) -> list[LintFinding]:
    return lint_rubric(load_rubric(rubric_path))

def lint_rubric(rubric: dict[str, Any]) -> list[LintFinding]:
    findings: list[LintFinding] = []
    criteria = rubric.get("criteria", [])
    total = sum(float(c.get("weight", 0)) for c in criteria if isinstance(c.get("weight"), (int, float)))
    if criteria and abs(total - 1.0) > 0.001:
        findings.append(LintFinding("/criteria", "warning", "R_WEIGHT_TOTAL", f"weights sum to {total:.3f}", "Normalize weights to 1.0."))
    for i, c in enumerate(criteria):
        text = " ".join(str(c.get(k, "")) for k in ("label", "description"))
        path = f"/criteria/{i}"
        if VAGUE.search(text): findings.append(LintFinding(path, "warning", "R_VAGUE", "criterion uses vague wording", "Use observable scoring boundaries."))
        if COMPOUND.search(text): findings.append(LintFinding(path, "warning", "R_COMPOUND", "criterion may combine multiple judgments", "Split independent judgments."))
        if not c.get("examples"): findings.append(LintFinding(path, "warning", "R_EXAMPLES", "criterion has no examples", "Add synthetic positive and negative examples."))
    return findings
