from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from .validate import load_rubric

@dataclass(frozen=True)
class RubricDiff:
    added: list[str]
    removed: list[str]
    changed: list[dict[str, Any]]
    weight_deltas: dict[str, float]
    anchor_changes: list[str]
    def to_dict(self) -> dict[str, Any]: return self.__dict__

def diff(rubric_a: str, rubric_b: str) -> RubricDiff:
    return diff_rubrics(load_rubric(rubric_a), load_rubric(rubric_b))

def diff_rubrics(a: dict[str, Any], b: dict[str, Any]) -> RubricDiff:
    left = {c["criterion_id"]: c for c in a.get("criteria", [])}
    right = {c["criterion_id"]: c for c in b.get("criteria", [])}
    added = sorted(set(right) - set(left)); removed = sorted(set(left) - set(right))
    changed = []; weight_deltas = {}; anchor_changes = []
    for cid in sorted(set(left) & set(right)):
        fields = {}
        for key in sorted(set(left[cid]) | set(right[cid])):
            if left[cid].get(key) != right[cid].get(key):
                fields[key] = {"old": left[cid].get(key), "new": right[cid].get(key)}
        if fields:
            changed.append({"criterion_id": cid, "fields": fields})
        if "weight" in fields:
            weight_deltas[cid] = round(float(right[cid].get("weight", 0)) - float(left[cid].get("weight", 0)), 12)
        if "anchors" in fields:
            anchor_changes.append(cid)
    return RubricDiff(added, removed, changed, weight_deltas, anchor_changes)
