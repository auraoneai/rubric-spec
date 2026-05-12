# AuraOne Rubric Schema v1

AuraOne Rubric Schema v1 is a portable JSON rubric format for deterministic and LLM-judged evaluations. A rubric contains stable criterion ids, labels, anchors, scale types, weights, tie-break rules, a judge prompt contract, version metadata, and provenance.

## Required Top-Level Fields

- `version`: exactly `auraone-rubric-v1`.
- `rubric_id`: stable identifier for the rubric.
- `criteria`: one or more scoring criteria.
- `judge_prompt_contract`: instructions and output expectations for judge implementations.
- `provenance`: source, author, creation date, and `synthetic` disclosure.

## Scale Examples

### Binary

A binary criterion has two anchors, usually `0` and `1`.

```json
{"criterion_id":"safety","label":"Safety","scale_type":"binary","weight":0.4,"anchors":[{"value":0,"label":"unsafe"},{"value":1,"label":"safe"}]}
```

### Ordinal

Ordinal criteria use ordered labels such as `1`, `2`, and `3` where distance is rank based.

### Likert

Likert criteria are ordinal scales with human-readable agreement anchors, usually 1-5 or 1-7.

### Continuous

Continuous criteria define minimum and maximum anchors and may include a threshold in `metadata`.

## Tie Breaking

Use `prefer_lower_risk` for safety or compliance rubrics, `prefer_higher_score` for quality rubrics, `manual_review` when automated resolution is inappropriate, and `none` when ties are accepted.

## Provenance And Synthetic Data

Examples in this repository are synthetic and mark `provenance.synthetic=true`. Do not embed real customer rubrics unless they are explicitly cleared for release.
