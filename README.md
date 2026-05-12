# rubric-spec

`rubric-spec` is the reference implementation for AuraOne Rubric Schema v1, a portable rubric format that can move between Inspect AI, PromptFoo, DeepEval, LangSmith, and EvalKit without losing criterion ids, anchors, weights, judge prompt contracts, or provenance.

## Quickstart

```bash
python -m venv .venv
. .venv/bin/activate
pip install rubric-spec
rubric-spec validate examples/minimal_rubric.json
rubric-spec conformance
```

## Adapter Migration Guides

- Inspect AI: export scorer criteria as JSON, then run `rubric-spec convert --from inspect_ai --to rubric_spec inspect.json`.
- PromptFoo: map `assert`/grading configs into criteria; `from_spec` preserves weights and anchors.
- DeepEval: test case metrics become rubric criteria.
- LangSmith: feedback schema entries become criteria.
- EvalKit: JSONL rows round-trip into the canonical v1 object.

## FAQ

### Why a spec?

Rubrics are operational contracts. A named schema makes reviews portable, diffable, lintable, and conformance-testable.

### Why not OpenEval?

This package focuses on the human-judgment layer: anchors, tie-break rules, reviewer-facing examples, judge prompt contracts, and provenance. It can be used alongside broader eval orchestration standards.

### How is this different from OpenAI Evals YAML?

OpenAI Evals YAML configures a run. AuraOne Rubric Schema v1 defines the rubric artifact itself so it can be reused across runners.

## What This Is Not

This is not a leaderboard, a benchmark claim, or a source of real customer rubrics. All bundled examples are synthetic.

## Conformance

The conformance suite is defined in `spec/conformance-tests.md` and can be surfaced with `rubric-spec conformance`.
