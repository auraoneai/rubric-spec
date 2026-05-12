from __future__ import annotations

import importlib
import json
from dataclasses import dataclass
from copy import deepcopy
from pathlib import Path
from typing import Any

from .validate import load_rubric, validate_rubric
from .lint import lint_rubric

ADAPTERS = ("inspect_ai", "promptfoo", "deepeval", "langsmith", "evalkit")


@dataclass(frozen=True)
class ConformanceCase:
    name: str
    adapter: str
    ok: bool
    message: str = ""


@dataclass(frozen=True)
class ConformanceReport:
    suite: str
    cases: list[ConformanceCase]

    @property
    def ok(self) -> bool:
        return all(case.ok for case in self.cases)

    def to_dict(self) -> dict[str, Any]:
        return {
            "suite": self.suite,
            "ok": self.ok,
            "case_count": len(self.cases),
            "passed": sum(case.ok for case in self.cases),
            "failed": sum(not case.ok for case in self.cases),
            "cases": [case.__dict__ for case in self.cases],
        }


def run_conformance(rubric_path: str | Path, adapters: tuple[str, ...] = ADAPTERS) -> ConformanceReport:
    rubric = load_rubric(rubric_path)
    cases: list[ConformanceCase] = []

    validation = validate_rubric(rubric, str(rubric_path))
    cases.append(
        ConformanceCase(
            name="canonical rubric validates",
            adapter="rubric_spec",
            ok=validation.ok,
            message="" if validation.ok else "; ".join(error.message for error in validation.errors),
        )
    )

    for adapter_name in adapters:
        adapter = importlib.import_module(f"rubric_spec.adapters.{adapter_name}")
        native = adapter.from_spec(rubric)
        round_trip = adapter.to_spec(native)
        cases.append(
            ConformanceCase(
                name="to_spec(from_spec(rubric)) preserves canonical rubric",
                adapter=adapter_name,
                ok=round_trip == rubric,
                message="" if round_trip == rubric else "round-trip changed canonical rubric fields",
            )
        )
        converted_validation = validate_rubric(round_trip, f"{adapter_name}:round_trip")
        cases.append(
            ConformanceCase(
                name="adapter output validates",
                adapter=adapter_name,
                ok=converted_validation.ok,
                message="" if converted_validation.ok else "; ".join(error.message for error in converted_validation.errors),
            )
        )

    cases.extend(_schema_conformance_cases(rubric))
    return ConformanceReport(suite="rubric-spec-v1", cases=cases)


def _schema_conformance_cases(rubric: dict[str, Any]) -> list[ConformanceCase]:
    cases: list[ConformanceCase] = []

    missing_version = deepcopy(rubric)
    missing_version.pop("version", None)
    result = validate_rubric(missing_version, "missing_version")
    cases.append(
        ConformanceCase(
            name="rejects missing version with path-aware error",
            adapter="rubric_spec",
            ok=not result.ok and any(error.path == "/version" for error in result.errors),
            message=json.dumps(result.to_dict(), sort_keys=True),
        )
    )

    unsupported_scale = deepcopy(rubric)
    unsupported_scale["criteria"][0]["scale_type"] = "stars"
    result = validate_rubric(unsupported_scale, "unsupported_scale")
    cases.append(
        ConformanceCase(
            name="rejects unsupported scale_type",
            adapter="rubric_spec",
            ok=not result.ok and any(error.path.endswith("/scale_type") for error in result.errors),
            message=json.dumps(result.to_dict(), sort_keys=True),
        )
    )

    duplicate_ids = deepcopy(rubric)
    duplicate_ids["criteria"] = [deepcopy(rubric["criteria"][0]), deepcopy(rubric["criteria"][0])]
    result = validate_rubric(duplicate_ids, "duplicate_ids")
    cases.append(
        ConformanceCase(
            name="rejects duplicate criterion_id values",
            adapter="rubric_spec",
            ok=not result.ok and any("duplicate" in error.message for error in result.errors),
            message=json.dumps(result.to_dict(), sort_keys=True),
        )
    )

    weight_warning = deepcopy(rubric)
    weight_warning["criteria"][0]["weight"] = 0.75
    result = validate_rubric(weight_warning, "weight_warning")
    cases.append(
        ConformanceCase(
            name="warns when weights do not sum to one",
            adapter="rubric_spec",
            ok=result.ok and any(warning.path == "/criteria" for warning in result.warnings),
            message=json.dumps(result.to_dict(), sort_keys=True),
        )
    )

    lint_target = deepcopy(rubric)
    lint_target["criteria"][0]["description"] = "Good and useful answer."
    lint_target["criteria"][0]["examples"] = []
    rules = {finding.rule for finding in lint_rubric(lint_target)}
    cases.append(
        ConformanceCase(
            name="emits lint findings for vague compound missing-example criteria",
            adapter="rubric_spec",
            ok={"R_VAGUE", "R_COMPOUND", "R_EXAMPLES"}.issubset(rules),
            message=json.dumps(sorted(rules)),
        )
    )

    first = json.dumps(rubric, sort_keys=True, separators=(",", ":"))
    second = json.dumps(json.loads(first), sort_keys=True, separators=(",", ":"))
    cases.append(
        ConformanceCase(
            name="deterministic JSON serialization",
            adapter="rubric_spec",
            ok=first == second,
            message=first[:200],
        )
    )

    cases.append(
        ConformanceCase(
            name="preserves synthetic data disclosure",
            adapter="rubric_spec",
            ok=rubric.get("provenance", {}).get("synthetic") is True,
            message=json.dumps(rubric.get("provenance", {}), sort_keys=True),
        )
    )

    return cases
