# rubric-spec

Validate, lint, diff, and convert LLM evaluation rubrics with AuraOne Rubric Schema v1.

`rubric-spec` is for evaluation engineers and tool builders who need one inspectable rubric artifact across review and scoring systems. Its differentiator is a canonical JSON contract for criterion ids, anchors, weights, tie-break rules, judge prompt requirements, examples, and provenance. The adapters convert JSON shapes; they do not run or contact Inspect AI, PromptFoo, DeepEval, LangSmith, or EvalKit.

## Inspectable Output

| Command | Proof produced |
| --- | --- |
| `validate` | JSON with `ok`, path-aware errors, and warnings |
| `lint` | JSON findings for weight totals, vague wording, compound criteria, and missing examples |
| `diff` | JSON with added, removed, and changed criteria, weight deltas, and anchor changes |
| `convert` | Converted JSON on stdout after validating the canonical rubric |
| `conformance` | An 18-case JSON report covering schema rules and bundled adapter round trips |

## Runtime Boundary

All commands read local JSON or JSONL files and write to stdout. The package has no runtime dependencies, makes no network requests, and performs no model calls. Conversion support is limited to the bundled adapter representations; successful conversion is not a claim that an external framework can execute the result.

## Install

```bash
python -m pip install rubric-spec==0.1.2
```

For development from a clone:

```bash
python -m pip install -e .
```

## Quickstart

From a repository checkout with the bundled synthetic examples:

```bash
rubric-spec validate examples/minimal_rubric.json > validation.json
rubric-spec lint examples/minimal_rubric.json > lint-findings.json
rubric-spec diff examples/minimal_rubric.json examples/multi_criteria_rubric.json > rubric-diff.json
rubric-spec conformance examples/minimal_rubric.json > conformance.json
```

## Documentation

- Schema: [`spec/rubric-schema-v1.md`](spec/rubric-schema-v1.md)
- Conformance cases: [`spec/conformance-tests.md`](spec/conformance-tests.md)
- Synthetic examples: [`examples/`](examples/)

## Release Status

Registry status verified July 13, 2026: version `0.1.2` is published on PyPI and tagged `v0.1.2` in the public repository. The project is alpha software. No usage, adoption, or benchmark claim is made.

## Limits

This package does not orchestrate evaluation runs, certify downstream framework compatibility, or supply production rubrics. Bundled examples are synthetic.

## Next Action

Run `validate` and `lint` on the rubric you plan to ship, resolve every validation error, then run `conformance` before converting it for one supported target.
