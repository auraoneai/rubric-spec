# Rubric Spec v1 Conformance Tests

A framework can claim AuraOne Rubric Schema v1 compliance when it passes these cases:

1. Accepts a minimal valid binary rubric.
2. Accepts ordinal anchors in ascending order.
3. Accepts Likert anchors with five levels.
4. Accepts continuous anchors with numeric endpoints.
5. Rejects missing `version`.
6. Rejects an unsupported `scale_type`.
7. Rejects duplicate `criterion_id` values.
8. Warns when weights do not sum to 1.0.
9. Preserves top-level provenance during import/export.
10. Preserves criterion-level tie-break rules.
11. Preserves judge prompt contract output format.
12. Round-trips examples on criteria without dropping fields.
13. Converts framework-native binary grading to spec binary scale.
14. Converts spec ordinal criteria to framework-native weighted criteria.
15. Produces deterministic JSON serialization for the same rubric.
16. Emits path-aware validation errors.
17. Emits lint findings for vague, compound, or missing-example criteria.
18. Leaves synthetic data disclosure intact.
