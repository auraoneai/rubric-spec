from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import json
from typing import Any

SUPPORTED_SCALES = {"binary", "ordinal", "likert", "continuous"}
TIE_BREAKS = {"prefer_lower_risk", "prefer_higher_score", "manual_review", "none"}

@dataclass(frozen=True)
class ValidationIssue:
    path: str
    message: str
    severity: str = "error"

@dataclass(frozen=True)
class ValidationResult:
    path: str
    errors: list[ValidationIssue] = field(default_factory=list)
    warnings: list[ValidationIssue] = field(default_factory=list)
    @property
    def ok(self) -> bool:
        return not self.errors
    def to_dict(self) -> dict[str, Any]:
        return {"path": self.path, "ok": self.ok, "errors": [e.__dict__ for e in self.errors], "warnings": [w.__dict__ for w in self.warnings]}

def load_rubric(path: str | Path) -> dict[str, Any]:
    text = Path(path).read_text(encoding="utf-8")
    stripped = text.strip()
    if stripped.startswith("{"):
        return json.loads(stripped)
    rows = [json.loads(line) for line in text.splitlines() if line.strip()]
    return {
        "version": "auraone-rubric-v1",
        "rubric_id": Path(path).stem,
        "label": Path(path).stem,
        "tie_break_rule": "none",
        "judge_prompt_contract": {"instruction": "Score each criterion from the anchors.", "output_format": "json", "required_fields": ["criterion_id", "score"]},
        "provenance": {"source": str(path), "created_by": "unknown", "created_at": "1970-01-01", "synthetic": True},
        "criteria": [from_evalkit_row(row) for row in rows],
    }

def from_evalkit_row(row: dict[str, Any]) -> dict[str, Any]:
    scoring = str(row.get("scoring_type", "binary"))
    scale = "binary" if scoring in {"binary", "pass_fail"} else "ordinal" if scoring.startswith("scale") else scoring
    max_score = int(row.get("max_score", 1 if scale == "binary" else 5))
    anchors = row.get("anchors") or row.get("score_levels") or [{"value": 0, "label": "low"}, {"value": max_score, "label": "high"}]
    if isinstance(anchors, dict):
        anchors = [{"value": k, "label": str(v)} for k, v in anchors.items()]
    return {"criterion_id": str(row.get("criterion_id", row.get("id", "criterion"))), "label": str(row.get("label", row.get("criterion", "Criterion"))), "description": str(row.get("criterion", row.get("description", ""))), "scale_type": scale if scale in SUPPORTED_SCALES else "ordinal", "weight": float(row.get("weight", 1.0)), "tie_break_rule": row.get("tie_break_rule", "none"), "anchors": anchors, "examples": row.get("examples", [])}

def validate_rubric(rubric: dict[str, Any], path: str = "<memory>") -> ValidationResult:
    errors: list[ValidationIssue] = []
    warnings: list[ValidationIssue] = []
    def err(p: str, msg: str): errors.append(ValidationIssue(p, msg))
    def warn(p: str, msg: str): warnings.append(ValidationIssue(p, msg, "warning"))
    if rubric.get("version") != "auraone-rubric-v1": err("/version", "version must be auraone-rubric-v1")
    if not rubric.get("rubric_id"): err("/rubric_id", "rubric_id is required")
    criteria = rubric.get("criteria")
    if not isinstance(criteria, list) or not criteria: err("/criteria", "criteria must be a non-empty array"); criteria = []
    seen: set[str] = set(); total = 0.0
    for i, c in enumerate(criteria):
        base = f"/criteria/{i}"
        cid = c.get("criterion_id")
        if not cid: err(base + "/criterion_id", "criterion_id is required")
        elif cid in seen: err(base + "/criterion_id", f"duplicate criterion_id {cid}")
        seen.add(str(cid))
        if not c.get("label"): err(base + "/label", "label is required")
        if c.get("scale_type") not in SUPPORTED_SCALES: err(base + "/scale_type", "scale_type must be binary, ordinal, likert, or continuous")
        weight = c.get("weight")
        if not isinstance(weight, (int, float)) or isinstance(weight, bool) or weight <= 0: err(base + "/weight", "weight must be a positive number")
        else: total += float(weight)
        if c.get("tie_break_rule", "none") not in TIE_BREAKS: err(base + "/tie_break_rule", "unsupported tie_break_rule")
        anchors = c.get("anchors")
        if not isinstance(anchors, list) or len(anchors) < 2: err(base + "/anchors", "at least two anchors are required")
    if criteria and abs(total - 1.0) > 0.001: warn("/criteria", f"weights sum to {total:.6g}, not 1.0")
    contract = rubric.get("judge_prompt_contract")
    if not isinstance(contract, dict) or not contract.get("instruction") or contract.get("output_format") not in {"json", "score", "label"}: err("/judge_prompt_contract", "judge_prompt_contract requires instruction and output_format")
    provenance = rubric.get("provenance")
    if not isinstance(provenance, dict) or "synthetic" not in provenance: err("/provenance", "provenance with synthetic disclosure is required")
    return ValidationResult(path=path, errors=errors, warnings=warnings)

def validate(rubric_path: str | Path) -> ValidationResult:
    try:
        return validate_rubric(load_rubric(rubric_path), str(rubric_path))
    except Exception as exc:
        return ValidationResult(path=str(rubric_path), errors=[ValidationIssue("/", str(exc))])
