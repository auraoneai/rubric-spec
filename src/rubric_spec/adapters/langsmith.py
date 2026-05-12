from __future__ import annotations
from copy import deepcopy
from typing import Any

FRAMEWORK = __name__.split(".")[-1]

def to_spec(native: dict[str, Any]) -> dict[str, Any]:
    if native.get("version") == "auraone-rubric-v1":
        spec = deepcopy(native)
        spec.pop("framework", None)
        return spec
    criteria = native.get("criteria") or native.get("checks") or native.get("graders") or native.get("feedback") or native.get("test_cases") or []
    spec_criteria = []
    for idx, item in enumerate(criteria):
        spec_criteria.append({
            "criterion_id": str(item.get("criterion_id", item.get("id", f"{FRAMEWORK}_{idx}"))),
            "label": str(item.get("label", item.get("name", item.get("criterion", f"Criterion {idx+1}")))),
            "description": str(item.get("description", item.get("prompt", item.get("criterion", "")))),
            "scale_type": item.get("scale_type", "binary"),
            "weight": float(item.get("weight", 1 / max(len(criteria), 1))),
            "tie_break_rule": item.get("tie_break_rule", "none"),
            "anchors": item.get("anchors", [{"value": 0, "label": "fail"}, {"value": 1, "label": "pass"}]),
            "examples": item.get("examples", []),
        })
    return {"version":"auraone-rubric-v1","rubric_id":str(native.get("rubric_id", native.get("id", FRAMEWORK + "-rubric"))),"label":native.get("label", FRAMEWORK + " rubric"),"tie_break_rule":native.get("tie_break_rule", "none"),"judge_prompt_contract":native.get("judge_prompt_contract", {"instruction":"Score each criterion.","output_format":"json","required_fields":["criterion_id","score"]}),"provenance":native.get("provenance", {"source":FRAMEWORK,"created_by":"adapter","created_at":"1970-01-01","synthetic":True}),"criteria":spec_criteria}

def from_spec(spec: dict[str, Any]) -> dict[str, Any]:
    native = deepcopy(spec)
    native["framework"] = FRAMEWORK
    return native
