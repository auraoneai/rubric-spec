from __future__ import annotations

import importlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .validate import load_rubric, validate_rubric

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

    return ConformanceReport(suite="rubric-spec-v1", cases=cases)
