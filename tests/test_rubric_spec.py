import json, subprocess, sys
from pathlib import Path
from rubric_spec import validate, diff_rubrics, lint_rubric
from rubric_spec.adapters import inspect_ai, promptfoo, deepeval, langsmith, evalkit

ROOT = Path(__file__).resolve().parents[1]

def test_validate_minimal():
    result = validate(ROOT / "examples/minimal_rubric.json")
    assert result.ok, result.to_dict()

def test_diff_reports_weight_delta():
    rubric = json.loads((ROOT / "examples/minimal_rubric.json").read_text())
    changed = json.loads(json.dumps(rubric)); changed["criteria"][0]["weight"] = 0.4; changed["criteria"][1]["weight"] = 0.6
    d = diff_rubrics(rubric, changed)
    assert d.weight_deltas["correctness"] == -0.1

def test_lint_weight_warning():
    rubric = json.loads((ROOT / "examples/minimal_rubric.json").read_text()); rubric["criteria"][0]["weight"] = 2
    assert any(f.rule == "R_WEIGHT_TOTAL" for f in lint_rubric(rubric))

def test_adapter_round_trips_spec_shape():
    rubric = json.loads((ROOT / "examples/minimal_rubric.json").read_text())
    for adapter in [inspect_ai, promptfoo, deepeval, langsmith, evalkit]:
        native = adapter.from_spec(rubric)
        assert adapter.to_spec(native)["version"] == "auraone-rubric-v1"

def test_cli_validate():
    proc = subprocess.run([sys.executable, "-m", "rubric_spec.cli", "validate", str(ROOT / "examples/minimal_rubric.json")], text=True, capture_output=True)
    assert proc.returncode == 0, proc.stderr + proc.stdout
